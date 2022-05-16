from django.contrib import messages

supported_image_formats = ['png', 'jpg', 'jpeg']
supported_video_formats = ['mp4', 'webm', 'ogg']

def throwError(request, message, num_errors=0):
    messages.info(request, message)
    return num_errors + 1

def getFileFormat(file):
    return str.lower(str(file).split('.')[-1])

def checkImageFile(image):
    format = getFileFormat(image)

    if format in supported_image_formats:
        return format

    return None

def checkVideoFile(video):
    format = getFileFormat(video)

    if format in supported_video_formats:
        return format

    return None