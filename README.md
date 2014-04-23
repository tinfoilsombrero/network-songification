consists of three parts: mappings.config, netmidi.py and sniff.py

mappings.config is used to specify which ports+protocols should be mapped to which midi instruments. Standard MIDI allows for 16 different voices, exceeding this has will depend on your specific MIDI setup. The format is [TCP|UDP|ICMP] [Port #] [Channel # 1-16] [MIDI Program for this channel]
eg. TCP 80 1 3
will cause http packets to play a note on the Electric Piano program assigned to channel 1.

netmidi.py contains classes used to translate packet fields to MIDI messages. The important one is the NetMidi class, which takes in the midi port to create an object that can be passed packet info to play MIDI notes. The MIDI port refers to the listening MIDI device or software that will handle the MIDI message. MIDI ports can be listed with the aplaymidi utility (aplaymidi -l)
eg. myNetMidi = NetMidi(2)
will connect to the second available MIDI port.

Using the NetMidi.playNote() function, packet parameters can be passed to produce MIDI messages:
eg. myNetMidi.playNote("TCP",80,16003,1480)
where the parameters passed are ["TCP"|"UDP"|"ICMP"] [Port #] [Ephemeral Port #] [Packet Size in Bytes (max 1480)]
