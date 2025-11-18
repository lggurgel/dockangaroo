# 🦘 Bitcoin Puzzle Solver - Kangaroo Edition

<div align="center">

**A high-performance, distributed Bitcoin puzzle solver using Pollard's Kangaroo algorithm**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Algorithm](https://img.shields.io/badge/Algorithm-Pollard's%20Kangaroo-orange.svg)](https://en.wikipedia.org/wiki/Pollard%27s_kangaroo_algorithm)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 💰 Support This Project

<div align="center">

**If this solver helps you find a key, consider donating!**

Building and maintaining this solver takes significant time and computational resources.
Your support helps keep this project alive and improving.

### Bitcoin Donation Address

```
bc1qwh9k7rlkgj0qfw8wgvqmj86h5m5ddphph2lzg3af0x5p5h9s6qms7a6aqp
```

<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=bitcoin:bc1qwh9k7rlkgj0qfw8wgvqmj86h5m5ddphph2lzg3af0x5p5h9s6qms7a6aqp" alt="Bitcoin Donation QR Code" width="200"/>

**Every satoshi counts! Thank you for your support! 🙏**

</div>

---

## 🎯 What Is This?

This is a **battle-tested Bitcoin puzzle solver** that uses the industry-standard **Pollard's Kangaroo algorithm** (also known as the Lambda method for ECDLP). It has been **validated against successfully solved puzzles** to ensure correctness.

### Why Is Finding Keys So Hard?

Bitcoin's security relies on the **Elliptic Curve Discrete Logarithm Problem (ECDLP)**, which is computationally infeasible to solve for large key spaces. Here's the reality:

- **Puzzle 66** (solved): Search space of ~73 quintillion keys - took **massive distributed effort**
- **Puzzle 135** (unsolved): Search space of **~22 million trillion trillion trillion keys** 😱
- **At 1 million keys/sec**: Would take approximately **6.9 × 10²⁶ years** (longer than the universe's age!)

**But here's the thing**: Someone will eventually find it through distributed efforts, vulnerability discovery, or pure cosmic luck. This solver gives you a fighting chance!

### Why This Solver Is Special

- ✅ **Proven Algorithm**: Uses Pollard's Kangaroo - the same method used to solve Puzzle 66 and others
- ✅ **Battle-Tested**: Code validated against previously solved puzzles
- ✅ **Optimized**: ~2⁶⁷ times faster than brute force
- ✅ **Production-Ready**: Checkpoint system ensures you never lose progress
- ✅ **Docker-Based**: Run anywhere - Mac, Linux, Windows, Cloud
- ✅ **Fully Configurable**: Single config file controls everything

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (Docker Desktop for Mac/Windows, or Docker Engine for Linux)
- **8+ CPU cores** recommended (more = faster)
- **16GB+ RAM** recommended (32GB+ for optimal performance)

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/lggurgel/dockangaroo.git
cd dockangaroo

# Edit configuration (optional - defaults work for Puzzle 135)
nano config.env
```

### 2. Start Solving

```bash
# Build and start all workers
docker-compose up -d --build

# Monitor progress in real-time
python3 kangaroo_monitor.py
```

### 3. Check Progress Anytime

```bash
# View worker status
python3 stats.py

# View Docker logs
docker-compose logs -f
```

### 4. Stop When Needed

```bash
# Stop all workers (progress is automatically saved)
docker-compose down
```

**That's it!** The solver will automatically:
- Save progress every 60 seconds
- Resume from the last checkpoint when restarted
- Alert you if a solution is found
- Store the solution in `results/SOLUTION.txt`

---

## ⚙️ Configuration

All settings are in **`config.env`** - no code changes needed!

### Essential Settings

```bash
# Which puzzle to solve (1-160)
PUZZLE_NUMBER=135

# Target public key (get from https://privatekeys.pw/puzzles/bitcoin-puzzle-tx)
TARGET_PUBLIC_KEY=02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16

# Number of parallel workers
NUM_WORKERS=10

# CPU cores per worker (adjust for your system)
CPUS_PER_WORKER=1.0
```

### Performance Tuning

**For 8-core CPU:**
```bash
NUM_WORKERS=8
CPUS_PER_WORKER=1.0
```

**For 16-core CPU:**
```bash
NUM_WORKERS=10
CPUS_PER_WORKER=1.6
```

**For Cloud/GPU (Advanced):**
```bash
GPU_ENABLED=1
GPU_DEVICE=0
```

See `config.env` for all available options.

---

## 📊 How It Works

### Pollard's Kangaroo Algorithm

Unlike brute force (which tries every key sequentially), Kangaroo uses a "meet in the middle" approach:

1. **Tame Kangaroos** start from known positions and "hop" through the key space
2. **Wild Kangaroos** start from random positions and hop randomly
3. When kangaroos collide at a **Distinguished Point**, we can calculate the private key
4. This reduces complexity from **O(N)** to **O(√N)** - making it ~2⁶⁷ times faster!

### Visual Analogy

```
Brute Force:  Try every key → → → → → → → (2^135 tries)
Kangaroo:     Tame → → → ↘
                          ↘ COLLISION! ← ← ← Wild  (√2^135 = 2^67.5 tries)
```

### Architecture

```
┌─────────────┐
│ config.env  │  ← All settings in one place
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│     docker-compose.yml              │
│  ┌────────┐ ┌────────┐ ┌────────┐   │
│  │Worker 0│ │Worker 1│ │ ... N  │   │  ← Parallel workers
│  └───┬────┘ └───┬────┘ └───┬────┘   │
└──────┼──────────┼──────────┼────────┘
       │          │          │
       ↓          ↓          ↓
┌──────────────────────────────────────┐
│    Jean-Luc Pons' Kangaroo (C++)     │  ← Core algorithm
└──────────────────────────────────────┘
       │          │          │
       ↓          ↓          ↓
┌──────────────────────────────────────┐
│   kangaroo_work/ (checkpoints)       │  ← Progress saved here
│   results/       (solutions)         │  ← Solutions saved here
└──────────────────────────────────────┘
```

---

## 📈 Monitoring & Management

### Real-Time Monitoring

```bash
# Live dashboard with statistics
python3 kangaroo_monitor.py
```

Output example:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bitcoin Puzzle 135 - Kangaroo Solver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: 02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16
Workers: 10/10 active
Uptime: 2h 15m

Worker   Status      Operations      DPs Found    Last Update
────────────────────────────────────────────────────────────
W-0      ● Running   1,234,567,890   4,567        2s ago
W-1      ● Running   1,234,555,123   4,563        1s ago
...
```

### Viewing Statistics

```bash
# Quick statistics
python3 stats.py

# View specific worker logs
docker logs btc_kangaroo_worker_0

# Follow all logs
docker-compose logs -f
```

### Managing Progress

```bash
# Backup your progress
tar -czf backup-$(date +%Y%m%d).tar.gz kangaroo_work/ distinguished_points/

# Reset and start fresh (caution!)
rm -rf kangaroo_work/* distinguished_points/*
docker-compose restart
```

---

## 🎲 Performance & Expectations

### Speed Estimates

| System | Workers | Est. Speed | Time to Search Full Puzzle 135 |
|--------|---------|------------|--------------------------------|
| 8-core CPU | 8 | ~800k ops/sec | 8.6 × 10²⁶ years |
| 16-core CPU | 16 | ~1.6M ops/sec | 4.3 × 10²⁶ years |
| Cloud (48-core) | 48 | ~4.8M ops/sec | 1.4 × 10²⁶ years |
| GPU (NVIDIA 3090) | N/A | ~50M ops/sec* | 1.4 × 10²⁵ years |

*GPU performance depends on implementation and optimization

### Reality Check

**Solving Puzzle 135 solo is statistically impossible.** However:

- ✅ **Educational Value**: Learn Bitcoin cryptography and optimization
- ✅ **Luck Factor**: Someone has to find it!
- ✅ **Smaller Puzzles**: Try Puzzle 66-70 for realistic chances
- ✅ **Distributed Effort**: Run on multiple machines/cloud
- ✅ **Future Optimizations**: Quantum computing, vulnerabilities, etc.

**Think of it like mining**: You're unlikely to find a Bitcoin block solo, but someone always does!

---

## 🔐 Security & Safety

### What Happens If You Find The Key?

1. **🎉 Congratulations!** You've won the cosmic lottery
2. **🔒 Secure it immediately** - the private key is in `results/SOLUTION.txt`
3. **💰 Claim the reward** - import the key into a wallet and transfer the Bitcoin
4. **🙏 Consider donating** - help support this project!

### Security Best Practices

- ✅ **Keep your machine secure** - the private key is valuable
- ✅ **Backup your progress** - don't lose weeks of computation
- ✅ **Don't share work files** - they could reveal your progress
- ✅ **Use testnet first** - test with Puzzle 1-40 to validate setup

---

## 🛠️ Advanced Usage

### Running on Multiple Machines

Split workers across machines for even faster solving:

**Machine 1:**
```bash
# Edit config.env
NUM_WORKERS=10
# Start workers 0-9
docker-compose up -d
```

**Machine 2:**
```bash
# Edit config.env and docker-compose.yml to use workers 10-19
NUM_WORKERS=20  # Total workers across all machines
# Adjust WORKER_ID in docker-compose.yml
docker-compose up -d
```

### Cloud Deployment

Deploy on AWS, GCP, or Azure:

```bash
# 1. Launch a compute instance (e.g., AWS EC2 c5.12xlarge - 48 cores)
# 2. Install Docker
# 3. Clone repo and configure
# 4. Run!
docker-compose up -d --build
```

**Cost estimate**: AWS c5.12xlarge = ~$2/hour = ~$48/day

### GPU Acceleration

For NVIDIA GPUs (requires CUDA setup):

```bash
# Edit config.env
GPU_ENABLED=1

# Use GPU docker-compose
docker-compose -f docker-compose.gpu.yml up -d --build
```

---

## 📚 Technical Details

### Dependencies

- **[Jean-Luc Pons' Kangaroo](https://github.com/JeanLucPons/Kangaroo)** - Core ECDLP solver (C++)
- **[coincurve](https://github.com/ofek/coincurve)** - Fast secp256k1 bindings (Python)
- **Docker** - Containerization and orchestration

### Algorithm Complexity

- **Brute Force**: O(N) = 2¹³⁵ operations
- **Pollard's Kangaroo**: O(√N) = 2⁶⁷·⁵ operations
- **Speedup**: ~2⁶⁷·⁵ times faster (147,000,000,000,000,000,000,000x)

### File Structure

```
dockangaroo/
├── config.env                 # ← All configuration here
├── docker-compose.yml         # Container orchestration
├── Dockerfile.kangaroo        # Docker image definition
├── kangaroo_wrapper.py        # Python wrapper for Kangaroo
├── kangaroo_monitor.py        # Real-time monitoring
├── stats.py                   # Statistics viewer
├── requirements.txt           # Python dependencies
├── kangaroo_work/            # Worker checkpoints (auto-created)
├── distinguished_points/      # DP files (auto-created)
└── results/                   # Solutions (auto-created)
```

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: "docker-compose: command not found"
```bash
# Use docker compose (no hyphen) on Docker v2+
docker compose up -d
```

**Problem**: Containers keep restarting
```bash
# Check logs
docker-compose logs
# Usually caused by incorrect config or missing dependencies
```

### Performance Issues

**Problem**: System is slow/unresponsive
```bash
# Reduce CPU per worker
CPUS_PER_WORKER=0.8  # in config.env

# Or reduce number of workers
NUM_WORKERS=6
```

**Problem**: Out of memory
```bash
# Reduce memory per worker
MEMORY_PER_WORKER=1  # in config.env
```

### Algorithm Issues

**Problem**: No progress after hours
```bash
# This is normal! Kangaroo requires:
# - ~2^67 operations for Puzzle 135
# - At 1M ops/sec = 4.7 × 10^12 years average
#
# For testing, try smaller puzzles (e.g., Puzzle 40)
PUZZLE_NUMBER=40  # Much smaller search space
```

---

## 🤝 Contributing

Found a bug? Have an optimization? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Optimization ideas we'd love to see:**
- GPU kernel improvements
- Better DP merging strategies
- Multi-machine coordination
- Performance monitoring enhancements

---

## 📄 License

This project is provided for **educational and research purposes**.

**Disclaimer**: Solving Bitcoin puzzles requires significant computational resources and has an extremely low probability of success. Use responsibly and at your own risk.

---

## 🙏 Acknowledgments

- **[Jean-Luc Pons](https://github.com/JeanLucPons)** - For the excellent Kangaroo implementation
- **Bitcoin Community** - For creating and maintaining these fascinating puzzles
- **secp256k1 Contributors** - For the robust elliptic curve library
- **You** - For supporting this project!

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/lggurgel/dockangaroo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lggurgel/dockangaroo/discussions)
- **Bitcoin Puzzle Info**: https://privatekeys.pw/puzzles/bitcoin-puzzle-tx

---

## 🌟 Star This Repo!

If you find this project useful, please star it on GitHub! It helps others discover this tool.

---

<div align="center">

**Good luck, and may the cryptographic odds be ever in your favor!** 🍀

*Remember: The real treasure is the knowledge gained along the way*
*(but finding the key would be pretty cool too)*

</div>
