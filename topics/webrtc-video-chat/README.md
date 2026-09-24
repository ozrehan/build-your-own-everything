---
title: "WebRTC Video Chat"
category: "web-development"
difficulty: "advanced"
tags: [webrtc, video, p2p]
related: [websocket-chat, nat-traversal, service-worker-offline, oauth2-provider]
---

# WebRTC Video Chat

WebRTC lets browsers stream audio, video, and data directly to each other with no plugins, using peer-to-peer connections negotiated through a small signaling server. Building a video chat app — signaling, SDP exchange, ICE, media tracks — teaches real-time networking: NAT traversal, codecs, and why a "serverless" call still needs servers.

## Core concepts

- **Signaling** — WebRTC doesn't define how peers find each other; you build a WebSocket server to relay session descriptions (SDP) and ICE candidates between callers — the only centralized piece.
- **SDP offer/answer** — Session Description Protocol blobs where each peer declares its media capabilities (codecs, resolutions); one side creates an offer, the other answers, converging on a common configuration.
- **ICE and STUN** — Interactive Connectivity Establishment gathers candidate network addresses; STUN servers help a peer discover its public IP:port behind NAT so the other side can reach it.
- **TURN relay** — When direct P2P fails (symmetric NATs, restrictive firewalls), a TURN server relays all media — the reason video calls still work on corporate networks, at the cost of bandwidth.
- **Media tracks and getUserMedia** — `navigator.mediaDevices.getUserMedia()` captures camera/mic as `MediaStreamTrack`s, which are added to the `RTCPeerConnection` and rendered in `<video>` elements.
- **Data channels** — `RTCDataChannel` gives you low-latency SCTP-based messaging over the same peer connection — perfect for chat, file transfer, or game state alongside the call.
- **Congestion control** — WebRTC adapts bitrate to network conditions automatically (via REMB/TWCC feedback); understanding this explains why call quality degrades gracefully instead of freezing.
- **SFU vs MCU vs P2P** — 1:1 calls are pure P2P; group calls need a Selective Forwarding Unit (routes each stream to everyone) or MCU (mixes into one stream) — which is why real apps run media servers.

## How it works

1. Both peers connect to your signaling server (WebSocket) and join the same "room".
2. Caller creates an `RTCPeerConnection`, adds local media tracks, creates an SDP offer, and sends it via signaling; callee answers with its SDP.
3. Both sides exchange ICE candidates through signaling until a direct (or TURN-relayed) path is established; DTLS-SRTP encrypts the media.
4. Remote tracks arrive via the `track` event and play in `<video>` elements; a data channel carries chat messages in parallel.

## Build milestones

1. A signaling server (WebSocket rooms) plus a page that exchanges offers/answers and opens a data channel for text chat — no media yet, working in an evening.
2. Add `getUserMedia` camera/mic and render the remote stream — your first real 1:1 video call.
3. Add a public STUN server config, then deploy your own coturn TURN server and verify calls work across NATs.
4. Add mute/unmute, camera switching, and screen sharing (`getDisplayMedia`).
5. Build a 3+ person room: either mesh P2P or integrate an open-source SFU (LiveKit/mediasoup) and compare.

## Best resources

- [WebRTC API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API) — the complete reference: peer connections, tracks, data channels, with examples.
- [Getting Started — webrtc.org](https://webrtc.org/getting-started/overview) — the official overview from the project itself.
- [RFC 8445 — ICE](https://datatracker.ietf.org/doc/html/rfc8445) — the spec behind NAT traversal; read the overview to understand candidate pairing.
- [WebRTC samples](https://github.com/webrtc/samples) — official working demos for every API piece, from getUserMedia to data channels.
- [PeerJS docs](https://peerjs.com/) — a tiny wrapper that hides SDP/ICE boilerplate; great for prototyping before going raw.

## Stretch ideas

- Build file transfer over data channels with chunking and progress.
- Add end-to-end encrypted chat using inserted SFrame or manual key exchange on top of the data channel.
