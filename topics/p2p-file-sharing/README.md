---
title: "P2P File Sharing"
category: "distributed-data"
difficulty: "intermediate"
tags: [p2p, bittorrent, file-sharing]
related: [dht-kademlia, merkle-trees, nat-traversal]
---

# P2P File Sharing

BitTorrent moves petabytes daily with no CDN bill: downloaders become uploaders, and the swarm's total bandwidth grows with demand instead of collapsing under it. Building a tiny torrent client teaches you piece selection, choking algorithms, and why tit-for-tat keeps a swarm of strangers cooperating.

## Core concepts

- **Torrent descriptor / metainfo** — A small file describing the content: file names, sizes, piece length, and the SHA-1 hash of every piece. The hash list lets you verify each piece independently, so a corrupt peer can't poison your download.
- **Pieces and blocks** — Files are split into pieces (typically 256KB–4MB), each verified by hash; pieces are transferred as smaller blocks (16KB). You can share a piece the moment you have it, long before the whole file arrives.
- **Tracker / peer discovery** — The classic way to find peers: ask a central tracker "who else wants this torrent." Modern clients also use the DHT and peer exchange (PEX) so swarms survive tracker death.
- **Rarest-first piece selection** — Request the pieces fewest peers have. This keeps rare pieces circulating and prevents the "last piece" problem where everyone waits on one peer holding the final chunk.
- **Choking / unchoking** — Each peer uploads to only a few others at a time, preferring those who upload back fastest (tit-for-tat). Periodically it "optimistically unchokes" a random peer, discovering better partners and giving newcomers a chance.
- **Endgame mode** — When only a few blocks remain, request them from everyone simultaneously and cancel duplicates as they arrive — trading a little wasted bandwidth to avoid stalling on one slow peer.
- **Seeding** — A peer with the complete file that only uploads. Swarm health is measured by the seeder-to-leecher ratio; without seeders, rare pieces die and the torrent withers.

## How it works

Your client reads the .torrent metainfo, computes the info-hash, and asks the tracker (or DHT) for peers. It opens TCP connections and performs the BitTorrent handshake: a fixed header containing the info-hash plus your peer ID. Peers exchange bitfields announcing which pieces they have, then your client requests 16KB blocks of the pieces it needs, prioritizing rarest-first, and verifies each completed piece against its SHA-1 before writing it to disk. Meanwhile the choking algorithm runs every 10 seconds: rank peers by their recent upload rate to you, unchoke the top few plus one random optimistic pick, choke the rest. As pieces complete, you announce them with HAVE messages and start serving them to others — every downloader is also an uploader from the first piece on.

## Build milestones

1. Parse a real .torrent file: decode bencoding, extract the info-hash, file list, and piece hashes — verify against a known torrent.
2. Build the peer wire protocol: handshake, bitfield, request/block messages over TCP; connect to a local test peer and download one piece, verifying its SHA-1.
3. Add a multi-peer downloader: fetch the peer list from a tracker (or a local test tracker), download different pieces from different peers in parallel with rarest-first selection.
4. Add uploading and choking: serve pieces you have to other peers, implement tit-for-tat unchoking with optimistic unchoke, and watch two of your clients trade pieces with no seeder present after the initial bootstrap.
5. Impressive end state: share a real file (e.g. a Linux ISO) across 5+ of your clients on different machines, kill the original seeder halfway, and show the swarm completing anyway — then add DHT-based peer discovery so it works with the tracker killed too.

## Best resources

- [BEP 3: The BitTorrent Protocol Specification](http://www.bittorrent.org/beps/bep_0003.html) — The official wire protocol: handshake, message types, and the exact byte layout your client must speak.
- [BitTorrent — Wikipedia](https://en.wikipedia.org/wiki/BitTorrent) — History, the economics of swarms, and how the ecosystem (trackers, DHT, magnet links) fits together.
- [BitTorrent.org](http://www.bittorrent.org/) — Home of the BEP process; BEPs 5 (DHT), 9 (metadata exchange), and 11 (peer exchange) are your roadmap past the basics.
- [libtorrent](https://libtorrent.org/) — The mature C++ implementation; its design docs and source are the best reference when your client misbehaves and you need to see how the pros handle an edge case.

## Stretch ideas

- Add magnet-link support: fetch metainfo from peers via the extension protocol (BEP 9) so you can download with no .torrent file at all.
- Implement a streaming mode that prioritizes pieces in playback order with rarest-first as a fallback, turning your client into a P2P video player.
