import time
import rtmidi
import sys
import string
import threading

class NetMidi:
	"""Maps network fields to midi notes"""
	def __init__(self,portNum):
		# load the mapping file
		self.noteMap = {}
		self.threadLock = threading.Lock()
		try:
			f = open("mappings.config",'r')
		except (OSError, IOError) as e:
			sys.exit("Problem with mappings.config file")
	   	l = f.readlines()
		del l[0]
		for i in l:
			t = i.split(' ')
			t[-1] = t[-1].replace('\n','')
			self.noteMap[t[0]+t[1]] = t[2:]
		f.close()	
		# create the connection to the midi device	
		self.midiout = rtmidi.MidiOut()
		avail = self.midiout.get_ports()
		if len(avail) < portNum:
			sys.exit("Problem with IO port number given")
		else:
			self.midiout.open_port(portNum-1)
			self.__setProgs()

	def __setProgs(self):
		"""Sets the channels with the instrument specified in the config file"""
		for mapping in self.noteMap.values():
			chan = 191 + int(mapping[0])
			prog = int(mapping[1])
			self.midiout.send_message([chan,prog])

	def playNote(self,prot,port,eph,size):
		"""Processes packet info and creates a new thread for playback"""
		if (prot+str(port)) in self.noteMap.keys(): # check if the mapping exists
			mapping = self.noteMap[prot+str(port)]
		else:
			sys.exit("No mapping exists for "+prot+str(port))
		chan = int(mapping[0])
		note = ((eph * 80)/65535) + 20
		velo = (((size - 20) * 107) / 1480) + 20
		print(chan,note,velo)
		# create a new noteplayer thread and run it
		np = NotePlayer(chan,note,velo,self.midiout,self.threadLock)
		np.start()
	
class NotePlayer (threading.Thread):
	"""Plays a single note as a new thread, to allow mutliple notes at once"""
	def __init__(self,chan,note,velo,midOut,tl):
		threading.Thread.__init__(self)
		self.noteOnMes = [chan+143,note,velo]
		self.threadLock = tl
		self.noteOffMes = [chan+127,note,0]
		self.midiout = midOut
	
	def run(self):
		print("starting thread")
		self.threadLock.acquire()
		self.midiout.send_message(self.noteOnMes)
		self.threadLock.release()
		time.sleep(0.5)
		self.threadLock.acquire()
		self.midiout.send_message(self.noteOffMes)
		self.threadLock.release()
