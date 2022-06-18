from netifaces import AF_INET, gateways

def get_gateway(iface):
    gws = gateways()
    for gw in gws:
        gw_iface = gws[gw][AF_INET]
        if gw_iface:
            gateway_ip, gateway_iface = gw_iface[0], gw_iface[1]
            if gateway_iface == iface:
                return gateway_ip
    return None