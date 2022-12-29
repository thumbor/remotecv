from http.server import BaseHTTPRequestHandler
import logging


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b"WORKING")

    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        logging.info(format.replace('\"', ""), *args)
