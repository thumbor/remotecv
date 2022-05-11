from http.server import BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b"WORKING")
