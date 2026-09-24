# Build Your Own Load Balancer

A tiny **round-robin HTTP reverse proxy** in one Python file (`lb.py`,
~130 lines, stdlib only). It accepts client requests on a frontend port
and deals them out to backend servers one after another, streaming each
backend's response back to the client.

## What you'll build

`lb.py` is a reverse proxy: clients talk only to it, and it forwards
each request to the next backend in rotation. Run two (or more) backend
web servers, point the balancer at them, and watch traffic alternate
between them — the core idea behind every production load balancer, from
nginx to AWS ELB.

## How it works, step by step

1. **Frontend server** — `create_server()` starts a `ThreadingHTTPServer`
   (thread-per-request, so slow backends don't block each other) on the
   frontend port.
2. **Round-robin pick** — `make_handler()` builds a handler class bound
   to your backend list. A shared counter, guarded by a `threading.Lock`,
   picks `backends[counter % len(backends)]` and increments — the lock
   matters because requests arrive on different threads.
3. **Forward** — `do_GET()` rebuilds the URL as
   `http://<backend><path>` and fetches it with `urllib`. The query
   string and path pass through untouched.
4. **Stream back** — the backend's status code, response headers
   (minus hop-by-hop ones like `Connection`, which a proxy must not
   forward), and body are relayed to the client. An `X-Backend` header is
   added so you can see which backend answered.
5. **Failure mode** — if a backend is down, the client gets `502 Bad
   Gateway` instead of a hang; if a backend returns an error status
   (e.g. 404), it is forwarded as-is.

## How to run

Terminal 1 and 2 — start two backends (any static server works):

```bash
python3 -m http.server 9001
python3 -m http.server 9002
```

Terminal 3 — start the balancer:

```bash
cd guides/load-balancer
python3 lb.py 8000 127.0.0.1:9001 127.0.0.1:9002
```

Then open http://localhost:8000/ and refresh — or run
`curl -s -H "X-Debug: 1" localhost:8000 -D -` and watch the `X-Backend`
header alternate between the two backends.

## How to test

```bash
python3 test_lb.py
```

The test starts two in-process backends (returning the unique strings
`backend-1` / `backend-2`), puts the balancer in front of them, fires 4
sequential requests, and asserts the responses come back in strict
alternating order, that a 5th request cycles back to backend 1, and that
status codes and paths forward intact.

## Stretch exercises

1. **Health checks** — ping backends every few seconds and skip the ones
   that don't answer, instead of 502-ing.
2. **Weighted round-robin** — let some backends take twice the traffic
   (hint: expand the rotation list, e.g. `[a, b, b]`).
3. **Least-connections** — track in-flight requests per backend and
   route to the least busy one instead of strict rotation.

## Further reading

- [nginx reverse proxy & load balancing guide](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [Python `http.server` docs (the stdlib pieces used here)](https://docs.python.org/3/library/http.server.html)
- [HAProxy "load balancing algorithms" concepts](https://www.haproxy.com/blog/load-balancing-algorithms)
