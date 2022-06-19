import logging
from twisted.internet import reactor
from twisted.web import http
from services.service import Service

from sslstrip.sslstrip.StrippingProxy import StrippingProxy
from sslstrip.sslstrip.URLMonitor import URLMonitor
from sslstrip.sslstrip.CookieCleaner import CookieCleaner

class HTTPService(Service):
    def start(self):
        if self.config.http_listen_port:
            URLMonitor.getInstance().setFaviconSpoofing(False)
            CookieCleaner.getInstance().setEnabled(False)

            strippingFactory          = http.HTTPFactory(timeout=10)
            strippingFactory.protocol = StrippingProxy

            reactor.listenTCP(self.config.http_listen_port, strippingFactory)
            logging.warning("[HTTP] Listening for TCP")