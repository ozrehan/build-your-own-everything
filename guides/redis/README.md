# Build Your Own Redis

A tiny Redis clone in ~180 lines of Python that speaks the real RESP
protocol — real `redis-cli` can talk to it. You'll learn how Redis
serializes data on the wire and how an in-memory store with expiry works.

## What you'll build

`redis.py` (stdlib only: `socket` + `threading`) implementing:

- **RESP protocol** — simple strings, errors, integers, bulk strings, arrays
- **Commands** — `PING`, `ECHO`, `SET`, `GET`, `DEL`, `EXISTS`, `INCR`,
  `EXPIRE`, `TTL`, `KEYS`
- **Expiry** — keys with millisecond-precision TTLs, lazily expired on access
- **Threading** — one thread per client connection

## How it works

1. **RESP parsing.** Commands arrive as arrays of bulk strings, e.g.
   `*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n`. A small recursive parser
   turns bytes into Python lists.
2. **Dispatch.** The first element names the command; a dict maps names to
   handler functions taking the connection and args.
3. **Store.** A plain `dict` holds values; a second dict holds expiry
   timestamps. Every read checks `is_expired()` first and deletes stale keys.
4. **Encoding.** Replies are encoded back to RESP (`+OK\r\n`, `:1\r\n`,
   `$-1\r\n` for nil, …) and written to the socket.
5. **Concurrency.** Each client gets a thread, guarded by a lock around the
   store.

## Run it

```sh
cd guides/redis
python3 redis.py          # listens on 127.0.0.1:6379
python3 redis.py 6380    # custom port
```

Then, if you have `redis-cli` installed:

```sh
redis-cli -p 6379 ping
redis-cli -p 6379 set name ada
redis-cli -p 6379 get name
```

Or talk raw RESP with netcat:

```sh
printf '*1\r\n$4\r\nPING\r\n' | nc 127.0.0.1 6379
```

## Test it

```sh
python3 test_redis.py   # RESP round-trips over a real socket
```

## Stretch exercises

1. Add `LPUSH`/`RPOP` list commands (store Python lists as values).
2. Add persistence: `SAVE` writes the dict to disk, loaded on startup.
3. Add `SUBSCRIBE`/`PUBLISH` pub/sub between connected clients.

## Further reading

- [Write your own miniature Redis with Python](https://charlesleifer.com/blog/building-a-simple-redis-clone-in-python/) — the classic tutorial
- [Build Your Own Redis from Scratch (Go)](https://www.build-redis-from-scratch.dev) — full book-length guide
- [Build your own Redis client and server (Rust/tokio)](https://tokio.rs/tokio/tutorial/setup) — async approach
