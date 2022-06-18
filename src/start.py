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
    global stop_app
    if config.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s', stream=sys.stdout)

    if config.log_file:
        fileHandler = logging.FileHandler(config.log_file)
        fileHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logging.getLogger().addHandler(fileHandler)

    services = [
        ARPService(config),
        DNSService(config),
        HTTPService(config),
        ForwarderService(config)
    ]

    stop_app = False
    def stop(signal, frame):
        global stop_app
        stop_app = True

    for service in services:
        reactor.callInThread(service.start)

    signal.signal(signal.SIGINT, stop)

    def stopThread():
        global stop_app
        while not stop_app:
            sleep(0.1)
        logging.warning("Stopping")
        reactor.stop()
        for service in services:
            service.stop()
        sleep(0.5)
        logging.warning("Exiting")
        os._exit(0)

    reactor.callInThread(stopThread)
    reactor.run()