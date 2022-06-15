from __future__ import unicode_literals
from prompt_toolkit.eventloop import run_in_executor
from prompt_toolkit.shortcuts import dialogs
from prompt_toolkit.widgets import Dialog, Label
from scapy.all import ARP, Ether, srp
from client import Client

from utils import stu, uts

class NetworkScan:
    def __init__(self, iface, cidr):
        self.iface = iface
        self.cidr = cidr

    def _scan(self):
        # create ARP packet
        arp = ARP(pdst=self.cidr)
        # create the Ether broadcast packet
        # ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        # stack them
        packet = ether/arp

        result = srp(
            packet,
            timeout=3,
            iface=self.iface,
            verbose=False
        )[0]

        # a list of clients, we will fill this in the upcoming loop
        clients = []

        for sent, received in result:
            # for each response, append ip and mac address to `clients` list
            clients.append(Client(received.psrc, received.hwsrc))

        return clients

    def execute(self):
        app = dialogs._create_app(
            Dialog(
                title="Scanning network...",
                body=Label(text="Scanning network for available devices...", dont_extend_height=True),
                with_background=True,
            ),
            None
        )

        def start():
            try:
                self.clients = self._scan()
            finally:
                app.exit()

        run_in_executor(start)

        app.run()

        return self.clients