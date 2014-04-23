#!/usr/bin/env python

# import python libraries that we use
from optparse import OptionParser
from scapy.all import *

# get params from command line
parser = OptionParser()
parser.add_option("-i", "--interface", dest="interface", help="interface to listen on", default="eth0")
parser.add_option("-p", "--pcap", dest="pcap", help="Use PCAP file instead of network interface. Pass path to PCAP file.", default=False)
# if you use -h this will print out a help description

options, remainder = parser.parse_args() # store options in variable

# start sniffing
if options.pcap == False:
	sniff(prn=callback, store=0, iface=options.interface) # listen to interface
else:
	sniff(prn=callback, store=0, offline=options.pcap) # read pcap file

# everytime scapy sees a packet this func will be called
def callback(pkt):
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
		func(proto, port, eph_port, size) # this is where midi stuff will get called
	elif pkt.haslayer(ICMP):
		print pkt.show() # if you see an icmp packet print to screen
		# logic for icmp will come later

def func(prot,port,eph,size):
	# placeholder function
	a = 1