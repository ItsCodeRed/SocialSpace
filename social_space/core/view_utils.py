from django.contrib import messages

supported_image_formats = ['png', 'jpg', 'jpeg']
supported_video_formats = ['mp4', 'webm', 'ogg']

def throwError(request, message, num_errors=0):
    messages.info(request, message)
    return num_errors + 1

def getFileFormat(file):
    return str.lower(str(file).split('.')[-1])

def checkImageFile(image):
    if image == None:
        return None

    format = getFileFormat(image)

    if format in supported_image_formats:
        return format

    return None

def checkVideoFile(video):
    if video == None:
        return None

    format = getFileFormat(video)

    if format in supported_video_formats:
        return format

    return None

def parseVideoId(link):
    last_portion = str(link).split('/')[-1]

    if '=' in last_portion:
        return last_portion.split('=')[-1]

    return last_portion

def splitFeed(feed, n):
    for x in range(0, len(feed), n):
        every_chunk = feed[x: n+x]

        yield every_chunk