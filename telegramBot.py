from typing import Final
from telegram.ext import ContextTypes, CommandHandler, Application, filters, MessageHandler
from telegram import Update
import os
import imageFunctions as proc


# Reading the API TOKEN from Token file
with open(os.getcwd() + '/Token', 'r') as token_file:
    TOKEN: Final = token_file.read()

# Global variables declaration
img = None
img_path = None
desired_img_format = None




async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
       Starts the chat session
       :param update: a reference to telegram Update
       :param context: a reference to the telegram conversation context
       :return: None
       """
    await update.message.reply_text("""
    
    Hello!, welcome to my bot.
    
    Please enter an image!  
    
    for more information please type /help
    
    """)




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
       Provides help to the chat user
       :param update: a reference to telegram Update
       :param context: a reference to the telegram conversation context
       :return: None
       """
    await update.message.reply_text("""
    
    
    Here are the bot possible commands:
        
    start - Start the bot
    help - Provides help for using the bot
    
    rescale - To rescale an image.
    for image rescaling you need to provide a scale 
    factor that grater than 0.
    values between 0 to 1 ar recommended.
    
    send_back - Sends the result image back
    
    compress - Compress the current image.
    compression values are constants. 
    to get max compression, desired image format 
    is recommended to be 'jpeg'
    
    brightness - adjust the image brightness by factor value.
    factor value need to be grater than 0.
    values above 1 will brighten the image and values
    below 1 will darken the image.
    
    
    """)




async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    handles an errors that can happen during chat time (package errors)
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    print(f'Update {update} caused error {context.error}')




async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Downloads an image file from the chatbot conversation
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    # First, try to receive an image file
    try:
        file_id = update.message.photo[-1].file_id

    except Exception as i:
        await update.message.reply_text("Unable to read file, please provide an image file")
        print("An error occurred during file receiving:", str(i))
        return

    # Download the image file to the main directory
    file = await context.bot.get_file(file_id)
    global img, img_path
    img = str(await file.download_to_drive())
    img = os.getcwd() + '/' + img
    img_path = img

    # Handle possible image file errors
    possible_error = proc.error_handler(img)
    if possible_error is None:
        await update.message.reply_text("file saved successfully!\nPlease enter image desired format:")
    else:
        await update.message.reply_text(possible_error)
        return

    # Reading the image
    img = proc.read_image(img)




async def get_image_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Gets and update the user desired returned photo format
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    # Catching the user text
    global desired_img_format
    des_format = update.message.text

    # Checking that the desired format is supported
    if not is_supported_format(des_format):
        await update.message.reply_text("desired format can be: png, jpeg, jpg, tiff")
        return

    # Updating the desired format
    desired_img_format = des_format
    update_image_path(img_path)

    # Replaying with an info message
    await update.message.reply_text("The desired format is: " + desired_img_format)




async def rescale_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Rescales the user image to the scale input provided
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """

    global img, img_path

    # Checking the image has been uploaded
    if img is None:
        await update.message.reply_text("Image needs to be uploaded first")
        return

    # Checks a desired format was inserted
    if check_format_was_inserted() is False:
        await update.message.reply_text("Desired format needs to be inserted first")
        return

    # Getting the scale input argument (type str)
    scale = context.args[0] if len(context.args) > 0 else None

    # Checking that the scale is legit
    if scale is None:
        await update.message.reply_text("You must insert an image desired scale value")
        return

    if not is_number(scale):
        await update.message.reply_text("Image desired scale value must be a number grater than 0")
        return

    scale = float(scale)

    # Rescaling the image and updating the image path
    img = proc.rescale_frame(img, scale)
    update_image_path(img_path)

    await update.message.reply_text("Image was rescaled successfully!")




async def send_doc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sending back the current image
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    chat_id = update.message.chat_id

    # Checks if an image file was uploaded
    if img_path is None:
        await update.message.reply_text("No image was inserted")
        return

    # Checks a desired format was inserted
    if check_format_was_inserted() is False:
        await update.message.reply_text("Desired format needs to be inserted first")
        return

    # Send back the file
    await context.bot.send_document(chat_id, img_path)




async def compress_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Compressing current image
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    # Checking the image has been uploaded
    if img is None:
        await update.message.reply_text("Image needs to be uploaded first")
        return

    # Compress image
    try:
        proc.compress_image(img, img_path)

    except Exception as i:
        await update.message.reply_text("Unable to compress file")
        print("An error occurred during file receiving:", str(i))
        return

    await update.message.reply_text("Image Compressed successfully!")




async def adjust_brightness_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Adjusting image brightness according to the inserted factor
    :param update: a reference to telegram Update
    :param context: a reference to the telegram conversation context
    :return: None
    """
    global img, img_path

    # Checks image was uploaded
    if img is None:
        await update.message.reply_text("Image needs to be uploaded first")
        return

    # Receiving the brightness factor argument
    brightness_factor = context.args[0] if len(context.args) > 0 else None

    # Checkin an argument was inserted
    if brightness_factor is None:
        await update.message.reply_text("You must insert an image brightness factor")
        return

    # Checks the argument is legitimate
    if not is_number(brightness_factor):
        await update.message.reply_text("Image brightness factor must be a number grater than 0")
        return

    brightness_factor = float(brightness_factor)

    # Adjust the brightness
    try:
        img = proc.adjust_brightness(img, brightness_factor)
        update_image_path(img_path)

    except Exception as i:
        await update.message.reply_text("Unable to adjust brightness")
        print("An error occurred during file receiving:", str(i))
        return

    await update.message.reply_text("Brightness adjusted successfully")




def is_number(string) -> bool:
    """
    Checks if the argument is a number grater than 0
    :param string: string representing the number
    :return: boolean True/False
    """
    # Split the string by the decimal point
    parts = string.split('.')

    # If there are two parts and both parts are digits, it's an incomplete number
    if len(parts) == 2 and parts[0].isnumeric() and parts[1].isdigit():
        return True
    if len(parts) == 1 and parts[0].isnumeric() and string != '0':
        return True

    return False




def is_supported_format(des_format: str) -> bool:
    """
    Checking if the string argument is a supported format
    :param des_format: str representative of a format
    :return: boolean True/False
    """
    return des_format in ['jpg', 'jpeg', 'png', 'tiff']




def update_image_path(path) -> None:
    """
    Updating an image path
    :param path: path to update to
    :return: None
    """
    global img_path
    path = path.split('.')[0] + '.' + desired_img_format
    img_path = path
    proc.write_image(img, path)




def check_format_was_inserted() -> bool:
    """
    Checks that desired format was inserted
    :return: boolean True/False
    """
    global desired_img_format
    return desired_img_format is not None




def run_bot() -> None:
    """
    Main function that runs the bot.
    Called from program's main function
    :return: None
    """

    print('Starting Bot')
    app = Application.builder().token(TOKEN).build()

    # Add the commands and messages handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('rescale', rescale_command))
    app.add_handler(CommandHandler('send_back', send_doc_command))
    app.add_handler(CommandHandler('compress', compress_image_command))
    app.add_handler(CommandHandler('brightness', adjust_brightness_command))
    app.add_handler(MessageHandler(filters.ATTACHMENT, download_command))
    app.add_handler(MessageHandler(filters.TEXT, get_image_format))

    # Add an error handler
    app.add_error_handler(error)

    print('Polling..')
    app.run_polling(poll_interval=3)



