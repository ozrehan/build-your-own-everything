#!/usr/bin/env python3
"""Build your own blockchain.

A tiny blockchain: blocks hold transactions, each block is sealed with a
SHA-256 hash, and sealing requires *proof of work* — finding a nonce so the
block's hash starts with N zero hex characters. Anyone can verify the chain
by recomputing the hashes.
"""

import hashlib
import json
import time


class Block:
    """One block in the chain."""

    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        # transactions: a list of dicts, e.g. {"from": "alice", "to": "bob", "amount": 5}
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        # The block's identity is the hash of everything inside it.
        self.hash = self.compute_hash()

    def compute_hash(self):
        """SHA-256 over a canonical JSON encoding of the block's contents."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        """Proof of work: keep trying nonces until the hash starts with
        `difficulty` zero hex characters. Returns the winning hash."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash


class Blockchain:
    """An append-only chain of mined blocks."""

    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.chain = []
        # The first block is special: it has no real predecessor, so it
        # points at the dummy hash "0".
        genesis = Block(0, [{"from": "genesis", "to": "network", "amount": 0}], "0")
        genesis.mine(self.difficulty)
        self.chain.append(genesis)

    def add_block(self, transactions):
        """Mine a new block containing `transactions` and append it."""
        prev = self.chain[-1]
        block = Block(len(self.chain), transactions, prev.hash)
        block.mine(self.difficulty)
        self.chain.append(block)
        return block

    def is_valid(self):
        """Check every block: hashes recompute correctly, each block links
        to the previous one, and every block's hash meets the difficulty."""
        target = "0" * self.difficulty
        for i, block in enumerate(self.chain):
            # 1. The stored hash must match the block's actual contents.
            if block.compute_hash() != block.hash:
                return False
            # 2. The block must actually have done the proof of work.
            if not block.hash.startswith(target):
                return False
            # 3. Each block must point at the hash of the one before it.
            if i > 0 and block.previous_hash != self.chain[i - 1].hash:
                return False
        return True


if __name__ == "__main__":
    chain = Blockchain(difficulty=2)
    print("Mining 3 blocks (difficulty=2)...")
    chain.add_block([{"from": "alice", "to": "bob", "amount": 5}])
    chain.add_block([{"from": "bob", "to": "carol", "amount": 2}])
    chain.add_block([{"from": "carol", "to": "dave", "amount": 7}])
    print()
    for block in chain.chain:
        print(f"Block {block.index}:")
        print(f"  hash:          {block.hash}")
        print(f"  previous_hash: {block.previous_hash}")
        print(f"  nonce:         {block.nonce}")
        print(f"  transactions:  {block.transactions}")
        print()
    print("Chain valid?", chain.is_valid())
