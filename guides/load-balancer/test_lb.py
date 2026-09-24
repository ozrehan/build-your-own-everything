#!/usr/bin/env python3
"""Tests for lb.py. Run with: python3 test_lb.py

Spins up two tiny backend HTTP servers (each returns a unique ID string),
starts the load balancer in front of them, and asserts 4 sequential
requests alternate: backend-1, backend-2, backend-1, backend-2.
"""
import os
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import lb  # noqa: E402

PASS = 0


def check(name, cond):
    global PASS
    assert cond, "FAILED: %s" % name
    PASS += 1
    print("ok - %s" % name)


def make_backend(body):
    """A trivial backend server that always answers 200 with `body`."""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass  # keep test output clean

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


def serve_in_background(server):
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return t


def get(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, resp.read().decode()


def main():
    backend1 = make_backend("backend-1")
    backend2 = make_backend("backend-2")
    serve_in_background(backend1)
    serve_in_background(backend2)
    port1 = backend1.server_address[1]
    port2 = backend2.server_address[1]
    print("backends on :%d and :%d" % (port1, port2))

    balancer = lb.create_server(0, ["127.0.0.1:%d" % port1,
                                    "127.0.0.1:%d" % port2])
    serve_in_background(balancer)
    front = balancer.server_address[1]
    print("balancer on :%d" % front)

    try:
        # 4 sequential requests must alternate backends in order.
        bodies = [get("http://127.0.0.1:%d/" % front)[1] for _ in range(4)]
        check("round-robin order", bodies == ["backend-1", "backend-2",
                                              "backend-1", "backend-2"])

        # A 5th request keeps cycling back to the first backend.
        check("cycle continues", get("http://127.0.0.1:%d/" % front)[1] == "backend-1")

        # Status code and body stream through untouched.
        status, body = get("http://127.0.0.1:%d/some/path" % front)
        check("status 200 forwarded", status == 200)
        check("path forwarded (body intact)", body == "backend-2")
    finally:
        balancer.shutdown()
        backend1.shutdown()
        backend2.shutdown()

    print("\n%d tests passed" % PASS)


if __name__ == "__main__":
    main()
