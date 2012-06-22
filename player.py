from ctypes import windll
import os
import sys

winmm = windll.winmm

def mciSend(s):
    i,o = windll.winmm.mciSendStringA(s,0,0,0)
    if i<>0:
        print "Error %d in mciSendString %s" % ( i, s )
    print str(o)

def playMP3(mp3Name):
    mciSend("Close All")
    mciSend("Open \"%s\" Type MPEGVideo Alias theMP3" % mp3Name)
    #mciSend("Play theMP3 Wait")
    mciSend("Play theMP3")
   
def closeMP3():
    mciSend("Close All")
    
def pauseMP3():
    mciSend("Pause theMP3")
    
def resumeMP3():
    mciSend("Resume theMP3")
   
def main():
    os.chdir(r'C:\Users\Andrew\Music')
    while True:
        listdir = os.listdir(os.getcwd())
        cmd = raw_input("%s $ " % os.getcwd())
        opt = cmd.split(" ")
        try:
            if (int(opt[0])) in range(len(listdir)):
                f = listdir[int(opt[0])]
                if os.path.isdir(f):
                    os.chdir(f)
                elif os.path.isfile(f):
                    if f.endswith("mp3") or f.endswith("MP3"):
                        print "\nPlaying ... %s\n" % f
                        playMP3(os.path.join(os.getcwd(), f))
                    else:
                        print "Not an .mp3 file"
                else:
                    print "%s is not a valid thing" % f
        except ValueError, e:
            pass      
            
        if opt[0] == "cd":
            newpath = " ".join(opt[1:])
            if "My " in newpath:
                newpath.replace("My ", "")
            if os.path.isdir(" ".join(opt[1:])):
                os.chdir(" ".join(opt[1:]))
            else:
                print "%s is not a valid directory" % " ".join(opt[1:])  
                
        elif opt[0] == "stop" or opt[0] == "s":
            closeMP3()
        elif opt[0] == "exit" or opt[0] == "e":
            sys.exit(0)
        elif opt[0] == "ls":
            for (i, name) in zip(range(len(listdir)), listdir):
                print '[%s] %s' % (i, name)   
        elif opt[0] == "pause" or opt[0] == "p":
            pauseMP3()
        elif opt[0] == "resume" or opt[0] == "r":    
            resumeMP3()
            
if __name__ == "__main__":
    main()