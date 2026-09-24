#!/usr/bin/env python3
"""lb.py -- a tiny round-robin HTTP reverse proxy load balancer.

Listens on a frontend port and forwards each incoming GET request to the
next backend in round-robin order, streaming the backend's status code,
headers, and body back to the client.

Usage:
    python3 lb.py 8000 127.0.0.1:9001 127.0.0.1:9002

Then `curl http://localhost:8000/` hits 9001, the next request hits 9002,
the next hits 9001 again, and so on.

Stdlib only: http.server + urllib.
"""

import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Hop-by-hop headers must not be forwarded by a proxy (RFC 2616 section 13.5.1).
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "transfer-encoding", "upgrade",
}


def make_handler(backends):
    """Build a request-handler class bound to a backend list.

    The round-robin counter is shared by all handler instances and guarded
    by a lock, because ThreadingHTTPServer handles requests on threads.
    """
    counter = [0]
    lock = threading.Lock()

    class LBHandler(BaseHTTPRequestHandler):
        server_version = "TinyLB/1.0"

        def _pick_backend(self):
            with lock:
                backend = backends[counter[0] % len(backends)]
                counter[0] += 1
            return backend

        def do_GET(self):
            backend = self._pick_backend()
            url = "http://%s%s" % (backend, self.path)
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    body = resp.read()
                    self.send_response(resp.status)
                    for name, value in resp.headers.items():
                        if name.lower() not in HOP_BY_HOP:
                            self.send_header(name, value)
                    # Helpful for debugging: which backend served this request.
                    self.send_header("X-Backend", backend)
                    self.end_headers()
                    self.wfile.write(body)
            except urllib.error.HTTPError as e:
                # Backend answered with an error status: forward it as-is.
                body = e.read()
                self.send_response(e.code)
                self.send_header("X-Backend", backend)
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                # Backend unreachable / timed out.
                self.send_error(502, "Bad Gateway: backend %s: %s" % (backend, e))

        def log_message(self, fmt, *args):
            sys.stderr.write("lb: %s\n" % (fmt % args))

    return LBHandler


def create_server(port, backends):
    """Create (but do not start) the load balancer server."""
    handler = make_handler(backends)
    return ThreadingHTTPServer(("0.0.0.0", port), handler)


def main(argv):
    if len(argv) < 3:
        sys.exit("usage: python3 lb.py <frontend-port> <backend1> [backend2 ...]\n"
                 "example: python3 lb.py 8000 127.0.0.1:9001 127.0.0.1:9002")
    port = int(argv[1])
    backends = argv[2:]
    server = create_server(port, backends)
    print("load balancer listening on :%d -> %s" % (port, ", ".join(backends)))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")


if __name__ == "__main__":
    main(sys.argv)
