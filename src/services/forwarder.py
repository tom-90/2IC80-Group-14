import logging
from os import system
from services.service import Service

class ForwarderService(Service):
    def start(self):
        logging.warning("[INIT] Configuring IPTables Firewall rules...")
        system("echo \"1\" > /proc/sys/net/ipv4/ip_forward")
        system("iptables -t nat -A PREROUTING -p udp --destination-port 53 -j REDIRECT --to-port " + str(self.config.dns_listen_port))
        
    def stop(self):
        logging.warning("[INIT] Restoring IPTables Firewall rules...")
        system("iptables -t nat -D PREROUTING -p udp --destination-port 53 -j REDIRECT --to-port " + str(self.config.dns_listen_port))
