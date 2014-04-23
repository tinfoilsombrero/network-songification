import time
import rtmidi
import sys
import string
import thread

class NetMidi:
	"""Maps network fields to midi notes"""
	def __init__(self,portNum):
		# load the mapping file
		self.noteMap = {}
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
#		self.__setProgs()

	def __setProgs(self):
		"""Sets the channels with the instrument specified in the config file"""
		for mapping in self.noteMap.values():
			chan = 191 + int(mapping[0])
			prog = int(mapping[1])
			self.midiout.send_message([chan,prog])

	def playNote(self,prot,port,eph,size):
		"""Plays a note on the midi channel specified by given info"""
		if (prot+str(port)) in self.noteMap.keys(): # check if the mapping exists
			mapping = self.noteMap[prot+str(port)]
		else:
			sys.exit("No mapping exists for "+prot+str(port))
		chan = int(mapping[0])
		note = ((eph * 127)/65535) + 1
		velo = (((size - 20) * 127) / 1480) + 1
		print(chan,note,velo)
		self.midiout.send_message([chan+143,note,velo])
		time.sleep(0.5)
		self.midiout.send_message([chan+127,note,0])

test = NetMidi(2)
test.playNote("TCP",80,15000,1480)
del test
