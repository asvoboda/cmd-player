from ctypes import windll, c_buffer


class MCI():
    ##internals
    def __init__(self):
        self.wmci = windll.winmm.mciSendStringA
        self.wmerror = windll.winmm.mciGetErrorStringA

    def direct_send(self, commands):
        buffer = c_buffer(255)
        error_code = self.wmci(commands, buffer, 254, 0)
        if error_code:
            return error_code, self.get_error(error_code)
        else:
            return error_code, buffer.value

    def get_error(self, error):
        error = int(error)
        buffer = c_buffer(255)
        self.wmerror(error, buffer, 254)
        return buffer.value

    ##externals	
    def play_song(self, name):
        self.direct_send("Close All")
        self.direct_send("Open \"%s\" Type MPEGVideo Alias mus" % name)
        self.direct_send("Play mus")

    def close_song(self):
        self.direct_send("Close All")

    def pause_song(self):
        self.direct_send("Pause mus")

    def resume_song(self):
        self.direct_send("Resume mus")

    def seek_song(self, pos):
        err_length, buf_length = self.direct_send("status mus length")
        if pos > buf_length:
            pos = buf_length - 5
        self.direct_send("seek mus to %s" % pos)
        self.direct_send("play mus")

    def try_song(self, s):
        print(self.direct_send(s))

    def length(self):
        return self.direct_send("status mus length")

    def position(self):
        return self.direct_send("status mus position")