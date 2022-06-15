from twisted.internet import reactor
from twisted.web import http
from service import Service

from sslstrip.StrippingProxy import StrippingProxy
from sslstrip.URLMonitor import URLMonitor
from sslstrip.CookieCleaner import CookieCleaner

class HTTPService(Service):
    def start(self):
        URLMonitor.getInstance().setFaviconSpoofing(True)
        CookieCleaner.getInstance().setEnabled(True)

        strippingFactory          = http.HTTPFactory(timeout=10)
        strippingFactory.protocol = StrippingProxy

        reactor.listenTCP(self.config.http_listen_port, strippingFactory)
        print("Listening for TCP")