from data.client import Client

class Config:
    attacker = Client(None, None)
    victim = Client(None, None)
    gateway = Client(None, None)

    arp_sleep_time = 1
    """
    Interval (in seconds) in which to send arp spoof messages
    """

    iface = None
    """
    Interface to use for network messages
    """

    http_listen_port = 80
    """
    Port that the SSL-stripping HTTP proxy will listen on
    """

    dns_listen_port = 10595
    """
    Port that the DNS spoofing server will listen on
    """

    hostnames = [ "*" ]

    verbose = False
    """
    Log verbosely
    """

    log_file = None
    """
    File to save logs to
    """