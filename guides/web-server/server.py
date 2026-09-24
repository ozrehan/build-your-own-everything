#!/usr/bin/env python3
"""tinyhttp - a tiny HTTP/1.1 static file server in ~150 lines.

Stdlib only: socket + threading. Serves files from ./www,
handles GET (and HEAD), returns proper status codes and headers.

Usage:  python3 server.py [port]   (default port 8000)
"""

import mimetypes
import os
import socket
import threading
from datetime import datetime, timezone

WWW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")

# We only need a few, but mimetypes covers the rest.
EXTRA_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/x-icon",
    ".json": "application/json",
    ".txt": "text/plain",
}

STATUS = {200: "OK", 404: "Not Found", 405: "Method Not Allowed", 400: "Bad Request"}


def http_date():
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")


def send_response(conn, code, body=b"", ctype="text/html", head_only=False):
    reason = STATUS.get(code, "Unknown")
    headers = [
        f"HTTP/1.1 {code} {reason}",
        f"Date: {http_date()}",
        "Server: tinyhttp/1.0",
        f"Content-Type: {ctype}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    conn.sendall("\r\n".join(headers).encode())
    if not head_only and body:
        conn.sendall(body)


def safe_path(url_path):
    """Map a URL path to a file under WWW, blocking '..' escapes."""
    path = url_path.split("?", 1)[0].split("#", 1)[0]
    if path.endswith("/"):
        path += "index.html"
    full = os.path.normpath(os.path.join(WWW, path.lstrip("/")))
    if not full.startswith(WWW + os.sep) and full != WWW:
        return None
    return full


def handle(conn, addr):
    try:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 65536:
                break
        if not data:
            return
        request_line = data.split(b"\r\n", 1)[0].decode("latin-1")
        parts = request_line.split(" ")
        if len(parts) != 3:
            send_response(conn, 400, b"<h1>400 Bad Request</h1>")
            return
        method, target, _version = parts
        if method not in ("GET", "HEAD"):
            send_response(conn, 405, b"<h1>405 Method Not Allowed</h1>")
            return

        path = safe_path(target)
        if path is None or not os.path.isfile(path):
            body = b"<h1>404 Not Found</h1><p>tinyhttp has no such file.</p>"
            send_response(conn, 404, body, head_only=(method == "HEAD"))
            return

        ext = os.path.splitext(path)[1].lower()
        ctype = EXTRA_TYPES.get(ext) or mimetypes.guess_type(path)[0] or \
            "application/octet-stream"
        with open(path, "rb") as f:
            body = f.read()
        send_response(conn, 200, body, ctype, head_only=(method == "HEAD"))
    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:  # never kill the server on a bad request
        try:
            send_response(conn, 400, f"<h1>400</h1><p>{e}</p>".encode())
        except Exception:
            pass
    finally:
        conn.close()


def serve(port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(16)
    print(f"tinyhttp serving {WWW} on http://127.0.0.1:{port}  (Ctrl-C to stop)")
    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nbye!")
    finally:
        srv.close()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.makedirs(WWW, exist_ok=True)
    serve(port)
