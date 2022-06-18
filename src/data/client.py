from scapy.all import getmacbyip, get_if_list, get_if_addr, get_if_hwaddr

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

        if mac == None or mac == 'ff:ff:ff:ff:ff:ff':
            # Check to see if the IP is one of the local interfaces
            for iface in get_if_list():
                if get_if_addr(iface) == ip:
                    return Client(ip, get_if_hwaddr(iface))
            return None

        return Client(ip, mac)