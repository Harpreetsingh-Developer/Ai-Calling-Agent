#!/usr/bin/env python3
"""
Simple HTTP server to test connectivity.
"""

import http.server
import socketserver
import json

PORT = 8080

class JSONHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == "/api/health":
            response = {
                "status": "ok",
                "message": "AI Calling Agent test server is running"
            }
        else:
            response = {
                "message": "Hello from simple HTTP server",
                "path": self.path
            }
        
        self.wfile.write(json.dumps(response).encode("utf-8"))

def run():
    with socketserver.TCPServer(("0.0.0.0", PORT), JSONHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run() 