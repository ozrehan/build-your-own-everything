# Build Your Own Blockchain

A tiny blockchain in ~90 lines of Python. No dependencies — just the standard library.

## What you'll build

A working blockchain with:

- **Blocks** that hold a list of transactions, a timestamp, the previous block's hash, and a nonce
- **SHA-256 hashing** — every block's identity is the hash of its contents
- **Proof-of-work mining** — sealing a block means finding a nonce so its hash starts with N zero hex characters (difficulty is configurable, default 2)
- **Chain validation** — `is_valid()` recomputes every hash, checks every link, and verifies every block did its proof of work

Run the demo and you'll mine a genesis block plus 3 transaction blocks, then print the whole chain.

## How it works, in plain steps

1. **A block is just data + a hash.** `Block` stores `index`, `timestamp`, `transactions`, `previous_hash`, and `nonce`. `compute_hash()` serializes all of that to canonical JSON (`sort_keys=True` so the encoding is deterministic) and SHA-256 hashes it.
2. **Mining is guessing.** `mine(difficulty)` increments the nonce, rehashes, and repeats until the hash starts with `"0" * difficulty`. Each extra zero makes it ~16x harder — that's the "work" in proof of work.
3. **Blocks link together.** `Blockchain.add_block()` creates a block whose `previous_hash` is the last block's hash, mines it, and appends it. Change any byte of an old block and its hash changes, which breaks the link for every block after it.
4. **Validation redoes everything.** `is_valid()` checks three things per block: the stored hash matches a fresh recomputation (catches tampering), the hash meets the difficulty (catches cheaters who skip mining), and `previous_hash` matches the previous block's hash (catches reordering/splicing).

## How to run

```bash
python3 blockchain.py
```

## How to test

```bash
python3 test_blockchain.py
```

The tests check that a mined block's hash meets the difficulty, that editing a transaction breaks `is_valid()`, that chain links are consistent, and that recomputing a hash *without* re-mining still fails validation.

## Stretch exercises

1. **Transactions with signatures.** Add a fake "signature" field to each transaction and make `is_valid()` reject blocks containing transactions not signed by the sender. (Real chains use public-key crypto; a shared-secret HMAC from `hmac` is a fine toy stand-in.)
2. **Fork choice.** Simulate two miners: let the chain fork into two competing branches, then implement "longest valid chain wins" and a `replace_chain()` method.
3. **Adjustable difficulty.** Retarget the difficulty every N blocks so blocks arrive at a steady pace — measure actual mining time per block and nudge difficulty up or down, like Bitcoin does every 2016 blocks.

## Further reading

- Bitcoin whitepaper — https://bitcoin.org/bitcoin.pdf (the original, only 9 pages)
- "Blockchain demo" visualizer — https://andersbrownworth.com/blockchain/ (watch hashes, nonces, and tampering live)
- Naivecoin tutorial — https://lhartikk.github.io/ (a minimal blockchain built up step by step in code)
