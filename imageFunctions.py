import cv2 as cv
import os




def error_handler(path: str) -> str:
    """
    Handles basic probable errors
    :param path: image file path
    :return: str error message or None if no errors were found
    """
    path_name, path_extension = os.path.splitext(path)
    path_extension = path_extension[1:]
    path_extension.lower()

    if not os.path.isfile(path):
        return "Image file not found."

    if not os.access(path, os.R_OK):
        return "Unable to read the image file."

    # Check if the path format is supported by OpenCV
    if path_extension not in ['jpg', 'jpeg', 'png', 'tiff']:
        return "Invalid format! Please provide 'jpg', 'jpeg', tiff or 'png'."

    return None




def convert_img(image_path, format='png'):
    """
    Converts the image to the desired format
    :param image_path:
    :param format:
    :return:
    """
    try:
        # Read the image
        image = cv.imread(image_path) if type(image_path) is str else image_path

        # Getting the file extension
        extension = os.path.splitext(image_path)[1]
        extension = extension[1:]

        # Extract the file extension from the desired format
        desired_format = format.lower()

        # Checks if the file is already in the desired format
        if extension.lower() == desired_format:
            print("The image is already in the desired format.")
            return None

        # Check if the path format is supported by OpenCV
        if desired_format not in ['jpg', 'jpeg', 'png', 'tiff']:
            return "Invalid desired format!, only 'jpg', 'jpeg', tiff or 'png' are supported."

        # Create the new file name with the desired format
        new_file_name = image_path.split('.')[0] + '.' + desired_format

        # Convert and save the image with the desired format
        cv.imwrite(new_file_name, image)

        print("Image converted successfully")
        return None

    # Handles openCV image conversion error
    except Exception as e:
        print("An error occurred during image conversion:", str(e))




def rescale_frame(frame, scale=0.75):
    """
    Rescales an image to the desired scale
    :param frame: the image to scale
    :param scale: the desired scale (0.75 will be the default scale)
    :return: rescaled image, otherwise exception will be raised
    """
    try:
        # Basic scaling errors
        if scale <= 0:
            raise Exception("Scale value Must be grater than 0")

        image = cv.imread(frame) if type(frame) is str else frame

        # Defines the interpolation that will suit best (based on openCV documentation)
        cur_interpolation = cv.INTER_AREA if scale < 1 else cv.INTER_LINEAR

        # Adjusting the Desired scale dimensions
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        dimensions = (width, height)

        # Rescaling the image
        ret = cv.resize(image, dimensions, interpolation=cur_interpolation)
        print("Image was resized successfully!")
        return ret

    # Handles openCV image conversion error
    except Exception as e:
        print("An error occurred during image rescaling:", str(e))




def write_image(image, desired_path) -> None:
    """
    Writes an image to the desired path
    :param image: image to be written
    :param desired_path: path to write to
    :return: None upon success
    """
    # Write the image only if it has been read first
    if type(image) is not str:
        cv.imwrite(desired_path, image)




def compress_image(image, desired_path) -> None:
    """
    Compresses image
    :param image: image to compress
    :param desired_path: path to write the image to
    :return: None upon success (otherwise raises exception)
    """

    # Checks if the image was read
    if type(image) is str:
        raise Exception("Image needs to be read first")

    # Gets the image format
    image_format = desired_path.split('.')[1]

    compression_list = []

    # Assigns compression_list with the right cv compression flag
    if image_format == 'png':
        compression_list = [int(cv.IMWRITE_PNG_COMPRESSION), 9]
    elif image_format == 'jpg' or image_format == 'jpeg':
        compression_list = [int(cv.IMWRITE_JPEG_QUALITY), 50]
    elif image_format == 'tiff':
        compression_list = [int(cv.IMWRITE_TIFF_COMPRESSION), 8]
    elif len(compression_list) == 0:
        raise Exception("Image format is not supported")

    # writing the image
    cv.imwrite(desired_path, image, compression_list)
    return None


def adjust_brightness(image, factor):
    """
    Adjust the image brightness (bright/dark)
    :param image: image to work on
    :param factor: brightness factor, above 1 will brighten, between 0 and 1 will darken
    :return: result image
    """
    # Gets the image info
    x_pix, y_pix, num_channels = image.shape
    # Max saturation variable to avoid over saturation.
    saturation_limit = 255

    # Iterate over the image info and apply the bright factor
    for x in range(x_pix):
        for y in range(y_pix):
            for c in range(num_channels):
                # Apply the bright factor
                channel_result = image[x, y, c] * factor
                image[x, y, c] = channel_result if channel_result <= saturation_limit else saturation_limit

    return image


def read_image(image):
    """
    Read image
    :param image: image to read
    :return: read image
    """

    # Read image only if it has not been read
    return cv.imread(image) if type(image) is str else image



