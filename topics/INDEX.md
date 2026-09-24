# Topics Index

200 bite-sized learning guides — what each thing is, how it works inside, and a concrete path to building it yourself. Each guide includes core concepts, build milestones, and verified resources.

## Programming Languages

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [Build Your Own Actor-Model Concurrency](actor-model-concurrency/) | intermediate | The actor model structures concurrent programs as isolated actors that communicate only by sending asynchronous messages — no shared... |
| [Build Your Own Assembler](assembler/) | intermediate | An assembler is the simplest real compiler: it translates human-readable mnemonics like `mov rax, 1` into the exact bytes the CPU executes. |
| [Build Your Own Bytecode Virtual Machine](bytecode-virtual-machine/) | intermediate | A bytecode virtual machine compiles source code to a compact stream of numeric instructions, then executes them with a simple... |
| [Build Your Own DSL](dsl-design/) | intermediate | A domain-specific language trades generality for expressiveness: instead of writing loops and conditionals, users of a DSL write what... |
| [Build Your Own Esoteric Language](esoteric-language/) | beginner | Esoteric languages are programming languages designed as art, jokes, or puzzles — Brainfuck has eight commands, Shakespeare programs... |
| [Build Your Own Formal Grammar (EBNF)](formal-grammars-ebnf/) | beginner | A formal grammar is a precise, checkable definition of what counts as a valid program — every language specification, from XML to Rust,... |
| [Build Your Own JIT Compiler (Basics)](jit-compiler-basics/) | advanced | A just-in-time compiler watches your program run, finds the hot loops, and compiles them to native machine code on the fly — which is... |
| [Build Your Own Lexical Scoping and Closures](lexical-scoping-closures/) | beginner | Lexical scoping means a name refers to whatever was visible where the code was written, not where it happens to run — and a closure is a... |
| [Build Your Own Linker](linker/) | advanced | A linker is the program that turns scattered object files into one runnable executable: it merges sections, assigns final addresses, and... |
| [Build Your Own Macro System](macro-systems/) | advanced | A macro system lets programs write programs: macros transform syntax before (or during) compilation, so you can add language features as... |
| [Build Your Own Mark-Sweep Garbage Collector](mark-sweep-garbage-collector/) | advanced | A mark-sweep garbage collector finds memory your program can no longer reach and reclaims it automatically, so programmers never call... |
| [Build Your Own Memory Allocator](memory-allocator/) | intermediate | Every `malloc` call runs a small, clever algorithm: your memory allocator decides where each block lives, splits and merges free space,... |
| [Build Your Own Package Manager](package-manager/) | intermediate | A package manager is a dependency solver with a network client: it reads version constraints, finds a set of package versions that... |
| [Build Your Own Parser Combinators](parser-combinators/) | intermediate | Parser combinators build parsers out of parsers: tiny functions like `char('(')` and `many(digit)` snap together with combinators like... |
| [Build Your Own Pattern-Matching Engine](pattern-matching-engine/) | advanced | Pattern matching lets you destructure data by shape — matching on lists, trees, and variants — and it's the feature that makes ML-family... |
| [Build Your Own Recursive-Descent Parser](recursive-descent-parser/) | beginner | A recursive-descent parser turns a stream of tokens into a syntax tree using one function per grammar rule — `parseExpression()` calls... |
| [Build Your Own REPL](repl-design/) | beginner | A REPL — read, eval, print, loop — is the fastest feedback loop in programming: type an expression, see the result, keep the state. |
| [Build Your Own Transpiler](transpiler/) | intermediate | A transpiler is a compiler whose target language is another high-level language: TypeScript becomes JavaScript, early C++ became C, and... |
| [Build Your Own Tree-Walking Interpreter](tree-walking-interpreter/) | intermediate | A tree-walking interpreter is the most direct way to make a programming language run: it parses source code into an abstract syntax... |
| [Build Your Own Type Checker](type-checker/) | advanced | A type checker is the part of a compiler that proves your program makes sense before it runs: it walks the syntax tree, assigns a type... |

