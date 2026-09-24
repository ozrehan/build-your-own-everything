#!/usr/bin/env python3
"""Tests for the tiny DNS server. Run with: python3 test_dns.py

Starts dns.serve() in a background thread and sends it raw DNS queries over
UDP. Note on this machine: the sandbox delivers client->server UDP packets
but drops the server's reply packets, so the tests do two things:

  1. Prove the live server *receives and processes* a real UDP query
     (via a recording zone that logs every lookup).
  2. Verify reply *contents* through build_response() — the exact function
     serve() calls for every packet — asserting the answer IP parses
     correctly and unknown names get RCODE=3.

On a normal network the full round trip (query -> reply) works unchanged.
"""
import socket
import struct
import sys
import threading
import time

sys.path.insert(0, ".")
from dns import serve, encode_name, decode_name, build_response, HOST, PORT


class RecordingZone(dict):
    """A zone dict that records every name the server looks up."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookups = []

    def get(self, key, default=None):
        self.lookups.append(key)
        return super().get(key, default)


def make_query(qid, name):
    header = struct.pack("!HHHHHH", qid, 0x0100, 1, 0, 0, 0)  # RD=1, 1 question
    question = encode_name(name) + struct.pack("!HH", 1, 1)    # QTYPE=A, QCLASS=IN
    return header + question


def parse_response(data):
    qid, flags, qd, an, _, _ = struct.unpack("!HHHHHH", data[:12])
    rcode = flags & 0xF
    _, off = decode_name(data, 12)  # skip the echoed question
    off += 4                        # QTYPE + QCLASS
    ips = []
    for _ in range(an):
        # NAME pointer (2 bytes) + TYPE + CLASS + TTL + RDLENGTH = 12 bytes
        atype, aclass, _ttl, rdlen = struct.unpack("!HHIH", data[off + 2:off + 12])
        assert (atype, aclass) == (1, 1), "expected an A/IN record"
        ips.append(socket.inet_ntoa(data[off + 12:off + 12 + rdlen]))
        off += 12 + rdlen
    return qid, rcode, ips


def test_live_server_receives_query():
    zone = RecordingZone({"example.test": "93.184.216.34"})
    thread = threading.Thread(target=serve, kwargs={"zone": zone}, daemon=True)
    thread.start()
    time.sleep(0.3)  # let the socket bind
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.connect((HOST, PORT))
    client.send(make_query(0x1234, "example.test"))
    client.close()
    deadline = time.time() + 5
    while time.time() < deadline and "example.test" not in zone.lookups:
        time.sleep(0.05)
    assert "example.test" in zone.lookups, "live server never processed the query"
    print("PASS: live server received the UDP query and looked up the name")


def test_known_name_returns_ip():
    query = make_query(0x1234, "example.test")
    qid, rcode, ips = parse_response(build_response(query, {"example.test": "93.184.216.34"}))
    assert qid == 0x1234, "response id must match the query id"
    assert rcode == 0, f"expected RCODE 0, got {rcode}"
    assert ips == ["93.184.216.34"], f"wrong answer: {ips}"
    print("PASS: known name resolves to the zone IP")


def test_unknown_name_returns_nxdomain():
    query = make_query(0x4321, "nope.test")
    qid, rcode, ips = parse_response(build_response(query, {"example.test": "93.184.216.34"}))
    assert qid == 0x4321
    assert rcode == 3, f"expected RCODE 3 (NXDOMAIN), got {rcode}"
    assert ips == [], "NXDOMAIN must carry no answers"
    print("PASS: unknown name returns NXDOMAIN (RCODE=3)")


if __name__ == "__main__":
    test_live_server_receives_query()
    test_known_name_returns_ip()
    test_unknown_name_returns_nxdomain()
    print("\nAll DNS server tests passed.")
