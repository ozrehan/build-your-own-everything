# Build Your Own DNS Server

A tiny authoritative DNS server in ~110 lines of Python, using only `socket` and `struct`. It speaks real DNS over UDP — `dig` can query it.

## What you'll build

- A UDP server on `127.0.0.1:5353` that parses DNS query packets (header + question section)
- Answers **A-record** queries from a configurable zone dict, e.g. `{"example.test": "93.184.216.34"}`
- Returns **NXDOMAIN (RCODE 3)** for names not in the zone
- Correct DNS packet details: echoed question section, compression pointer `0xC00C` in answers, copied RD bit, RA bit set

## How it works, in plain steps

1. **DNS is just bytes.** A query is a 12-byte header (ID, flags, counts) followed by the question: the domain name as length-prefixed labels (`\x07example\x04test\x00`), then QTYPE (1 = A) and QCLASS (1 = IN). `struct.unpack("!HHHHHH", ...)` reads the header.
2. **Names can be compressed.** Real DNS packets use `0xC0xx` pointers to reuse names. `decode_name()` walks the labels and follows pointers when it sees the top two bits set, so it can parse questions from any client.
3. **The response echoes + answers.** `build_response()` copies the query ID, sets QR=1 (this is a response), copies the client's RD bit, sets RA=1, and echoes the question section verbatim. Then it looks the name up in the zone dict.
4. **Hit or miss.** If the name is in the zone (and QTYPE is A), it appends one answer record: name as pointer `0xC00C` (offset 12 = where the question name starts), TYPE=A, CLASS=IN, TTL=300, and the 4 IP bytes. If not, it sets RCODE=3 (NXDOMAIN) and sends no answers.

## How to run

```bash
python3 dns.py
```

Then query it in another terminal:

```bash
dig @127.0.0.1 -p 5353 example.test A +short
# 93.184.216.34
dig @127.0.0.1 -p 5353 nope.test A
# ... status: NXDOMAIN
```

Edit the `ZONE` dict at the top of `dns.py` to serve your own names.

## How to test

```bash
python3 test_dns.py
```

The test starts `serve()` in a background thread, sends it a raw hand-built DNS query over UDP, and asserts the server received and processed it; then it verifies through `build_response()` (the exact function the server calls per packet) that a known name resolves to the right IP and an unknown name returns RCODE=3 with no answers.

## Stretch exercises

1. **More record types.** Support AAAA (IPv6, 16-byte RDATA) and CNAME. For CNAME, the RDATA is an encoded domain name — and the client will then re-query for the target, so test the full chase with `dig`.
2. **Forwarding resolver.** If a name isn't in your zone, forward the query to `8.8.8.8:53`, wait for the real answer, and relay it back to the client. You'll need to match the upstream response to the pending query by ID.
3. **A zone file parser.** Read a real zone-file format (`name  TTL  IN  A  1.2.3.4`, one per line, with `$ORIGIN`) into your zone dict so the server loads its data from disk.

## Further reading

- RFC 1035, sections 3–4 — https://datatracker.ietf.org/doc/html/rfc1035 (the DNS spec; surprisingly readable for the packet format)
- "Let's build a DNS server" — https://github.com/codecrafters-io/build-your-own-x (the DNS challenge this guide is modeled on)
- Julia Evans's DNS zines — https://wizardzines.com/zines/dns/ (friendly visual explanations of queries, records, and resolution)
