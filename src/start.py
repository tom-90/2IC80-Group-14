from __future__ import print_function
import logging
import os
import signal
import sys
from time import sleep
from twisted.internet import reactor

from services.arp import ARPService
from services.dns import DNSService
from services.forwarder import ForwarderService
from services.http import HTTPService


def start(config):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', stream=sys.stdout)

    services = [
        ARPService(config),
        DNSService(config),
        HTTPService(config),
        ForwarderService(config)
    ]

    def stop(signal, frame):
        print("Stopping")
        reactor.stop()
        for service in services:
            service.stop()
        sleep(0.5)
        print("Exiting")
        os._exit(0)

    for service in services:
        reactor.callInThread(service.start)

    signal.signal(signal.SIGINT, stop)
    reactor.run()