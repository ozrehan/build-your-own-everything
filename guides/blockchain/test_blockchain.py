#!/usr/bin/env python3
"""Tests for the tiny blockchain. Run with: python3 test_blockchain.py"""
import sys
sys.path.insert(0, ".")
from blockchain import Blockchain, Block


def test_mined_block_meets_difficulty():
    block = Block(0, [{"from": "a", "to": "b", "amount": 1}], "0")
    block.mine(difficulty=2)
    assert block.hash.startswith("00"), f"hash {block.hash} misses difficulty 2"
    assert block.compute_hash() == block.hash, "stored hash != recomputed hash"
    print("PASS: mined block hash meets difficulty")


def test_tampering_breaks_validity():
    chain = Blockchain(difficulty=2)
    chain.add_block([{"from": "alice", "to": "bob", "amount": 5}])
    assert chain.is_valid(), "fresh chain should be valid"
    # Tamper: rewrite a transaction without re-mining.
    chain.chain[1].transactions[0]["amount"] = 5000
    assert not chain.is_valid(), "tampered chain must be invalid"
    print("PASS: tampering with a transaction breaks is_valid()")


def test_chain_links_are_consistent():
    chain = Blockchain(difficulty=2)
    chain.add_block([{"from": "a", "to": "b", "amount": 1}])
    chain.add_block([{"from": "b", "to": "c", "amount": 2}])
    assert chain.is_valid()
    for i in range(1, len(chain.chain)):
        assert chain.chain[i].previous_hash == chain.chain[i - 1].hash, \
            f"block {i} does not link to block {i - 1}"
        assert chain.chain[i].index == i
    print("PASS: chain links are consistent")


def test_remining_after_tamper_passes_hash_but_fails_pow():
    # A sneaky attacker recomputes the hash without mining: the hash won't
    # meet the difficulty, so is_valid() must still reject it.
    chain = Blockchain(difficulty=2)
    chain.add_block([{"from": "a", "to": "b", "amount": 1}])
    victim = chain.chain[1]
    victim.transactions[0]["amount"] = 999
    victim.nonce = 0
    victim.hash = victim.compute_hash()  # recompute, but no mining
    assert not chain.is_valid(), "unmined rewritten block must be invalid"
    print("PASS: recomputed-but-unmined block fails is_valid()")


if __name__ == "__main__":
    test_mined_block_meets_difficulty()
    test_tampering_breaks_validity()
    test_chain_links_are_consistent()
    test_remining_after_tamper_passes_hash_but_fails_pow()
    print("\nAll blockchain tests passed.")
