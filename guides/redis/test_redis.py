"""Test for redis.py — speaks raw RESP over a socket to a live server."""
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Conn:
    def __init__(self, port):
        self.s = socket.create_connection(("127.0.0.1", port), timeout=5)
        self.buf = b""

    def cmd(self, *args):
        out = f"*{len(args)}\r\n".encode()
        for a in args:
            a = str(a).encode()
            out += f"${len(a)}\r\n".encode() + a + b"\r\n"
        self.s.sendall(out)
        return self._read()

    def _read(self):
        while b"\r\n" not in self.buf:
            chunk = self.s.recv(4096)
            assert chunk, "connection closed"
            self.buf += chunk
        line, self.buf = self.buf.split(b"\r\n", 1)
        t, rest = line[:1], line[1:]
        if t == b"+":
            return rest.decode()
        if t == b"-":
            raise AssertionError("ERR " + rest.decode())
        if t == b":":
            return int(rest)
        if t == b"$":
            n = int(rest)
            if n == -1:
                return None
            while len(self.buf) < n + 2:
                self.buf += self.s.recv(4096)
            data, self.buf = self.buf[:n], self.buf[n + 2:]
            return data.decode()
        if t == b"*":
            return [self._read() for _ in range(int(rest))]
        raise AssertionError(f"unknown reply type: {line!r}")

    def close(self):
        self.s.close()


def main():
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, "redis.py"), str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        c = None
        for _ in range(50):
            try:
                c = Conn(port)
                break
            except OSError:
                time.sleep(0.1)
        assert c, "server did not start"

        assert c.cmd("PING") == "PONG"
        assert c.cmd("ECHO", "hello") == "hello"
        assert c.cmd("SET", "k", "v") == "OK"
        assert c.cmd("GET", "k") == "v"
        assert c.cmd("GET", "missing") is None
        assert c.cmd("EXISTS", "k") == 1
        assert c.cmd("EXISTS", "missing") == 0
        assert c.cmd("DEL", "k") == 1
        assert c.cmd("GET", "k") is None

        assert c.cmd("SET", "n", "10") == "OK"
        assert c.cmd("INCR", "n") == 11

        assert c.cmd("SET", "temp", "x") == "OK"
        assert c.cmd("EXPIRE", "temp", "1") == 1
        assert c.cmd("TTL", "temp") in (0, 1)
        time.sleep(1.2)
        assert c.cmd("GET", "temp") is None, "key should have expired"

        c.cmd("SET", "a1", "1")
        c.cmd("SET", "a2", "2")
        keys = c.cmd("KEYS", "a*")
        assert set(keys) == {"a1", "a2"}, f"KEYS mismatch: {keys}"
        c.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    print("all redis tests passed")


if __name__ == "__main__":
    main()
