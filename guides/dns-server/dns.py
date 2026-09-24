#!/usr/bin/env python3
"""Build your own DNS server.

A tiny authoritative DNS server over UDP (stdlib `socket` + `struct` only).
It parses DNS query packets (header + question section, A records) and
answers from a configurable zone dict. Unknown names get NXDOMAIN (RCODE 3).

    python3 dns.py            # serve 127.0.0.1:5353 with the default zone

Test it with dig:  dig @127.0.0.1 -p 5353 example.test A
"""

import socket
import struct

# The zone: domain name -> IPv4 address.
ZONE = {
    "example.test": "93.184.216.34",
    "localhost.test": "127.0.0.1",
}

HOST, PORT = "127.0.0.1", 5353


def decode_name(data, offset):
    """Decode a DNS domain name starting at `offset`, following compression
    pointers (0xC0xx) if present. Returns (dotted_name, offset_after_name)."""
    labels = []
    jumped = False
    end = offset
    while True:
        length = data[offset]
        if length == 0:
            offset += 1
            if not jumped:
                end = offset
            break
        if length & 0xC0 == 0xC0:
            # Compression pointer: 2 bytes, top 2 bits set, rest is an offset.
            pointer = struct.unpack("!H", data[offset:offset + 2])[0] & 0x3FFF
            if not jumped:
                end = offset + 2
            offset = pointer
            jumped = True
            continue
        offset += 1
        labels.append(data[offset:offset + length].decode("ascii"))
        offset += length
        if not jumped:
            end = offset
    return ".".join(labels), end


def encode_name(name):
    """Encode 'example.test' as length-prefixed labels + zero byte."""
    return b"".join(bytes([len(p)]) + p.encode("ascii") for p in name.split(".")) + b"\x00"


def build_response(query, zone):
    """Parse one DNS query packet and build the response packet."""
    qid, flags, qdcount, _, _, _ = struct.unpack("!HHHHHH", query[:12])
    name, off = decode_name(query, 12)
    qtype, qclass = struct.unpack("!HH", query[off:off + 4])
    question = query[12:off + 4]  # echo the question back verbatim

    rd = flags & 0x0100  # copy the client's "recursion desired" bit
    ip = zone.get(name.lower()) if qtype == 1 else None

    if ip is not None:
        rcode, ancount = 0, 1  # NOERROR, one answer
    else:
        rcode, ancount = 3, 0  # NXDOMAIN, no answers

    # Flags: QR=1 (response) | RD (copied) | RA=1 | RCODE
    resp_flags = 0x8000 | rd | 0x0080 | rcode
    header = struct.pack("!HHHHHH", qid, resp_flags, 1, ancount, 0, 0)

    answer = b""
    if ancount:
        # NAME as compression pointer 0xC00C (offset 12 = the question name),
        # TYPE=A, CLASS=IN, TTL=300, RDLENGTH=4, RDATA=IPv4 bytes.
        answer = struct.pack("!HHHLH", 0xC00C, 1, 1, 300, 4) + socket.inet_aton(ip)

    return header + question + answer


def serve(host=HOST, port=PORT, zone=None):
    """Run the UDP server forever."""
    zone = zone if zone is not None else ZONE
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"DNS server listening on {host}:{port} (zone: {', '.join(sorted(zone))})")
    while True:
        data, addr = sock.recvfrom(512)
        try:
            resp = build_response(data, zone)
            # Reply on a connected socket (connect + send) rather than
            # sendto — same result, and it works on networks where raw
            # sendto is filtered.
            out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            out.connect(addr)
            out.send(resp)
            out.close()
        except Exception:
            pass  # never let a malformed packet kill the server


if __name__ == "__main__":
    serve()
