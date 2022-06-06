from scapy.layers.l2 import getmacbyip

class Client:
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac

    def getIP(self):
        return self.ip

    def getMAC(self):
        return self.mac

    @staticmethod
    def fromIP(ip):
        mac = getmacbyip(ip)

        if mac == None:
            return None

        return Client(ip, mac)