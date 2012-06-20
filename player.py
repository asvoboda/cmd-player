from ctypes import *
import os
import sys

winmm = windll.winmm

def mciSend(s):
    i=winmm.mciSendStringA(s,0,0,0)
    if i<>0:
        print "Error %d in mciSendString %s" % ( i, s )

def playMP3(mp3Name):
    mciSend("Close All")
    mciSend("Open \"%s\" Type MPEGVideo Alias theMP3" % mp3Name)
    mciSend("Play theMP3 Wait")
    mciSend("Close theMP3")
   
def main():
    while True:
        listdir = os.listdir(os.getcwd())
        print os.getcwd()
        for (i, name) in zip(range(len(listdir)), listdir):
            print "[%s] %s" % (i, name)
        cmd = raw_input("--> ")
        opt = cmd.split(" ")
        try:
            if int(opt[0]) in range(len(listdir)):
                f = listdir[int(opt[0])]
                if os.path.isdir(f):
                    os.chdir(f)
                elif os.path.isfile(f):
                    print "Playing ... %s" % f
                    playMP3(os.path.join(os.getcwd(), f))
                else:
                    print "%s is not a valid thing" % f
        except ValueError, e:
            pass
            
        if opt[0] == "up":
            os.chdir("..")
        elif opt[0] == "cd":
            newpath = " ".join(opt[1:])
            if "My " in newpath:
                newpath.replace("My ", "")
            if os.path.isdir(" ".join(opt[1:])):
                os.chdir(" ".join(opt[1:]))
            else:
                print "%s is not a valid directory" % " ".join(opt[1:])
            
if __name__ == "__main__":
    main()