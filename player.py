import os
import time
import sys
import pprint
import cmd
import threading
import Queue as qu

from MCI import MCI
from subprocess import call
from utils import get_filename
from env import get_environment

#Windows doesn't have a readline package :(
try:
    import readline
except ImportError:
    import pyreadline as readline


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

class PlayerShell(cmd.Cmd):
    intro = 'Dumb Python Player. Type "help" or "?"" to list commands.\n'
    prompt = '> '
    token = '> '

    def preloop(self):
        self.mci = MCI()
        self.playlist = qu.Queue()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.running = True
        self.types = Enum(["PLAY", "PAUSE", "CLOSE", "RESUME"])
        self.messages = qu.Queue()
        environment = get_environment()
        self.chdir(environment['music_home'])

        consumer = threading.Thread(target=self.player)
        consumer.daemon = True

        consumer.start()


    def do_exit(self, arg):
        'Stop playing, and exit.'

        self.messages.put(self.types.CLOSE)

        self.running = False
        return True

    def do_cd(self, arg):
        'Change directory to the argument specified'
        #windows hack
        if "My " in arg:
            arg.replace("My ", "")
        if os.path.isdir(arg):
            self.chdir(arg)
        else:
            print("%s is not a valid directory" % arg)

    def complete_cd(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_ls(self, arg):
        'List and print the current directory'
        call("ls")

    #playlist options
    #TODO: can we group these better?
    def do_add(self, arg):
        'Adds a song to the playlist specified as the argument to this command'
        f = get_filename(arg)
        if f:
            self.playlist.put(f)
        else:
            print("Not a valid selection to add to the playlist")

    def complete_add(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_addall(self, arg):
        'Adds all songs in the current directory to the playlist, not recursively'
        for song in self.list():
            f = get_filename(song)
            if f:
                self.playlist.put(f)

    def do_clear(self, arg):
        'Clears the entire playlist'
        self.playlist = qu.Queue()

    def do_show(self, arg):
        'Prints out the entire playlist'
        self.pp.pprint(self.playlist.queue)

    #song options
    #TODO: logicall group together?
    def do_play(self, arg):
        'Play the song specified in the argument to this command'
        f = get_filename(arg)
        if f:
            song = os.path.join(os.getcwd(), f)
            #self.play(song)
            self.playlist.put(song)
            self.messages.put(self.types.PLAY)

    def complete_play(self, text, line, begidx, endidx):
        return self.complete_helper(text, line, begidx, endidx)

    def do_resume(self, arg):
        'Resume a paused song'
        #self.mci.resume_song()
        self.messages.put(self.types.RESUME)

    def do_pause(self, arg):
        'Pause a currently playing song'
        #self.mci.pause_song()
        self.messages.put(self.types.PAUSE)

    def do_skip(self, arg):
        'Stop the current song and play the next one in the playlist if it exists'
        #By simply closing, our backround thread will start the next song if there is one
        self.messages.put(self.types.CLOSE)


    def do_stop(self, arg):
        'Stop playing the current song and clear playlist'
        #self.mci.close_song()
        self.messages.put(self.types.CLOSE)
        self.playlist = qu.Queue()

    #helper methods
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
            mline = mline.encode("utf8")
            return [
                    s[offs:] for s in current_directory 
                    if s.startswith(mline)
                ]
        else:
            return current_directory

    def player(self):
        while self.running:
            if not self.messages.empty():
                cmd = self.messages.get()

                if cmd == self.types.PLAY:
                    if not self.playlist.empty():
                        song = self.playlist.get()
                        self.mci.play_song(song)

                elif cmd == self.types.CLOSE:
                    self.mci.close_song()

                elif cmd == self.types.PAUSE:
                    self.mci.pause_song()

                elif cmd == self.types.RESUME:
                    self.mci.resume_song()


            err_length, buf_length = self.mci.length()
            err_position, buf_position = self.mci.position()
            try:
                position = int(buf_position)
                total_time = int(buf_length)
                if position >= total_time:
                    self.mci.close_song()
                    #self.messages.put(self.types.CLOSE)
                    if not self.playlist.empty():
                        song = self.playlist.get()
                        #print("\nPlaying ... %s\n" % song)
                        self.mci.play_song(song)
                        #self.messages.put(self.types.PLAY)
            except ValueError:
                if not self.playlist.empty():
                    song = self.playlist.get()
                    #print("\nPlaying ... %s\n" % song)
                    self.mci.play_song(song)
                    #self.messages.put(self.types.PLAY)

            time.sleep(1)

if __name__ == "__main__":
    PlayerShell().cmdloop()
