#!/usr/bin/env python3
"""tinyredis - a tiny Redis clone in ~180 lines of Python (stdlib only).

Speaks enough of the RESP protocol for redis-cli to connect.
In-memory store with key expiry, one thread per connection.

Usage:  python3 redis.py [port]      (default 6379)
"""

import fnmatch
import socket
import sys
import threading
import time

store = {}  # key(bytes) -> [value(bytes), expire_at(float|None)]
lock = threading.Lock()


def _entry(key):
    """Return [value, expire_at] or None, deleting expired keys lazily."""
    e = store.get(key)
    if e is None:
        return None
    if e[1] is not None and e[1] <= time.time():
        del store[key]
        return None
    return e


# ---------------- RESP encoding / decoding ----------------

def encode(obj):
    if obj is None:
        return b"$-1\r\n"                       # null bulk string
    if isinstance(obj, int):
        return b":%d\r\n" % obj                 # integer
    if isinstance(obj, bytes):
        return b"$%d\r\n%s\r\n" % (len(obj), obj)  # bulk string
    if isinstance(obj, str):
        if obj.startswith("-"):  # "-ERR ..." -> RESP error reply
            return b"-" + obj[1:].encode() + b"\r\n"
        return b"+" + obj.encode() + b"\r\n"   # simple string
    if isinstance(obj, list):
        return b"*%d\r\n" % len(obj) + b"".join(encode(x) for x in obj)
    raise TypeError("cannot encode %r" % type(obj))


def parse(f):
    """Parse one RESP value from a buffered binary file object."""
    line = f.readline()
    if not line:
        raise ConnectionError("client disconnected")
    if line[0:1] != b"*":  # inline command fallback (telnet)
        return line.strip().split()
    n = int(line[1:])
    if n <= 0:
        return []
    args = []
    for _ in range(n):
        hlen = f.readline()
        if hlen[0:1] != b"$":
            raise ValueError("expected bulk string")
        ln = int(hlen[1:])
        if ln == -1:
            args.append(None)
        else:
            args.append(f.read(ln))
            f.read(2)  # trailing \r\n
    return args


# ---------------- commands ----------------

def cmd_ping(a):
    return a[0] if a else "PONG"


def cmd_echo(a):
    if not a:
        return "-ERR wrong number of arguments for 'echo' command"
    return a[0]


def cmd_set(a):
    if len(a) < 2:
        return "-ERR wrong number of arguments for 'set' command"
    key, val = a[0], a[1]
    exp = None
    if len(a) > 2 and a[2].upper() == b"EX" and len(a) > 3:
        exp = time.time() + int(a[3])
    with lock:
        store[key] = [val, exp]
    return "OK"


def cmd_get(a):
    with lock:
        e = _entry(a[0])
    return e[0] if e else None


def cmd_del(a):
    n = 0
    with lock:
        for k in a:
            if _entry(k) is not None:
                del store[k]
                n += 1
    return n


def cmd_exists(a):
    with lock:
        return sum(1 for k in a if _entry(k) is not None)


def cmd_incr(a):
    with lock:
        e = _entry(a[0])
        try:
            v = int(e[0]) + 1 if e else 1
        except ValueError:
            return "-ERR value is not an integer or out of range"
        store[a[0]] = [str(v).encode(), e[1] if e else None]
    return v


def cmd_expire(a):
    with lock:
        e = _entry(a[0])
        if e is None:
            return 0
        e[1] = time.time() + int(a[1])
    return 1


def cmd_ttl(a):
    with lock:
        e = store.get(a[0])
        if e is None or (e[1] is not None and e[1] <= time.time()):
            store.pop(a[0], None)
            return -2
        if e[1] is None:
            return -1
        return int(e[1] - time.time())


def cmd_keys(a):
    pat = a[0].decode() if a else "*"
    with lock:
        keys = [k for k in list(store) if _entry(k) is not None
                and fnmatch.fnmatchcase(k.decode(errors="replace"), pat)]
    return keys


COMMANDS = {
    b"PING": cmd_ping, b"ECHO": cmd_echo, b"SET": cmd_set, b"GET": cmd_get,
    b"DEL": cmd_del, b"EXISTS": cmd_exists, b"INCR": cmd_incr,
    b"EXPIRE": cmd_expire, b"TTL": cmd_ttl, b"KEYS": cmd_keys,
    b"COMMAND": lambda a: [],
}


def dispatch(argv):
    if not argv:
        return "-ERR empty command"
    name = argv[0].upper() if isinstance(argv[0], bytes) else argv[0].upper().encode()
    fn = COMMANDS.get(name)
    if fn is None:
        try:
            cmd = name.decode()
        except Exception:
            cmd = repr(name)
        return "-ERR unknown command '%s'" % cmd
    try:
        return fn(argv[1:])
    except (IndexError, ValueError):
        return "-ERR wrong number of arguments for '%s' command" % name.decode().lower()


def serve_client(conn):
    with conn:
        f = conn.makefile("rb")
        try:
            while True:
                argv = parse(f)
                conn.sendall(encode(dispatch(argv)))
        except (ConnectionError, ValueError, BrokenPipeError):
            pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 6379
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(64)
    print("tinyredis listening on 127.0.0.1:%d" % port, flush=True)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=serve_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
