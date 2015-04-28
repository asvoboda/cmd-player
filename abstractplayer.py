from abc import ABCMeta, abstractmethod


class AbstractMusicPlayer(object):
    """Abstract class that defines the API for a Music Player"""
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def play_song(self, name):
        pass

    @abstractmethod
    def close_song(self):
        pass

    @abstractmethod
    def pause_song(self):
        pass

    @abstractmethod
    def resume_song(self):
        pass

    @abstractmethod
    def seek_song(self, pos):
        pass

    @abstractmethod     
    def length(self):
        pass

    @abstractmethod
    def position(self):
        pass
