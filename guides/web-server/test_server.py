"""Smoke test for server.py — starts it on an ephemeral port, hits it over HTTP."""
import http.client
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, "server.py"), str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
                c.request("GET", "/")
                r = c.getresponse()
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise AssertionError("server did not start")

        assert r.status == 200, f"GET / -> {r.status}"
        body = r.read()
        assert b"<html" in body.lower(), "index.html not served"
        assert "text/html" in r.getheader("Content-Type"), "wrong content type"

        c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        c.request("GET", "/style.css")
        r = c.getresponse()
        assert r.status == 200 and "text/css" in r.getheader("Content-Type")

        c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        c.request("GET", "/nope-missing")
        assert c.getresponse().status == 404, "expected 404"

        c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        c.request("POST", "/")
        assert c.getresponse().status == 405, "expected 405"

        c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        c.request("HEAD", "/")
        r = c.getresponse()
        assert r.status == 200 and r.read() == b"", "HEAD must have empty body"

        c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        c.request("GET", "/../server.py")
        assert c.getresponse().status == 404, "path traversal not blocked"

        def fetch(_):
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("GET", "/")
            return c.getresponse().status

        with ThreadPoolExecutor(max_workers=10) as ex:
            assert all(s == 200 for s in ex.map(fetch, range(10))), "parallel failed"
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    print("all web-server tests passed")


if __name__ == "__main__":
    main()
