from ctypes import windll, c_buffer
import os
import msvcrt
import time
import sys
import pprint

class Queue():
	def __init__(self):
		self.queue = []
	def enqueue(self, x):
		self.queue.append(x)
	def dequeue(self):
		try:
			tmp = self.queue[0]
			self.queue.remove(tmp)
			return tmp
		except IndexError, e:
			print e
		return None
	def isEmpty(self):
		return len(self.queue) == 0
	def clear(self):
		self.queue = []
	def show(self):
		return self.queue
		
class MCI:
	##internals
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
		return err, buf       
	##externals	
	def playMP3(self, name):
		self.direct_send("Close All")
		self.direct_send("Open \"%s\" Type MPEGVideo Alias mus" % name)
		self.direct_send("Play mus")
	def closeSong(self):
		self.direct_send("Close All")
	def pauseSong(self):
		self.direct_send("Pause mus")	
	def resumeSong(self):
		self.direct_send("Resume mus")
	def seekSong(self, pos):
		err_length, buf_length = self.direct_send("status mus length")
		if pos > buf_length:
			pos = buf_length - 5
		self.direct_send("seek mus to %s" % pos)
		self.direct_send("play mus")
	def trySong(self, s):
		print self.direct_send(s)	

def get_filename(f):
	name = None
	exts = ("mp3", "wav", "m4a", "MP3", "WAV", "M4A")
	if os.path.isfile(f):
		if f.endswith(exts):
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
		
def format_columns(mylist, cols):
	col_width = max(len(word) for word in mylist) + 2  # padding
	template = ""
	for i in range(cols):
		template += "{%s:%s}" % (i, col_width)

	data = []
	for i in range(0, len(mylist), cols):
		data.append(mylist[i:i+cols])

	for row in data:
		try:
			print template.format(*row)
		except IndexError:
			#last row might be too small for the template
			for k in range(cols - 1, 0, -1):
				try:
					new_template = ""
					for i in range(k):
						new_template += "{%s:%s}" % (i, col_width)
					print new_template.format(*row)
					break
				except IndexError:
					continue
		
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
	return count, rest
	
def handle_whitespace_chars(msg, input, last_input):
	if input == "\b" and msg:
		msg = msg[:-1]
		sys.stdout.write("\r" + msg + " " + "\b")
	elif input == "\t":
		split = msg.split()
		to_complete = " ".join(split[1:])
		the_rest = split[0]
		if last_input == "\t":
			num, to_print = tab_complete(to_complete, True)
			msg = to_print
		else:
			num, to_print = tab_complete(to_complete, False)
			msg = the_rest + " " + to_print
		sys.stdout.write("\r" + msg)
	elif input != "\r":
		msg += input
		sys.stdout.write("\r" + msg)
	else:
		print "\n"
		return msg, True
	return msg, False
		
def get_input(prompt, mci, queue):
	msg = ""
	sys.stdout.write(prompt+"\n")
	last_input = ""
	#async looping, waiting for input and doing stuff! 
	while 1:
		if msvcrt.kbhit():
			input = msvcrt.getche()
			msg, should_return = handle_whitespace_chars(msg, input, last_input)
			last_input = input
			if should_return:
				return msg
			
				
		err_length, buf_length = mci.direct_send("status mus length")
		err_position, buf_position = mci.direct_send("status mus position")
		try:
			position = int(buf_position)
			total_time = int(buf_length)
			if position >= total_time:
				mci.closeSong()
				if not queue.isEmpty():
					song = queue.dequeue()
					print "\nPlaying ... %s\n" % song
					mci.playMP3(song)
			time.sleep(0.09)    
		except ValueError, e:
			if not queue.isEmpty():
					song = queue.dequeue()
					print "\nPlaying ... %s\n" % song
					mci.playMP3(song)

def process_input(opt, listdir, mci, queue, pprint):
		#commands 
		if not opt[0]:
			return 0

		if opt[0] == "cd":
			newpath = " ".join(opt[1:])
			if "My " in newpath:
				newpath.replace("My ", "")
			if os.path.isdir(" ".join(opt[1:])):
				os.chdir(" ".join(opt[1:]))
			else:
				print "%s is not a valid directory" % " ".join(opt[1:])  
				
		elif opt[0] == "ls" or opt[0] == "l":
			num_cols = 2
			format_columns(listdir, num_cols)
			
		elif opt[0] == "play" or opt[0] == "p":
			f = get_filename(' '.join(opt[1:]))
			if f:
				print "\nPlaying ... %s\n" % f
				mci.playMP3(os.path.join(os.getcwd(), f))
				
		elif opt[0] == "exit":
			mci.closeSong()
			sys.exit(0)
			
		## song operations
		elif opt[0] == "song" or opt[0] == "s":
			if not opt[1]:
				return false
				
			if opt[1] == "resume" or opt[1] == "r":
				mci.resumeSong()
							
			elif opt[1] == "pause" or opt[1] == "p":
				mci.pauseSong()
				
			elif opt[1] == "skip" or opt[1] == "k":
				mci.closeSong()
				if not queue.isEmpty():
					song = queue.dequeue()
					print "\nPlaying ... %s\n" % song
					mci.playMP3(song)
					
			elif opt[1] == "stop" or opt[1] == "s":
				mci.closeSong()
				queue.clear()
				
		#queue operations
		elif opt[0] == "queue" or opt[0] == "q":
			if not opt[1]:
				return false
				
			if opt[1] == "all" or opt[1] == "a":
				for song in listdir:
					f = get_filename(song)
					if f:
						queue.enqueue(f)

			elif opt[1] == "clear" or opt[1] == "c":
				queue.clear()

			elif opt[1] == "show" or opt[1] == "s":
				pprint.pprint(queue.show())

			else:
				f = get_filename(" ".join(opt[1:]))
				if f:
					queue.enqueue(f)
				else:
					print "Not a valid selection to queue"
				
		## debuging options
		elif opt[0] == "try":
			mci.trySong(" ".join(opt[1:]))

		elif opt[0] == "seek":
			try:
				pos = int(opt[1])
				mci.seekSong(pos)
			except ValueError, e:
				pass
            
def main():
	mci = MCI()
	queue = Queue()
	pp = pprint.PrettyPrinter(indent=4)
	#TODO: try to grab this dynamically?
	os.chdir(r'C:\Users\Andrew\Music\iTunes\Music')
	while True:
		cmd = get_input("%s $ " % os.getcwd(), mci, queue)
		opt = cmd.split(" ")
		listdir = os.listdir(os.getcwd()) 
		process_input(opt, listdir, mci, queue, pp)

		try:
			pass #TODO: handle keyboard interrupt better
		except KeyboardInterrupt:
			sys.exit(0)
	
if __name__ == "__main__":
	main()