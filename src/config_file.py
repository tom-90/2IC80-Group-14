import argparse
import yaml

from sys import exit
from data.config import Config
from data.client import Client
from scapy.all import get_if_list, get_if_addr, get_if_hwaddr
from utils.gateway import get_gateway

parser = argparse.ArgumentParser(description='Perform ARP spoof, DNS spoof and log HTTP requests')
parser.add_argument('-c', '--config', default=None,
                    help='yaml config file (default: prompt for options)')
parser.add_argument('-l', '--log-file', default=None,
                    help='file where logs should be saved')
parser.add_argument('-d', '--disable-http-forward', action='store_true',
                    help='disable the forwarding of HTTP traffic to HTTPS (this allows you to run your own webserver to serve the user a different spoofed website)')
parser.add_argument('-v', '--verbose', dest='verbose', help='Enable verbose logging', action='store_true')

args = parser.parse_args()

def get_client(data, name):
    if not name in data['clients'] or not 'ip' in data['clients'][name]:
        print("Configuration does not contain a valid client for: " + name)
        exit(1)

    if 'mac' in data['clients'][name]:
        return Client(data['clients']['ip'], data['clients']['mac'])
    else:
        client = Client.fromIP(data['clients'][name]['ip'])
        if not client:
            print("Could not retrieve MAC address for client '" + name + "' with IP: " + data['clients'][name]['ip'])
            exit(1)
        return client


def get_config():
    if args.config == None:
        return None

    with open(args.config, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print("Failed to load configuration file:")
            print(e)
            exit(1)

    config = Config()
    
    if ( not 'interface' in data ) or ( not data['interface'] in get_if_list() ):
        print("Configuration file does not contain a valid interface.")
        exit(1)

    config.iface = data['interface']

    if not 'clients' in data:
        print("Configuration does not contain a valid client configuration.")
        exit(1)

    if not 'attacker' in data['clients']:
        config.attacker = Client(get_if_addr(config.iface), get_if_hwaddr(config.iface))
    else:
        config.attacker = get_client(data, 'attacker')

    if not 'gateway' in data['clients']:
        config.gateway = Client.fromIP(get_gateway(config.iface))
    else:
        config.gateway = get_client(data, 'gateway')

    config.victim = get_client(data, 'victim')

    if 'arp_sleep_time' in data:
        config.arp_sleep_time = data['arp_sleep_time']
    if 'http_listen_port' in data:
        config.http_listen_port = data['http_listen_port']
    if 'dns_listen_port' in data:
        config.dns_listen_port = data['dns_listen_port']
    if 'hostnames' in data:
        config.hostnames = data['hostnames']

    return config
