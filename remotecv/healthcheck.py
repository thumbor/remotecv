import logging
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CONTROL_CHARS = str.maketrans(
    {c: rf"\x{c:02x}" for c in [*range(0x20), *range(0x7F, 0xA0)]}
)
CONTROL_CHARS[ord("\\")] = r"\\"


class HealthCheckHandler(BaseHTTPRequestHandler):
    server_version = "remotecv"
    timeout = 5

    def version_string(self):
        return self.server_version

    def do_GET(self):
        self.send_response(200)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b"WORKING")

    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        message = format.replace('"', "") % args
        logging.info(message.translate(CONTROL_CHARS))


class HealthCheckServer(ThreadingHTTPServer):
    def __init__(self, server_address, handler_class):
        host, port = server_address
        host = host.strip("[]")
        if ":" in host:
            self.address_family = socket.AF_INET6
        super().__init__((host, port), handler_class)
