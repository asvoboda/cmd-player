import os
import time
import pprint
import cmd
import threading
from sys import exit
from queue import Queue
from subprocess import call

from env import get_environment
from mutagen.easyid3 import EasyID3

from utils import get_filename


"""Windows doesn't have a readline package :("""
try:
    import readline
except ImportError:
    import pyreadline as readline

if os.name == "nt":
    from winplayer import MusicPlayer
else:
    raise Exception("Not supported on this operation system at the moment")


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class PlayerShell(cmd.Cmd):
    intro = 'Dumb Python Music Player. Type "help" or "?"" to list commands.\n'
    prompt = '> '
    token = prompt

    # Internals
    player = MusicPlayer()
    playlist = Queue()
    pp = pprint.PrettyPrinter(indent=4)
    running = True
    types = Enum(["PLAY", "PAUSE", "CLOSE", "RESUME"])
    messages = Queue()
    environment = get_environment()
    current = None

    def preloop(self):
        self.chdir(self.environment['music_home'])
        consumer = threading.Thread(target=self.consumer_player)
        consumer.daemon = True
        consumer.start()

    def do_exit(self, arg):
        """Stop playing, and exit."""
        self.messages.put(self.types.CLOSE)
        self.running = False
        return True

    def do_cd(self, arg):
        """Change directory to the argument specified"""

        # windows hack
        if os.name == "nt":
            if "My " in arg:
                arg.replace("My ", "")
        if os.path.isdir(arg):
            self.chdir(arg)
        else:
            print("%s is not a valid directory." % arg)

    def complete_cd(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_ls(self, arg):
        """List and print the current directory"""
        call("ls")

    # playlist options
    # TODO: can we group these better?
    def do_add(self, arg):
        """Adds a song to the playlist specified as the argument to this command"""
        f = get_filename(arg)
        if f:
            self.playlist.put(f)
        else:
            print("Not a valid selection to add to the playlist.")

    def complete_add(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_addall(self, arg):
        """Adds all songs in the current directory to the playlist, not recursively"""
        for song in self.list():
            f = get_filename(song)
            if f:
                self.playlist.put(f)

    def do_clear(self, arg):
        """Clears the entire playlist"""
        self.playlist = Queue()

    def do_show(self, arg):
        """Prints out the current song, if one is playing"""
        if self.current is not None:
            audio = EasyID3(self.current)
            print("%s - %s" % (audio['title'][0], audio['album'][0]))
        else:
            print("There is no song currently playing.")
        
    def do_showall(self, arg):
        """Prints out the entire playlist"""
        for queued in self.playlist.queue:
            audio = EasyID3(queued)
            print("%s - %s" % (audio['title'][0], audio['album'][0]))

    # song options
    # TODO: logicall group together?
    def do_play(self, arg):
        """Play the song specified in the argument to this command"""
        f = get_filename(arg)
        if f:
            song = os.path.join(os.getcwd(), f)
            self.playlist.put(song)
            self.messages.put(self.types.PLAY)

    def complete_play(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_resume(self, arg):
        """Resume a paused song"""
        self.messages.put(self.types.RESUME)

    def do_pause(self, arg):
        """Pause a currently playing song"""
        self.messages.put(self.types.PAUSE)

    def do_skip(self, arg):
        """Stop the current song and play the next one in the playlist if it exists"""
        # By simply closing, our background thread will start the next song if there is one
        self.messages.put(self.types.CLOSE)


    def do_stop(self, arg):
        """Stop playing the current song and clear playlist"""
        self.messages.put(self.types.CLOSE)
        self.playlist = Queue()

    # helper methods
    def list(self):
        return os.listdir(".")

    def cwd(self):
        return os.getcwd()

    def chdir(self, dir):
        os.chdir(dir)
        self.prompt = self.cwd() + '\n' + self.token

    def complete_helper(self, text, line, begidx, endidx):
        current_directory = self.list()
        if text:
            mline = line.partition(' ')[2]
            offs = len(mline) - len(text)
            # mline = mline.encode("utf8")
            return [
                    s[offs:] for s in current_directory 
                    if s.startswith(mline)
                ]
        else:
            return current_directory

    def consumer_player(self):
        while self.running:
            # interrupt to modify the current song somehow
            if not self.messages.empty():
                _cmd = self.messages.get()

                if _cmd == self.types.PLAY:
                    if not self.playlist.empty():
                        song = self.playlist.get()
                        self.player.play_song(song)
                        self.current = song
                elif _cmd == self.types.CLOSE:
                    self.player.close_song()
                    self.current = None
                elif _cmd == self.types.PAUSE:
                    self.player.pause_song()
                elif _cmd == self.types.RESUME:
                    self.player.resume_song()

            err_length, buf_length = self.player.length()
            err_position, buf_position = self.player.position()
            # we might be finished playing the current song
            try:
                position = int(buf_position)
                total_time = int(buf_length)
                if position >= total_time:
                    self.player.close_song()
                    if not self.playlist.empty():
                        song = self.playlist.get()
                        self.player.play_song(song)
                        self.current = song
            except ValueError:
                if not self.playlist.empty():
                    song = self.playlist.get()
                    self.player.play_song(song)
                    self.current = song

            time.sleep(1)


def main():
    PlayerShell().cmdloop()


if __name__ == "__main__":
    exit(main())
