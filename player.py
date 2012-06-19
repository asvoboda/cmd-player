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
    name = raw_input("file to play")
    playMP3(name)
   
if __name__ == "__main__":
    main()