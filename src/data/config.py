from scapy.layers.l2 import getmacbyip
from client import Client

class Config:
    attacker = Client(None, None)
    victim = Client(None, None)
    gateway = Client(None, None)

    arp_sleep_time = 5
    """
    Interval (in seconds) in which to send arp spoof messages
    """

    iface = None
    """
    Interface to use for network messages
    """

    http_listen_port = 10594
    """
    Port that the SSL-stripping HTTP proxy will listen on
    """