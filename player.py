from ctypes import windll, c_buffer
import os
import msvcrt
import time
import sys
import subprocess

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

mci = MCI()                
queue = Queue()
current_song = 0
current_album = ""

def playMP3(name, mci):
    mci.direct_send("Close All")
    mci.direct_send("Open \"%s\" Type MPEGVideo Alias mus" % name)
    #mciSend("Play mus Wait")
    mci.direct_send("Play mus")
   
def closeSong(mci):
    mci.direct_send("Close All")
    
def pauseSong(mci):
    mci.direct_send("Pause mus")
    
def resumeSong(mci):
    mci.direct_send("Resume mus")
    
def seekSong(pos, mci):
    err_length, buf_length = mci.direct_send("status mus length")
    if pos > buf_length:
        pos = buf_length - 5
    mci.direct_send("seek mus to %s" % pos)
    mci.direct_send("play mus")

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
    
def find_largest_in_common(others, start_string):
    rest = min(others, key=len)
    largest_length = len(rest)
    build = start_string
    pos = 0

    while len(build) < largest_length:
        good = True
        for item in others:
            pos = len(build)
            if rest[pos] != item[pos]:
                good = False
        if good:
            build += rest[pos]
        else:
            break

    return build
    
def tab_complete(start_string, show):
    list = os.listdir(os.getcwd())
    count = 0 
    rest = ""
    others = []
    for item in list:
        if item.startswith(start_string):
            others.append(item)
            if count == 0:
                rest = item
            count += 1
    if count > 1:
        if show:
            rest = ", ".join(others)
        else:
            rest = find_largest_in_common(others, start_string)
            #rest = min(others, key=len)
    return count, rest

def poll_wait(prompt, mci, queue):
    done = False
    msg = ""
    sys.stdout.write(prompt+"\n")
    global current_album
    global current_song
    current_album = os.getcwd()[os.getcwd().rindex("\\") + 1:]
    #async looping, waiting for input and doing stuff! 
    while 1:
        if msvcrt.kbhit():
            input = msvcrt.getche()
            
            if input == "\b" and msg:
                msg = msg[:-1]
                sys.stdout.write('\r'+msg +" " + "\b")
            elif input == "\t":
                split = msg.split()
                to_complete = ' '.join(split[1:])
                the_rest = split[0]
                if last_input == "\t":
                    num, to_print = tab_complete(to_complete, True)
                    msg = to_print
                else:
                    num, to_print = tab_complete(to_complete, False)
                    msg = the_rest + " " + to_print
                
                #if num == 1:
                #    msg = the_rest + " " + to_print
                #elif num > 1:
                #    msg = to_print
                sys.stdout.write('\r' + msg)
            elif input != "\r":
                msg += input
                sys.stdout.write('\r'+msg)
            else:
                print "\n"
                return msg

            last_input = input
                
        err_length, buf_length = mci.direct_send("status mus length")
        err_position, buf_position = mci.direct_send("status mus position")
        try:
            position = int(buf_position)
            total_time = int(buf_length)
            if position >= total_time:
                closeSong(mci)
                if queue.queue:
                    playMP3(queue.pop(), mci)
                else:
                    listdir = os.listdir(os.getcwd())
                    this_album = os.getcwd()[os.getcwd().rindex("\\") + 1:]
                    if current_album == this_album:
                        if current_song >= len(listdir) - 1:
                           current_song = 0
                        else:
                            current_song = current_song + 1

                    else:
                        current_song = 0
                        listdir = os.listdir(os.getcwd())
                        current_album = this_album

                    if current_song in range(len(listdir)):
                        f = get_filename(listdir[current_song])
                        if f is not None:
                            print "\nPlaying ... %s\n" % f
                            playMP3(f, mci)
                            sys.stdout.write(prompt)
            time.sleep(0.09)    
        except ValueError, e:
            e        
            
def main():
    global queue
    global mci
    global current_song
    os.chdir(r'C:\Users\Andrew\Music\iTunes\Music')
    while True:
        cmd = poll_wait("%s $ " % os.getcwd(), mci, queue)
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
                        current_song = int(opt[0])
                        playMP3(os.path.join(os.getcwd(), f), mci)
        except ValueError, e:
            pass      

        #commands 
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
            if opt[1] == "all" or opt[1] == "a":
                for song in listdir:
                    f = get_filename(song)
                    if f is not None:
                        queue.push(f)
            else:
                try:
                    if (int(opt[1])) in range(len(listdir)):
                        f = get_filename(listdir[int(opt[1])])
                        if f is not None:
                            queue.push(f)
                        else:
                            print "Not a valid selection to queue"
                except ValueError, e:
                    print "Not a valid selection to queue"
            
        elif opt[0] == "show" or opt[0] == "s":
            print queue.queue
            
        elif opt[0] == "skip" or opt[0] == "k":
            closeSong(mci)
            if queue.queue:
                playMP3(queue.pop(), mci)
                
        elif opt[0] == "clear" or opt[0] == "cl":
            queue.queue = []

        elif opt[0] == "try":
            trySong(" ".join(opt[1:]), mci)

        elif opt[0] == "seek" or opt[0] == "sk":
            try:
                pos = int(opt[1])
                seekSong(pos, mci)
            except ValueError, e:
                pass
        try:
            pass
        except KeyboardInterrupt:
            sys.exit(0)
            
if __name__ == "__main__":
    main()