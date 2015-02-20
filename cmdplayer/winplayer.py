from ctypes import windll, c_buffer

from cmdplayer.abstractplayer import AbstractMusicPlayer

class _MCI(object):
    ##internals
    def __init__(self):
        self.wmci = windll.winmm.mciSendStringA
        self.wmerror = windll.winmm.mciGetErrorStringA

    def direct_send(self, command):
        buffer = c_buffer(255)
        error_code = self.wmci(command.encode(), buffer, 254, 0)
        if error_code:
            return error_code, self.get_error(error_code)
        else:
            return error_code, buffer.value

    def get_error(self, error):
        error = int(error)
        buffer = c_buffer(255)
        self.wmerror(error, buffer, 254)
        return buffer.value


class MusicPlayer(AbstractMusicPlayer):
    def __init__(self):
        self._mci = _MCI()

    ##externals	
    def play_song(self, name):
        self._mci.direct_send("Close All")
        self._mci.direct_send("Open \"%s\" Type MPEGVideo Alias mus" % name)
        self._mci.direct_send("Play mus")

    def close_song(self):
        self._mci.direct_send("Close All")

    def pause_song(self):
        self._mci.direct_send("Pause mus")

    def resume_song(self):
        self._mci.direct_send("Resume mus")

    def seek_song(self, pos):
        err_length, buf_length = self._mci.direct_send("status mus length")
        if pos > buf_length:
            pos = buf_length - 5
        self._mci.direct_send("seek mus to %s" % pos)
        self._mci.direct_send("play mus")

    def length(self):
        return self._mci.direct_send("status mus length")

    def position(self):
        return self._mci.direct_send("status mus position")