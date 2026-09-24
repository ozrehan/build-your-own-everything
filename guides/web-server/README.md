# Build Your Own Web Server

A tiny HTTP/1.1 static file server in ~150 lines of Python — raw sockets,
no frameworks. You'll learn exactly what happens between the browser's
address bar and the bytes on the wire.

## What you'll build

`server.py` (stdlib only: `socket` + `threading`) that:

- Serves static files from `./www` (a demo site is included)
- Handles `GET` and `HEAD` with correct status codes and headers
- Sniffs content types (`text/html`, `text/css`, `application/javascript`, …)
- Serves each connection on its own thread (parallel requests)
- Blocks path-traversal attacks (`/../secret` → 404)

## How it works

1. **Listen.** A TCP socket binds to 127.0.0.1:8000 and `accept()`s connections
   in a loop.
2. **Parse.** The request line (`GET /style.css HTTP/1.1`) is split into method,
   path, and version. Only `GET`/`HEAD` are allowed, else 405.
3. **Sanitize.** The path is normalized and resolved inside `./www`; anything
   escaping it gets a 404.
4. **Respond.** The file is read, a `Content-Type` is guessed from the
   extension, and a hand-built HTTP response (`HTTP/1.1 200 OK` + headers +
   body) is sent back. `HEAD` sends headers only.
5. **Thread.** Each connection is handled in a `threading.Thread` so slow
   clients don't block each other.

## Run it

```sh
cd guides/web-server
python3 server.py          # serves ./www on http://127.0.0.1:8000
python3 server.py 9000    # custom port
```

Then open http://127.0.0.1:8000 in a browser, or:

```sh
curl -i http://127.0.0.1:8000/
```

## Test it

```sh
python3 test_server.py   # 200/404/405, headers, HEAD, parallel requests
```

## Stretch exercises

1. Add `Connection: keep-alive` — handle multiple requests per socket.
2. Add directory listings for folders without `index.html`.
3. Implement byte ranges (`Range: bytes=0-99`) for resumable downloads.

## Further reading

- [Let's Build A Web Server (Python)](https://ruslanspivak.com/lsbaws-part1/) — sockets-to-WSGI series
- [A Simple Web Server (Python, 500 Lines)](https://aosabook.org/en/500L/a-simple-web-server.html) — architecture of a web server
- [Build Your Own Web Server From Scratch In JavaScript](https://build-your-own.org/blog/20250511122735-build-your-own-web-server-from-scratch-in-javascript) — same idea in Node
