#!/usr/bin/env python3

import argparse
import http.server

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_my_headers()
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='port number')
    args = parser.parse_args()

    # Start the HTTP server
    http.server.test(HandlerClass=MyHTTPRequestHandler, port=args.port)

if __name__ == '__main__':
    main()
