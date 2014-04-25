#!/usr/bin/env python

# import python libraries that we use
from optparse import OptionParser
from scapy.all import *
from netmidi import NetMidi
from tokenbucket import TokenBucket

# get params from command line
parser = OptionParser()
parser.add_option("-i", "--interface", dest="interface", help="interface to listen on", default="eth0")
parser.add_option("-p", "--pcap", dest="pcap", help="Use PCAP file instead of network interface. Pass path to PCAP file.", default=False)
parser.add_option("-m", "--midiport",dest="mport", help="The midi port number to output to", default=1)
# if you use -h this will print out a help description

options, remainder = parser.parse_args() # store options in variable
# create the NetMidi object for output
myNetMidi = NetMidi(int(options.mport))

#initialze leaky bucket algo
bucket = TokenBucket(10, 0.2)

# everytime scapy sees a packet this func will be called
def callback(pkt):
	if bucket.consume(1):
		if IP in pkt:
			if pkt.haslayer(TCP) or pkt.haslayer(UDP): # tcp and udp are only ones that will have port numbers
				size = pkt[IP].len
				if TCP in pkt:
					proto = "TCP"
					port = min([pkt[TCP].sport,pkt[TCP].dport])
					eph_port = max([pkt[TCP].sport,pkt[TCP].dport])
				elif UDP in pkt:
					proto = "UDP"
					port = min([pkt[UDP].sport,pkt[UDP].dport])
					eph_port = max([pkt[UDP].sport,pkt[UDP].dport])
				myNetMidi.playNote(proto, port, eph_port, size)
			elif pkt.haslayer(ICMP):
				# ICMP packets are special
				size = 1480
				port = pkt[ICMP].type
				eph_port = (pkt[ICMP].type + 1) * 15
				myNetMidi.playNote("ICMP", port, eph_port, size)

# start sniffing
if options.pcap == False:
        sniff(prn=callback, filter="tcp or udp or icmp", store=0, iface=options.interface) # listen to interface
else:
        sniff(prn=callback, filter="tcp or udp or icmp", store=0, offline=options.pcap) # read pcap file


