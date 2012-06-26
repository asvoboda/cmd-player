from ctypes import windll, c_buffer
import os
import threading
import msvcrt
import time
import sys

class Queue():
    def __init__(self):
        self.queue = []
    def push(self, x):
        self.queue.append(x)
    def pop(self):
        try:
            tmp = self.queue[0]
            self.queue.remove(tmp)
            return tmp
        except IndexError, e:
            print e
        return None
        
class MCI:
    def __init__(self):
        self.w32mci = windll.winmm.mciSendStringA
        self.w32mcierror = windll.winmm.mciGetErrorStringA

    def send(self, commands):
        buffer = c_buffer(255)
        error_code = self.w32mci(str(commands),buffer,254,0)
        if error_code:
            return error_code, self.get_error(error_code)
        else:
            return error_code, buffer.value

    def get_error(self, error):
        error = int(error)
        buffer = c_buffer(255)
        self.w32mcierror(error,buffer,254)
        return buffer.value

    def direct_send(self, txt):
        (err,buf) = self.send(txt)
        #if err != 0:
            #print 'Error', str(err), 'on', txt, ':', buf
        return err, buf        
        
class Poller(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, queue, mci):
        super(Poller, self).__init__()
        self._stop = threading.Event()
        self.queue = queue
        self.mci = mci

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()      

    def run(self):
        while True:
            err_length, buf_length = self.mci.direct_send("status mus length")
            err_position, buf_position = self.mci.direct_send("status mus position")
            try:
                position = int(buf_position) / 1000.0 # into seconds
                total_time = int(buf_length) / 1000.0
                percent = (position / total_time) * 100
                if buf_position < buf_length:
                    self.progress(40, percent)
            except ValueError, e:
                e
            time.sleep(3)       
            
    def progress(self, width, percent):
        marks = math.floor(width * (percent / 100.0))
        spaces = math.floor(width - marks)
     
        loader = '[' + ('=' * int(marks)) + (' ' * int(spaces)) + ']'
     
        sys.stdout.write("%s %d%%\r" % (loader, percent))
        if percent >= 100:
            sys.stdout.write("\n")
        sys.stdout.flush()                    
                

mci = MCI()                
queue = Queue()

def playMP3(name, mci):
    mci.direct_send("Close All")
    mci.direct_send("Open \"%s\" Type MPEGVideo Alias mus" % name)
    #mciSend("Play mus Wait")
    mci.direct_send("Play mus")
    
def playWav(name, mci):
    mci.direct_send("Close All")
    mci.direct_send("Open \"%s\" Type waveaudio Alias mus" % name)
    #mciSend("Play mus Wait")
    mci.direct_send("Play mus")
   
def closeSong(mci):
    mci.direct_send("Close All")
    
def pauseSong(mci):
    mci.direct_send("Pause mus")
    
def resumeSong(mci):
    mci.direct_send("Resume mus")

def trySong(s, mci):
    print mci.direct_send(s)
    
def get_filename(f):
    name = None
    if os.path.isfile(f):
        if f.endswith("mp3") or f.endswith("MP3") or f.endswith("WAV") or f.endswith("wav") or f.endswith("M4A") or f.endswith("m4a"):
            name = os.path.join(os.getcwd(), f)
        else:
            print "Not a valid media type"
    else:
        print "%s is not a valid thing" % f
    return name
    
def get_input(prompt):
    done = False
    msg = ""
    sys.stdout.write(prompt)
    while 1:
        if msvcrt.kbhit():
            input = msvcrt.getche()
            if input != "\r":
                msg += input
            else:
                print "\n"
                return msg
            
def main():
    global queue
    global mci
    
    os.chdir(r'C:\Users\Andrew\Music\iTunes\Music')
    poll_queue = Poller(queue, mci)
    poll_queue.start()
    while True:
        #cmd = raw_input("%s $ " % os.getcwd())
        cmd = get_input("%s $ " % os.getcwd())
        opt = cmd.split(" ")
        listdir = os.listdir(os.getcwd())
        try:
            if (int(opt[0])) in range(len(listdir)):
                if os.path.isdir(listdir[int(opt[0])]):
                    os.chdir(listdir[int(opt[0])])            
                else:
                    f = get_filename(listdir[int(opt[0])])
                    if f is not None:
                        print "\nPlaying ... %s\n" % f
                        playMP3(os.path.join(os.getcwd(), f), mci)
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
                
        elif opt[0] == "close" or opt[0] == "c":
            closeSong(mci)
        elif opt[0] == "exit" or opt[0] == "e":
            poll_queue.stop()
            closeSong(mci)
            sys.exit(0)
        elif opt[0] == "ls" or opt[0] == "l":
            for (i, name) in zip(range(len(listdir)), listdir):
                print '[%s] %s' % (i, name)   
        elif opt[0] == "pause" or opt[0] == "p":
            pauseSong(mci)
        elif opt[0] == "resume" or opt[0] == "r":    
            resumeSong(mci)
        elif opt[0] == "queue" or opt[0] == "q":
            # queue up the song!
            try:
                (int(opt[1])) in range(len(listdir))
                f = get_filename(listdir[int(opt[1])])
                if f is not None:
                    queue.push(f)
                else:
                    print "Not a valid selection to queue"
            except IndexError, e:
                print "Not a valid selection to queue"
            
        elif opt[0] == "show" or opt[0] == "s":
            print queue.queue
        elif opt[0] == "try":
            trySong(" ".join(opt[1:]), mci)            
            
        try:
            pass
        except KeyboardInterrupt:
            poll_queue.stop()
            sys.exit(0)
            
if __name__ == "__main__":
    main()