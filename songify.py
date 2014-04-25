#!/usr/bin/env python

# import python libraries that we use
from optparse import OptionParser
from scapy.all import *
from netmidi import NetMidi
from time import time

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
	if bucket.tokens > 0:
		bucket.consume(1)
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


# leaky bucket algorithm taken from http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/
class TokenBucket(object):
    """An implementation of the token bucket algorithm.
    
    >>> bucket = TokenBucket(80, 0.5)
    >>> print bucket.consume(10)
    True
    >>> print bucket.consume(90)
    False
    """
    def __init__(self, tokens, fill_rate):
        """tokens is the total tokens in the bucket. fill_rate is the
        rate in tokens/second that the bucket will be refilled."""
        self.capacity = float(tokens)
        self._tokens = float(tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def consume(self, tokens):
        """Consume tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.tokens:
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        if self._tokens < self.capacity:
            now = time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens
    tokens = property(get_tokens)