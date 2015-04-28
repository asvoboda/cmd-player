import os


def get_filename(f):
    name = None
    extensions = ("mp3", "wav", "m4a", "MP3", "WAV", "M4A")
    if os.path.isfile(f):
        if f.endswith(extensions):
            name = os.path.join(os.getcwd(), f)
        else:
            print("Not a valid media type")
    else:
        print("%s is not a valid thing" % f)
    return name