## Databases

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [B-Tree Index](b-tree-index/) | intermediate | A B-tree is the self-balancing tree structure that lets a database find any row among billions in a handful of disk reads. |
| [Columnar Storage Format](columnar-storage-format/) | intermediate | Columnar formats (Parquet, Arrow) store each column contiguously instead of each row, so an analytical query reading 2 of 50 columns... |
| [Connection Pooler](connection-pooler/) | intermediate | A connection pooler (PgBouncer, Pgpool) sits between your app and the database, multiplexing thousands of cheap client connections onto... |
| [Crash Recovery (ARIES)](crash-recovery-aries/) | advanced | ARIES is the recovery algorithm behind DB2, SQL Server, and Postgres's crash recovery: after a power failure, it replays the write-ahead... |
| [Document Store](document-store/) | intermediate | A document store (MongoDB, CouchDB) keeps data as self-describing JSON-like documents instead of rows, so each record can have a... |
| [Embedded Database](embedded-database/) | intermediate | An embedded database (SQLite, DuckDB) is a full SQL engine that runs inside your process — no server, no network, just a library and a file. |
| [Full-Text Search Index](full-text-search-index/) | intermediate | A full-text index is what turns "find documents containing these words" from a hopeless table scan into a millisecond query — it's the... |
| [Graph Database](graph-database/) | intermediate | A graph database stores entities as nodes and their relationships as first-class edges, so "friends of friends who bought X" is a... |
| [LSM-Tree Storage Engine](lsm-tree-storage/) | advanced | An LSM-tree (Log-Structured Merge-tree) is the storage engine behind Cassandra, RocksDB, and Bigtable: it turns random writes into... |
| [MVCC Transactions](mvcc-transactions/) | advanced | MVCC (Multi-Version Concurrency Control) is how Postgres and friends let readers never block writers: instead of locking rows, every... |
| [Query Planner and Optimizer](query-planner-optimizer/) | advanced | The planner is what makes declarative SQL fast: it turns "give me these rows" into a concrete execution plan — which indexes to use,... |
| [Raft Consensus](raft-consensus/) | advanced | Raft is the algorithm that lets a cluster of machines agree on a single sequence of operations even when some machines fail — it's what... |
| [Read Replicas and Replication](read-replicas-replication/) | intermediate | Replication keeps copies of your data on multiple machines so reads scale out and the database survives a server dying. |
| [Redis-Like Cache](redis-like-cache/) | beginner | A Redis-like cache is an in-memory key/value server speaking the RESP protocol: sub-millisecond reads, rich data structures, and... |
| [Secondary Indexing](secondary-indexing/) | intermediate | Secondary indexes are how a database answers "find by email" without scanning the table: auxiliary structures keyed by non-primary columns. |
| [Sharding Strategy](sharding-strategy/) | advanced | Sharding splits one logical database across many machines so no single node holds all the data or all the traffic. |
| [SQL Parser](sql-parser/) | intermediate | A SQL parser turns the text `SELECT a FROM t WHERE x > 1` into a structured query tree the database can plan and execute. |
| [Time-Series Database](time-series-database/) | intermediate | A time-series database stores timestamped measurements — metrics, sensor readings, stock ticks — and answers "give me the p99 latency... |
| [Vector Database](vector-database/) | advanced | A vector database stores ML embeddings and answers "find the 10 most similar items" over millions of high-dimensional vectors in... |
| [Write-Ahead Log](write-ahead-log/) | intermediate | The write-ahead log (WAL) is the reason a database can promise your data survives a power cut: every change is appended to a sequential... |

