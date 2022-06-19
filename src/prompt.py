from __future__ import unicode_literals
from scapy.all import get_if_list, get_if_addr, get_if_hwaddr, conf
from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog
from netifaces import ifaddresses, AF_INET
from ipaddress import ip_network

from utils.gateway import get_gateway
from utils.dialogs import input_dialog
from utils.network_scan import NetworkScan
from data.config import Config
from data.client import Client
from sys import exit

def prompt():
    config = Config()

    # Show GUI, where the user can select the interface they want to use (e.g. enp0s3)
    iface = radiolist_dialog(
        title="Interface",
        text="Select the interface to use",
        # The values that can be chosen from, are all interfaces (v) in the interface list. 
        # values = identifier, text. 
        values=[
            (v, v) for v in get_if_list()
        ]
    ).run()

    # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
    if iface == None:
        exit()

    # Retrieve network address information for the interface, including the subnet mask
    addresses = ifaddresses(iface)[AF_INET]
    network = None

    # If the program cannot find any ip addresses, the user will be asked to give the program an IP range. 
    if len(addresses) == 0:
        cidr = input_dialog(
            title='Address Range',
            text='Could not automatically determine IP range to use. Please enter an IP range in CIDR notation manually.'
        ).run()
        
        # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
        if cidr == None:
            exit()

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
        ).run()

        exit()

    # Show all the victims the user can choose between
    victim = radiolist_dialog(
        title='Select network device',
        text='Please select a victim:',
        # values = identifier, text. 
        values=[
            (c, c.getMAC() + ' - ' + c.getIP()) for c in clients
        ]
    ).run()

    # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
    if victim == None:
        exit()

    # Select hostnames to spoof
    hostNames = input_dialog(
        title="Select hostnames",
        text="Please enter the hostnames to spoof, comma-seperated.\nWildcards are supported: enter *.tue.nl to match any subdomain of tue.nl (not including tue.nl itself).\nUse **.tue.nl to match any multi-level subdomain of tue.nl.\nEnter * for any domain."
    ).run()

    # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
    if hostNames == None:
        exit()

    # Parse the hostnames input
    if hostNames == "":
        hostNames = ["*"]
    else:
        hostNames = hostNames.split(",")

    # The time the attack will be repeated in seconds
    repeatAttackTime = input_dialog(
        title='Repeat Time',
        text='Enter a time in seconds, for which the program will resend every time a new ARP attack.',
        default=str(config.arp_sleep_time)
    ).run()

    # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
    if repeatAttackTime == None:
        exit()
        
    while (not repeatAttackTime.isdigit()):
        # The time the attack will be repeated in seconds
        repeatAttackTime = input_dialog(
            title='Repeat Time',
            text='You entered a non-digit number. \n\n' +
                'Enter a time in seconds, for which the program will resend every time a new ARP attack.',
            default=repeatAttackTime
        ).run()

        # If the user selects cancel, the GUI will be exited and the program will be stop executing. 
        if repeatAttackTime == None:
            exit()

    gateway = get_gateway(iface)
    if not gateway:
        print("Could not determine gateway for interface")
        exit(1)

    config.iface = iface
    config.victim = victim
    config.attacker = Client(get_if_addr(iface), get_if_hwaddr(iface))
    config.gateway = Client.fromIP(gateway)
    config.arp_sleep_time = float(repeatAttackTime)
    config.hostnames = hostNames

    return config