import os
import time
import sys
import pprint
import Queue as qu

from MCI import MCI
from subprocess import call
from utils import handle_whitespace_chars, get_filename
from env import get_environment
from KBHit import KBHit


HELP_TEXT = """
Dumb Python Player
==================
`cd [dir]` to change directories
`ls` to list directories
`play [song]` to play the specified song

Playlist Operations
`playlist all` adds all songs in the current directory to your playlist
`playlist show` prints the songs in your playlist
`playlist clear` clears the playlist
`playlist [song]` adds the specified song to your playlist

Song Operations
`song pause` to pause the current song
`song resume` resumes a paused song
`song skip` to skip to the next song in the playlist
`song stop` stops execution and clears the playlist

`exit` to exit
"""

playlist = qu.Queue()

def get_input(prompt, mci, kb):
    msg = ""
    sys.stdout.write(prompt + "\n")
    last_input = ""
    global playlist
    #async looping, waiting for input and doing stuff!
    while 1:
        if kb.kbhit():
            c = kb.getch()
            msg, should_return = handle_whitespace_chars(msg, c, last_input)
            last_input = c
            if should_return:
                return msg

        err_length, buf_length = mci.length()
        err_position, buf_position = mci.position()
        try:
            position = int(buf_position)
            total_time = int(buf_length)
            if position >= total_time:
                mci.close_song()
                if not playlist.empty():
                    song = playlist.get()
                    print("\nPlaying ... %s\n" % song)
                    mci.play_song(song)
            time.sleep(0.09)
        except ValueError:
            if not playlist.empty():
                song = playlist.get()
                print("\nPlaying ... %s\n" % song)
                mci.play_song(song)


def process_input(opt, listdir, mci, pprint):
    #commands
    if not opt[0]:
        return 0

    global playlist

    if opt[0] == "cd":
        newpath = " ".join(opt[1:])
        if "My " in newpath:
            newpath.replace("My ", "")
        if os.path.isdir(" ".join(opt[1:])):
            os.chdir(" ".join(opt[1:]))
        else:
            print("%s is not a valid directory" % " ".join(opt[1:]))

    elif opt[0] == "help" or opt[0] == "h":
        print(HELP_TEXT)

    elif opt[0] == "ls" or opt[0] == "l":
        ret = call("ls")

    elif opt[0] == "play":
        f = get_filename(' '.join(opt[1:]))
        if f:
            print("\nPlaying ... %s\n" % f)
            mci.play_song(os.path.join(os.getcwd(), f))

    elif opt[0] == "exit":
        mci.close_song()
        sys.exit(0)

    ## song operations
    elif opt[0] == "song" or opt[0] == "s":
        if not opt[1]:
            return False

        if opt[1] == "resume" or opt[1] == "r":
            mci.resume_song()

        elif opt[1] == "pause" or opt[1] == "p":
            mci.pause_song()

        elif opt[1] == "skip" or opt[1] == "k":
            mci.close_song()
            if not playlist.empty():
                song = playlist.get()
                print("\nPlaying ... %s\n" % song)
                mci.play_song(song)

        elif opt[1] == "stop" or opt[1] == "s":
            mci.close_song()
            playlist = qu.Queue()

    #playlist operations
    elif opt[0] == "playlist" or opt[0] == "p":
        if not opt[1]:
            return False

        if opt[1] == "all" or opt[1] == "a":
            for song in listdir:
                f = get_filename(song)
                if f:
                    playlist.put(f)

        elif opt[1] == "clear" or opt[1] == "c":
            playlist = qu.Queue()

        elif opt[1] == "show" or opt[1] == "s":
            pprint.pprint(playlist.queue)

        else:
            f = get_filename(" ".join(opt[1:]))
            if f:
                playlist.put(f)
            else:
                print("Not a valid selection to playlist")

    ## debuging options
    elif opt[0] == "try":
        mci.try_song(" ".join(opt[1:]))

    elif opt[0] == "seek":
        try:
            pos = int(opt[1])
            mci.seek_song(pos)
        except ValueError:
            pass


def main():
    kb = KBHit()
    mci = MCI()
    
    pp = pprint.PrettyPrinter(indent=4)
    environment = get_environment()
    os.chdir(environment['music_home'])

    while 1:
        cmd = get_input("%s $ " % os.getcwd(), mci, kb)
        opt = cmd.split(" ")
        listdir = os.listdir(os.getcwd())
        try:
            process_input(opt, listdir, mci, pp)
        except IndexError:
            print("Invalid option")

        try:
            pass #TODO: handle keyboard interrupt better?
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
