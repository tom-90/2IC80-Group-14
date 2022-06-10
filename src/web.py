from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import httplib

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def forward(self):
        print(self.headers['Host'])
        print(self.path)
        conn = httplib.HTTPSConnection(self.headers['Host'])
        conn.request('GET', self.path, None, self.headers.dict)
        response = conn.getresponse()
        data = response.read()
        headers = response.getheaders()
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s %d %s\r\n" % (self.protocol_version, response.status, response.reason))
        for (header, value) in headers:
            self.send_header(header, value.replace('https://', 'http://'))
        self.end_headers()
        self.wfile.write(data.replace('https://', 'http://'))

    def do_GET(self):
        self.forward()
    def do_HEAD(self):
        self.forward()
    def do_POST(self):
        self.forward()
    def do_PUT(self):
        self.forward()
    def do_DELETE(self):
        self.forward()
    def do_OPTIONS(self):
        self.forward()
    def do_PATCH(self):
        self.forward()

class HTTPServer(Thread):
    def  __init__(self):
        super(HTTPServer, self).__init__()
        self.daemon = True

    def run(self, server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=80):
        server_address = (addr, port)
        httpd = server_class(server_address, handler_class)

        print("Starting httpd server")
        httpd.serve_forever()