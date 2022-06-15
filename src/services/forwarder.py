from os import system
from service import Service

class ForwarderService(Service):
    def start(self):
        print("Configuring IPTables Firewall rules...")
        system("echo \"1\" > /proc/sys/net/ipv4/ip_forward")
        system("iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port " + str(self.config.http_listen_port))
        
    def stop(self):
        print("Restoring IPTables Firewall rules...")
        system("echo \"0\" > /proc/sys/net/ipv4/ip_forward")
        system("iptables -t nat -D PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port " + str(self.config.http_listen_port))