## Networking

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [BGP Announcer](bgp-announcer/) | intermediate | BGP is the protocol that stitches the internet together — routers in 70,000+ autonomous systems use it to tell each other which IP... |
| [CDN Edge Cache](cdn-edge-cache/) | intermediate | A CDN puts cached copies of content on servers near users so most requests never reach the origin. |
| [DNS Resolver](dns-resolver/) | intermediate | Every name you type — every `curl`, every API call — starts with a DNS lookup, and almost nobody has seen the actual packets. |
| [gRPC Service](grpc-service/) | beginner | gRPC lets you define an API once in a `.proto` file and get type-safe clients and servers in a dozen languages, with binary... |
| [HTTP Protocol Deep Dive](http-protocol-deep-dive/) | intermediate | HTTP looks simple — text requests, text responses — but the details (persistent connections, chunked encoding, caching, content... |
| [HTTP/2 Framing](http2-framing/) | advanced | HTTP/2 keeps HTTP's semantics but replaces the text wire format with binary frames multiplexed over one connection — the fix for... |
| [Layer-7 Routing](layer7-routing/) | intermediate | A layer-7 router (reverse proxy / ingress) reads the actual HTTP request — host, path, headers — and decides which backend service... |
| [Message Queue](message-queue/) | intermediate | A message queue decouples producers from consumers in time: senders drop messages in and move on; workers pick them up at their own... |
| [NAT Traversal](nat-traversal/) | intermediate | Two machines behind home routers can't just connect to each other — neither has a public address the other can dial. |
| [Packet Sniffer](packet-sniffer/) | intermediate | A packet sniffer captures raw traffic off the wire and decodes it layer by layer — it's tcpdump/Wireshark from scratch. |
| [Port Scanner](port-scanner/) | beginner | A port scanner asks a host "which doors are open?" by probing its TCP and UDP ports and interpreting the replies. |
| [Pub/Sub Broker](pubsub-broker/) | intermediate | A pub/sub broker routes messages by topic: publishers fire into named channels, and every subscriber gets a copy — nobody knows about... |
| [QUIC Basics](quic-basics/) | advanced | QUIC rebuilds TCP+TLS as a user-space protocol on top of UDP: encrypted-by-default, 1-RTT handshakes, and independent streams with no... |
| [Rate Limiter](rate-limiter/) | beginner | A rate limiter decides who gets served and who gets a `429 Too Many Requests` — it's what keeps one abusive client from taking down your... |
| [Service Discovery](service-discovery/) | intermediate | In a world of containers and autoscaling, "where is the payments service?" changes every minute — hardcoded IPs don't survive. |
| [SOCKS Proxy](socks-proxy/) | beginner | SOCKS is the universal TCP (and UDP) relay: a client asks the proxy to "connect me to host:port" and the proxy shuttles bytes, never... |
| [Userspace TCP/IP Stack](tcp-ip-stack-userspace/) | advanced | A userspace TCP/IP stack reimplements the kernel's networking — Ethernet, ARP, IP, ICMP, and TCP — as an ordinary program that reads raw... |
| [TCP Load Balancer](tcp-load-balancer/) | intermediate | A TCP (layer-4) load balancer accepts client connections and spreads them across backend servers without understanding the application... |
| [VPN (WireGuard Basics)](vpn-wireguard-basics/) | intermediate | WireGuard replaced sprawling VPN daemons with ~4,000 lines of principled cryptography: a TUN interface, a 1-RTT Noise handshake, and... |
| [WebSocket Server](websocket-server/) | intermediate | WebSockets upgrade an ordinary HTTP connection into a persistent, bidirectional, message-oriented channel — the foundation of chat apps,... |

## Operating Systems

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [Bootloader](bootloader/) | intermediate | A bootloader is the first software that runs when a computer powers on: it bridges the firmware (BIOS/UEFI) and your operating system,... |
| [chroot Sandbox](chroot-sandbox/) | beginner | `chroot` changes a process's view of the filesystem so `/` points somewhere else — the oldest, simplest Unix sandboxing primitive. |
| [Container Runtime Basics](container-runtime-basics/) | intermediate | A container is not a VM and not magic: it's an ordinary Linux process running with restricted views of the system (namespaces) and... |
| [CPU Scheduler](cpu-scheduler/) | intermediate | A CPU scheduler decides which runnable task gets the CPU and for how long — it is the piece of the kernel that creates the illusion that... |
| [UART Device Driver](device-driver-uart/) | intermediate | A UART (serial port) is the simplest real hardware a kernel can talk to: a few I/O registers that send and receive bytes one at a time. |
| [ELF Loader](elf-loader/) | intermediate | ELF is the binary format of Unix: the loader parses its headers, maps loadable segments into memory with the right permissions, and... |
| [Hypervisor Basics](hypervisor-basics/) | advanced | A hypervisor runs entire virtual machines: it uses CPU virtualization extensions to let a guest OS execute directly on hardware while... |
| [Init System](init-system/) | beginner | PID 1 — the init system — is the first process the kernel starts and the ancestor of everything: it mounts filesystems, launches... |
| [Interrupt Handling](interrupt-handling/) | advanced | Interrupts are how hardware gets the CPU's attention: a device raises a line, the CPU suspends what it's doing and jumps to a handler. |
| [IPC: Pipes and Sockets](ipc-pipes-sockets/) | beginner | Inter-process communication is how separate programs talk: pipes give you a one-way byte stream between parent and child, and sockets... |
| [malloc Implementation](malloc-implementation/) | intermediate | `malloc` turns a raw stretch of memory from the OS into right-sized, reusable blocks for your program — and `free` must recycle them... |
| [Minimal Kernel](minimal-kernel/) | intermediate | A kernel is the privileged core of an operating system that owns the hardware and hands it out to programs. |
| [Page Cache](page-cache/) | intermediate | The page cache is the OS's transparent disk cache: file data lives in RAM in page-sized chunks, so repeated reads never touch the disk... |
| [Real-Time Scheduler](realtime-scheduler/) | advanced | A real-time scheduler doesn't optimize for throughput — it guarantees deadlines: a task that must run every 10ms will, provably, run... |
| [Simple Filesystem](simple-filesystem/) | intermediate | A filesystem turns a dumb array of disk blocks into named files and directories with permissions and persistence. |
| [Syscall Interface](syscall-interface/) | intermediate | System calls are the controlled doorway between user programs and the kernel — the only way a normal program can read files, allocate... |
| [Terminal Emulator](terminal-emulator/) | intermediate | A terminal emulator is the window your shell lives in: it draws a character grid, interprets ANSI escape sequences, and bridges... |
| [Unix Signals](unix-signals/) | beginner | Signals are the kernel's async notification system: numbered messages like SIGTERM, SIGSEGV, and SIGCHLD that interrupt a process to... |
| [Userspace Threads](userspace-threads/) | intermediate | Userspace threads (fibers, coroutines, green threads) are concurrency without the kernel: your library switches between stacks by saving... |
| [Virtual Memory and Paging](virtual-memory-paging/) | advanced | Virtual memory gives every process its own private, contiguous address space while physical RAM is shared underneath — it is the... |

## Web Development

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [CSS Layout Engine](css-layout-engine/) | advanced | A layout engine takes a DOM tree plus CSS rules and computes the exact pixel position and size of every box on the page — the "layout"... |
| [Dev Server with HMR](dev-server-hmr/) | advanced | A dev server serves your app unbundled with Hot Module Replacement: when you save a file, only the changed module is swapped into the... |
| [Form Validation Library](form-validation-library/) | beginner | A form validation library turns declarative rules ("email, required, min 8 chars") into field-level error messages, touched-state... |
| [GraphQL Server](graphql-server/) | intermediate | A GraphQL server exposes a typed schema and executes client-specified queries against it, letting frontends ask for exactly the fields... |
| [Headless CMS](headless-cms/) | intermediate | A headless CMS stores content (posts, pages, products) and serves it through an API instead of rendering web pages itself — the "head"... |
| [i18n System](i18n-system/) | intermediate | An internationalization system separates every user-facing string from code, then renders the right language, plural form, date, and... |
| [JavaScript Bundler](js-bundler/) | intermediate | A bundler resolves your `import` graph starting from entry files, transforms each module, and emits optimized output files the browser... |
| [JWT Authentication](jwt-auth/) | beginner | JSON Web Tokens are signed, self-contained credentials: the server issues a token after login, and the client sends it with each request... |
| [Markdown Renderer](markdown-renderer/) | beginner | A Markdown renderer parses plain-text markup like `bold` and `# Heading` into an AST and then emits HTML. |
| [OAuth2 Provider](oauth2-provider/) | advanced | An OAuth2 provider is the authorization server: it issues tokens that let third-party apps act on a user's behalf without ever seeing... |
| [Installable PWA](pwa-installable/) | beginner | A Progressive Web App is a website that can be installed to a home screen like a native app — with an icon, splash screen, and... |
| [REST API Client](rest-api-client/) | beginner | A REST API client is a wrapper around HTTP that turns endpoints into typed functions with retries, auth headers, caching, and sane error... |
| [Service Worker Offline](service-worker-offline/) | intermediate | A service worker is a script the browser runs in the background, able to intercept every network request from your site and serve cached... |
| [SPA Router](spa-router/) | beginner | A single-page-app router swaps views in the browser without full page reloads, keeping the address bar and back button working like a... |
| [SSR and Hydration](ssr-hydration/) | intermediate | Server-Side Rendering (SSR) means a Node/Deno server runs your UI code and sends fully-formed HTML to the browser, so the page is... |
| [Test Runner Framework](test-runner-framework/) | intermediate | A test runner discovers test files, executes them in isolation, and reports pass/fail with useful diffs — the engine behind Jest,... |
| [Web Components Library](web-components-library/) | beginner | Web Components are the browser's native component model: custom elements, shadow DOM, and templates, working in any framework or none. |
| [WebGL 2D Renderer](webgl-2d-renderer/) | advanced | WebGL gives JavaScript direct access to the GPU: you upload geometry, write shaders, and draw thousands of sprites in a single frame. |
| [WebRTC Video Chat](webrtc-video-chat/) | advanced | WebRTC lets browsers stream audio, video, and data directly to each other with no plugins, using peer-to-peer connections negotiated... |
| [WebSocket Chat App](websocket-chat/) | intermediate | A WebSocket chat app keeps a persistent two-way connection between browser and server so messages arrive instantly, no polling needed. |

## DevOps & Infrastructure

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [Artifact Registry](artifact-registry/) | intermediate | Every `docker pull`, `npm install`, and CI build artifact flows through a registry: a service that stores immutable, content-addressed... |
| [Autoscaler](autoscaler/) | intermediate | Traffic doubles at 9am; your service should double its capacity without a human being paged. |
| [Backup System](backup-system/) | intermediate | Backups are the only feature you can't test in production until you need them — and then they must work perfectly. |
| [Blue-Green Deployer](blue-green-deployer/) | intermediate | Deploying usually means replacing the running version in place and hoping. |
| [Chaos Monkey Lite](chaos-monkey-lite/) | beginner | Netflix's Chaos Monkey randomly kills production servers — on purpose. |
| [CI Runner](ci-runner/) | intermediate | Every push to a Git repo triggers invisible labor: checkout, install dependencies, run tests, build artifacts, deploy. |
| [Compose Alternative](compose-alternative/) | intermediate | `docker compose up` turns a YAML file into a running multi-container application: networks created, volumes mounted, containers started... |
| [Config Management](config-management/) | intermediate | Installing nginx on one server is a command; installing it identically on two hundred, keeping it that way, and knowing when someone... |
| [Container Image Builder](container-image-builder/) | advanced | `docker build` feels like magic: a Dockerfile becomes a portable image you can run anywhere. |
| [Cron Scheduler](cron-scheduler/) | beginner | `0 2    /backup.sh` — five fields that have run the world's batch jobs for forty years. |
| [Distributed Tracer](distributed-tracer/) | advanced | A slow request crosses five services, and each one's logs look fine. |
| [Feature Flag Service](feature-flag-service/) | beginner | Deploying code and releasing a feature are different events — feature flags are what separates them. |
| [Git Server](git-server/) | intermediate | GitHub is, at its core, a Git server with a nice UI: it speaks the Git wire protocols, stores bare repositories, and runs hooks on push. |
| [Mini Terraform (IaC)](iac-mini-terraform/) | intermediate | Infrastructure as Code tools let you declare "I want 3 VMs and a load balancer" in a file and have software make reality match. |
| [Log Aggregator](log-aggregator/) | intermediate | When you have fifty containers on ten machines, `tail -f` stops working. |
| [Metrics Monitor](metrics-monitor/) | intermediate | "Is the site slow, or is it just me?" Metrics monitoring answers that with numbers: a system that scrapes numeric time series (request... |
| [Process Orchestrator](process-orchestrator/) | intermediate | systemd, supervisord, and PM2 all answer one question: how do you keep a set of long-running processes alive, ordered, and observable? |
| [Secrets Vault](secrets-vault/) | intermediate | API keys, database passwords, and TLS private keys can't live in Git and shouldn't live in env files scattered across laptops. |
| [Service Mesh Sidecar](service-mesh-sidecar/) | advanced | In a microservices world, every service needs retries, timeouts, TLS, load balancing, and metrics — and hand-rolling that in ten... |
| [Status Page](status-page/) | beginner | When your service goes down, users don't check your logs — they check your status page. |

## Security

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [Audit Logger](audit-logger/) | beginner | An audit logger records who did what, when — logins, permission changes, data access — in a tamper-evident trail that survives long... |
| [Certificate Authority](certificate-authority/) | advanced | A certificate authority is the trust anchor of the web: it signs certificates that bind a public key to a domain name, letting browsers... |
| [Encrypted Chat](encrypted-chat/) | intermediate | End-to-end encrypted chat means only the two people talking can read the messages — not the server operator, not anyone tapping the wire. |
| [Firewall Basics](firewall-basics/) | beginner | A firewall is a gatekeeper that inspects every packet entering or leaving a machine and decides, rule by rule, whether it may pass. |
| [Fuzzer](fuzzer/) | advanced | A fuzzer feeds a program huge volumes of mutated, unexpected inputs to find crashes — and crashes often mean exploitable memory bugs. |
| [Honeypot](honeypot/) | intermediate | A honeypot is a decoy system — a fake SSH server, a fake login page — that has no legitimate users, so every interaction with it is... |
| [Intrusion Detection](intrusion-detection/) | intermediate | An intrusion detection system watches network traffic or host activity and raises alerts when something looks like an attack. |
| [Malware Analysis Sandbox](malware-analysis-sandbox/) | advanced | A malware analysis sandbox detonates a suspicious file in an isolated virtual machine and records everything it does — files touched,... |
| [Password Hashing](password-hashing/) | intermediate | Storing passwords means never storing the password itself — you store a one-way hash that can verify a login without ever being reversible. |
| [Phishing Simulator (Defensive Training)](phishing-simulator-defensive/) | intermediate | A phishing simulator sends safe, clearly-labeled mock phishing emails to your own organization's users (with written authorization) to... |
| [Sandboxed Code Executor](sandbox-executor/) | advanced | A sandboxed code executor runs untrusted programs — user-submitted code, plugins, build scripts — with strict limits on what they can touch. |
| [Secret Scanner](secret-scanner/) | beginner | A secret scanner hunts through code and git history for accidentally committed credentials — API keys, tokens, private keys — before... |
| [Secure File Shredder](secure-file-shredder/) | beginner | Deleting a file normally just removes its directory entry — the bytes sit on disk until overwritten, recoverable with free forensic tools. |
| [Security Headers Scanner](security-headers-scanner/) | beginner | HTTP security headers are one-line server configurations that switch on browser-side protections against XSS, clickjacking, and... |
| [Steganography Tools](steganography-tools/) | intermediate | Steganography hides the existence of a message — embedding data inside an image or audio file so no one suspects a secret is there at all. |
| [TLS Handshake](tls-handshake/) | advanced | The TLS handshake is the few-millisecond negotiation that turns a raw TCP connection into an authenticated, encrypted channel before any... |
| [TOTP Two-Factor Auth](totp-2fa/) | beginner | TOTP is the six-digit code in your authenticator app that changes every 30 seconds. |
| [VPN Client](vpn-client/) | advanced | A VPN client builds an encrypted tunnel from your device to a trusted endpoint, so traffic crossing hostile networks (coffee-shop Wi-Fi,... |
| [Vulnerability Scanner](vulnerability-scanner/) | intermediate | A vulnerability scanner probes systems you own for known weaknesses — open ports, outdated software, misconfigurations — and reports... |
| [WAF Rules](waf-rules/) | intermediate | A Web Application Firewall sits in front of your app and inspects HTTP requests against a ruleset, blocking SQL injection, XSS, and... |

## AI & Machine Learning

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [ReAct Agent Framework](agent-framework-react/) | intermediate | A ReAct agent loops through Thought → Action → Observation: the LLM reasons about what to do, calls a tool (search, calculator, code... |
| [Autograd Engine](autograd-engine/) | intermediate | An autograd engine records every arithmetic operation as a node in a computation graph, then walks the graph backwards applying the... |
| [CNN Image Classifier](cnn-image-classifier/) | intermediate | A convolutional network learns its own visual features — edges, textures, object parts — by sliding small learned filters across the... |
| [Dataset Pipeline](dataset-pipeline/) | intermediate | A dataset pipeline turns raw files into the shuffled, batched, prefetched tensors training loops consume — and it's where most real ML... |
| [Decision Tree](decision-tree/) | beginner | A decision tree classifies by asking a sequence of yes/no questions about the features — "is income > 50k?", "is age < 30?" — learned... |
| [Embeddings Visualizer](embeddings-visualizer/) | beginner | Word and sentence embeddings place meaning into geometry: similar things end up near each other in a high-dimensional vector space. |
| [LLM Eval Harness](eval-harness-llm/) | intermediate | An eval harness turns "the model feels smarter" into numbers: a set of tasks, a runner that prompts the model, and scorers that grade... |
| [K-Means Clustering](kmeans-clustering/) | beginner | K-means groups data into k clusters by alternating between assigning each point to its nearest centroid and moving each centroid to its... |
| [Model Quantization](model-quantization/) | advanced | Quantization shrinks models by storing weights in fewer bits — 8, 4, even 2 — so a 70B model fits on one GPU instead of four. |
| [Neural Net from Scratch](neural-net-from-scratch/) | beginner | A neural network is just layers of weighted sums followed by nonlinearities, trained by nudging each weight in the direction that... |
| [Optimizer Zoo](optimizer-zoo/) | intermediate | An optimizer is the rule that turns gradients into weight updates — and the differences between SGD, momentum, Adam, and friends are... |
| [PCA from Scratch](pca-from-scratch/) | intermediate | Principal Component Analysis finds the directions in which your data varies the most, letting you compress hundreds of features into a... |
| [Prompt Cache](prompt-cache/) | advanced | Every LLM request reprocesses the entire prompt — but when the prefix is identical across requests (system prompt, few-shot examples,... |
| [Q-Learning Agent](q-learning-agent/) | intermediate | Q-learning teaches an agent to act by trial and error: it maintains a table (or network) estimating the future reward of each action in... |
| [RAG Pipeline](rag-pipeline/) | intermediate | Retrieval-Augmented Generation grounds an LLM's answers in your own documents: chunk the docs, embed them, retrieve the relevant chunks... |
| [Collaborative Recommender](recommender-collaborative/) | intermediate | Collaborative filtering recommends items based on patterns across users: "people who liked what you liked also liked this." Implementing... |
| [RNN Text Generator](rnn-text-generator/) | intermediate | A recurrent network reads text one token at a time, updating a hidden state that acts as memory, and predicts the next token from that... |
| [BPE Tokenizer](tokenizer-bpe/) | intermediate | Byte-Pair Encoding turns raw text into the integer sequences models actually consume: it starts from characters and repeatedly merges... |
| [Transformer from Scratch](transformer-from-scratch/) | advanced | The Transformer replaced recurrence with self-attention: every token directly looks at every other token, weighted by learned relevance. |
| [HNSW Vector Search](vector-search-hnsw/) | advanced | Exact nearest-neighbor search over millions of high-dimensional vectors is too slow for production, so systems use approximate search —... |

## Games & Graphics

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [2D Game Engine](2d-game-engine/) | intermediate | A 2D game engine is the reusable core that sits under a game: a main loop, rendering, input, audio, and scene management. |
| [A* Pathfinding](a-star-pathfinding/) | intermediate | A is the workhorse pathfinding algorithm of games: given a grid or graph, it finds the shortest route from start to goal efficiently. |
| [ASCII Roguelike](ascii-roguelike/) | beginner | An ASCII roguelike is a dungeon crawler rendered entirely in text characters: `@` is you, `g` is a goblin, `#` is a wall. |
| [Audio Synthesizer](audio-synthesizer/) | intermediate | An audio synthesizer generates sound from math: oscillators, filters, and envelopes combine to make everything from chiptune bleeps to... |
| [Chess Engine](chess-engine/) | advanced | A chess engine is a program that plays chess: it represents the board, generates legal moves, and searches millions of positions to pick... |
| [CHIP-8 Emulator](chip8-emulator/) | beginner | CHIP-8 is a tiny interpreted language from the 1970s that ran simple games on 8-bit microcomputers. |
| [Dialogue System](dialogue-system/) | beginner | A dialogue system runs conversations in games: branching lines, player choices, and story state that remembers what you said. |
| [GLSL Shaders Playground](glsl-shaders-playground/) | beginner | A GLSL shaders playground is a live editor where you write fragment shaders and instantly see pixels respond. |
| [Rollback Netcode](netcode-rollback/) | advanced | Rollback netcode makes online fighting and action games feel like offline play: it predicts what remote players will do and rewinds the... |
| [Particle System](particle-system/) | beginner | A particle system creates effects like fire, smoke, sparks, and rain from hundreds of tiny sprites following simple rules. |
| [Physics Engine](physics-engine/) | intermediate | A physics engine simulates how bodies move and collide: gravity pulls, objects bounce, and stacks settle. |
| [Procedural Dungeon Generator](procedural-dungeon-gen/) | intermediate | A procedural dungeon generator creates a fresh, playable level every run — rooms, corridors, doors, and treasure placed by algorithm... |
| [Ray Tracer](ray-tracer/) | intermediate | A ray tracer renders images by simulating light: for every pixel, it shoots a ray into the scene and sees what it hits. |
| [Save System](save-system/) | beginner | A save system preserves a player's progress — position, inventory, quest flags — to disk and restores it later. |
| [Software Rasterizer](software-rasterizer/) | advanced | A software rasterizer draws 3D graphics entirely on the CPU, pixel by pixel, with no GPU help. |
| [Sprite Animation System](sprite-animation/) | beginner | Sprite animation is how 2D characters walk, jump, and attack: a series of frames drawn fast enough to look like motion. |
| [Tilemap Editor](tilemap-editor/) | intermediate | A tilemap editor is the tool level designers use to paint 2D game worlds: pick tiles from a palette and stamp them onto a grid. |
| [Tween Animation System](tween-animation-system/) | beginner | Tweening (in-betweening) animates a value from A to B over time — a menu sliding in, a button popping, a character hopping. |
| [UI Toolkit](ui-toolkit/) | intermediate | A UI toolkit is the widget set behind every menu, HUD, and settings screen: buttons, sliders, text fields, and panels that handle input... |
| [Voxel Engine Basics](voxel-engine-basics/) | advanced | A voxel engine renders worlds made of 3D cubes — Minecraft-style terrain you can dig through and build on. |

## Distributed Systems & Data

| Topic | Difficulty | What you'll learn |
| --- | --- | --- |
| [CQRS Read Models](cqrs-read-models/) | intermediate | The data shape that makes writes safe (normalized, validated, one aggregate at a time) is rarely the shape that makes reads fast... |
| [CRDT Collaborative Text](crdt-collaborative-text/) | advanced | Google Docs lets two people type in the same paragraph with no server arbitrating every keystroke. |
| [Dashboard Metrics](dashboard-metrics/) | beginner | "How many requests per second are we serving, and is the p99 latency okay?" Every production system answers this with metrics: numbers... |
| [Data Lake Layout](data-lake-layout/) | intermediate | Dump raw files into cloud storage and you have a data swamp; organize them with partitions, formats, and table metadata and you have a... |
| [Kademlia DHT](dht-kademlia/) | advanced | A distributed hash table lets millions of untrusted peers store and find data with no server — it's how BitTorrent finds peers without a... |
| [Distributed Lock](distributed-lock/) | intermediate | When three servers all think they're the one allowed to run the nightly billing job, you need a lock that lives outside any single machine. |
| [ETL Pipeline](etl-pipeline/) | beginner | Raw data is never in the shape you need: APIs return nested JSON, timestamps come in five formats, half the rows are malformed. |
| [Event Sourcing (Bank)](event-sourcing-bank/) | intermediate | A bank ledger never erases a transaction — your balance is just the sum of everything that ever happened. |
| [Exactly-Once Semantics](exactly-once-semantics/) | advanced | "At-most-once" loses data; "at-least-once" duplicates it; "exactly-once" — each record affecting the result precisely once, even across... |
| [Gossip Protocol](gossip-protocol/) | beginner | How does a 1,000-node cluster learn that node 742 just died — without any central registry and without everyone shouting at once? |
| [Leader Election](leader-election/) | advanced | Every distributed system has jobs only one node may do — accept writes, run the scheduler, hold the primary lease. |
| [Mini MapReduce](mapreduce-mini/) | beginner | MapReduce is the programming model that let Google process web-scale data on thousands of unreliable commodity machines. |
| [Merkle Trees](merkle-trees/) | beginner | How do you prove one chunk of a 4GB file is intact without re-downloading the whole thing? |
| [Notification Fanout](notification-fanout/) | intermediate | When a celebrity with 10 million followers posts, the system must create 10 million inbox entries in seconds — without making normal... |
| [OLAP Cube](olap-cube/) | intermediate | "Show me revenue by region, by quarter, by product category — and let me drill from year to month to day." Answering that from raw... |
| [P2P File Sharing](p2p-file-sharing/) | intermediate | BitTorrent moves petabytes daily with no CDN bill: downloaders become uploaders, and the swarm's total bandwidth grows with demand... |
| [Schema Registry](schema-registry/) | intermediate | In a system with fifty services producing events, who stops someone from renaming `user_id` to `userId` and breaking every consumer? |
| [Search Ranking (TF-IDF)](search-ranking-tfidf/) | beginner | Type "jaguar" into a search box and the car should beat the animal — if that's what the corpus suggests. |
| [Stream Processor](stream-processor/) | intermediate | Batch jobs answer questions about yesterday; stream processors answer questions about right now — fraud detection, live dashboards,... |
| [Workflow Engine](workflow-engine/) | advanced | "Charge the card, then book the flight, then email the ticket — and if step 2 fails after step 1 succeeded, refund." Multi-step... |

