#!/usr/bin/env python3
"""
Project Volusia — Robust Reverse Proxy Server
Serves static files and proxies API calls with better error handling.

Usage:
    python deploy_portal.py
"""

import http.server
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
STATIC_DIR = Path("Z:/zqm-garden-03/web/zqmlabs.com")
PORTAL_PORT = 8789
CONTRIBUTE_PORT = 8790
LISTEN_PORT = 80


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static files and proxy API requests."""
    
    def do_GET(self):
        # API routes → portal
        if self.path.startswith("/api/") and not self.path.startswith("/api/v1/"):
            self._proxy_to_portal()
            return
        
        # Contribution API → contribution service
        if self.path.startswith("/api/v1/"):
            self._proxy_to_contribute()
            return
        
        # Project Volusia portal page
        if self.path == "/project-volusia" or self.path == "/project-volusia/":
            locations = [
                STATIC_DIR / "project-volusia.html",
                Path("Z:/14_Projects/Active/Project-Volusia/project-volusia.html"),
            ]
            for loc in locations:
                if loc.exists():
                    self._serve_file_loc(loc)
                    return
            self._send_redirect("/")
            return
        
        # Data explorer
        if self.path == "/data-explorer" or self.path == "/data-explorer/":
            self._proxy_to_portal()
            return
        
        # Contribution page
        if self.path == "/contribute" or self.path == "/contribute/":
            locations = [
                STATIC_DIR / "contribute.html",
                Path("Z:/14_Projects/Active/Project-Volusia/contribute.html"),
            ]
            for loc in locations:
                if loc.exists():
                    self._serve_file_loc(loc)
                    return
            self._send_redirect("/")
            return
        
        # Static files
        self._serve_static()
    
    def do_POST(self):
        # Contribution API → contribution service
        if self.path.startswith("/api/v1/contributions"):
            self._proxy_to_contribute()
            return
        
        # Portal API → portal
        if self.path.startswith("/api/"):
            self._proxy_to_portal()
            return
        
        self.send_error(404, "Not Found")
    
    def do_PATCH(self):
        # Contribution API → contribution service
        if self.path.startswith("/api/v1/contributions"):
            self._proxy_to_contribute()
            return
        
        self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()
    
    def _serve_static(self):
        """Serve static files from the website directory."""
        path = self.path
        if path == "/":
            path = "/index.html"
        
        file_path = STATIC_DIR / path.lstrip("/")
        
        if file_path.exists() and file_path.is_file():
            self._serve_file_loc(file_path)
        else:
            # Fallback to index.html
            index_path = STATIC_DIR / "index.html"
            if index_path.exists():
                self._serve_file_loc(index_path)
            else:
                self.send_error(404, "Not Found")
    
    def _serve_file_loc(self, file_path):
        """Serve a specific file."""
        try:
            self.send_response(200)
            
            # Content type
            ext = file_path.suffix.lower()
            content_types = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }
            self.send_header("Content-Type", content_types.get(ext, "application/octet-stream"))
            
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def _send_redirect(self, location):
        """Send a redirect."""
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()
    
    def _proxy_to_portal(self):
        """Proxy request to the portal service."""
        target = f"http://127.0.0.1:{PORTAL_PORT}{self.path}"
        self._proxy_request(target)
    
    def _proxy_to_contribute(self):
        """Proxy request to the contribution service."""
        target = f"http://127.0.0.1:{CONTRIBUTE_PORT}{self.path}"
        self._proxy_request(target)
    
    def _proxy_request(self, target):
        """Proxy a request to the target URL."""
        try:
            # Read POST/PATCH body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Build request
            req = urllib.request.Request(target, data=body, method=self.command)
            for key, value in self.headers.items():
                if key.lower() not in ("host", "transfer-encoding"):
                    req.add_header(key, value)
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(key, value)
                
                # CORS headers
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                self.wfile.write(response.read())
        
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(e.read())
        
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            error = json.dumps({"error": "Service Unavailable", "detail": str(e)})
            self.wfile.write(error.encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            error = json.dumps({"error": "Internal Server Error", "detail": str(e)})
            self.wfile.write(error.encode())


def main():
    server = http.server.HTTPServer(("0.0.0.0", LISTEN_PORT), ProxyHandler)
    print(f"Project Volusia Proxy Server running on port {LISTEN_PORT}")
    print(f"  Static files: {STATIC_DIR}")
    print(f"  Portal API: http://127.0.0.1:{PORTAL_PORT}")
    print(f"  Contribution API: http://127.0.0.1:{CONTRIBUTE_PORT}")
    print(f"\nAccess points:")
    print(f"  http://localhost/ — Main website")
    print(f"  http://localhost/contribute/ — Contribution page")
    print(f"  http://localhost/project-volusia — Portal")
    print(f"  http://localhost/data-explorer — Data Explorer")
    print(f"\nPress Ctrl+C to stop.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
