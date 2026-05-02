# 🔍 LostCryptoHunter — Simulated

**A Python-based educational simulation** that demonstrates how BIP39 mnemonic generation and BIP44 hierarchical-deterministic (HD) wallet derivation work under the hood — with a live, color-coded terminal dashboard for Ethereum (ETH) and Litecoin (LTC).

> ⚠️ **This is a simulated / educational project.**
> It generates random wallets and queries their public balances via open blockchain APIs.
> It does **not** crack, brute-force, or gain unauthorized access to any wallet.
> The cryptographic address space is astronomically large — the probability of randomly deriving an existing funded wallet is effectively zero.
> This project exists purely to explore blockchain key derivation and async API querying concepts.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Terminal UI Preview](#-terminal-ui-preview)
- [Output Files](#-output-files)
- [Concepts Demonstrated](#-concepts-demonstrated)
- [Disclaimer](#-disclaimer)
- [Author](#-author)

---

## 🔍 Overview

LostCryptoHunter-Simulated is a command-line tool that continuously generates BIP39 mnemonic phrases, derives their corresponding cryptocurrency wallet addresses via the BIP44 derivation path, and queries their on-chain balances through public blockchain APIs — all displayed in a live, auto-refreshing terminal dashboard.

Two independent scanners are included:

| Script | Coin | Derivation Path | Balance API |
|--------|------|----------------|-------------|
| `eth_console.py` | Ethereum (ETH) | `m/44'/60'/0'/0/0` | Etherscan API |
| `ltc_console.py` | Litecoin (LTC) | `m/44'/2'/0'/0/0` | Etherscan API (configurable) |

---

## ⚙️ How It Works

Each scanner follows the same pipeline on every iteration:

```
1. Generate a random 128-bit BIP39 mnemonic (12 words)
        ↓
2. Derive a 512-bit seed from the mnemonic (PBKDF2-HMAC-SHA512)
        ↓
3. Build the BIP32 HD root key from the seed
        ↓
4. Traverse the BIP44 derivation path to the first account address
        ↓
5. Query the address balance via a public blockchain API (async HTTP)
        ↓
6. Log the result to the terminal dashboard
        ↓
7. If balance > 0 → append to output file and flag as FOUND
```

The entire scan loop runs asynchronously using Python's `asyncio` and `aiohttp`, allowing non-blocking HTTP requests while the terminal UI stays responsive.

---

##  Features

- **Live Terminal Dashboard** — A color-coded, ANSI escape-code-driven UI that updates in place without scrolling, displaying a running count of wallets scanned, wallets found, and total balance accumulated
- **BIP39 Mnemonic Generation** — Uses the `mnemonic` library to generate cryptographically standard 12-word seed phrases
- **BIP44 HD Wallet Derivation** — Derives wallet addresses using the correct coin-type paths (`60'` for ETH, `2'` for LTC) via `bip32utils`
- **Async HTTP Queries** — Balances are fetched concurrently with `aiohttp`, keeping the scan loop fast and non-blocking
- **Rolling Log Buffer** — The last 25 log entries are shown in the terminal, with older entries rolling off cleanly
- **Auto-save on Hit** — Any address with a non-zero balance is immediately written to `eth_active.txt` with a timestamp, mnemonic, address, and balance
- **Graceful Shutdown** — `Ctrl+C` cleanly stops the scan loop and prints a stop message
- **Inactivity Check** — Includes a `check_inactive()` helper that flags addresses whose last on-chain transaction was over 365 days ago

---

## 📁 Project Structure

```
LostCryptoHunter-Simulated/
│
├── eth_console.py      # Ethereum scanner — BIP44 m/44'/60'/0'/0/0
├── ltc_console.py      # Litecoin scanner — BIP44 m/44'/2'/0'/0/0
│
└── eth_active.txt      # Auto-created at runtime; stores any non-zero hits
```

---

## 🧰 Prerequisites

- Python 3.8 or higher
- pip

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/mdavidjeremiah/LostCryptoHunter-Simulated.git
cd LostCryptoHunter-Simulated

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install mnemonic bip32utils aiohttp colorama
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `mnemonic` | BIP39 mnemonic phrase generation and seed derivation |
| `bip32utils` | BIP32 HD key tree construction and BIP44 path traversal |
| `aiohttp` | Async HTTP client for non-blocking balance API calls |
| `colorama` | Cross-platform ANSI color support for the terminal UI |

---

## 🖥️ Usage

**Run the Ethereum scanner:**
```bash
python eth_console.py
```

**Run the Litecoin scanner:**
```bash
python ltc_console.py
```

Stop either scanner at any time with `Ctrl+C`. The terminal will print a clean stop message and exit.

> **Note:** The Etherscan API has rate limits on its free tier. The scanner includes a `1.2s` delay between requests to stay within limits. You can swap in your own Etherscan API key in the `api_key` field inside `EthScanner.__init__()` for higher throughput.

---

## 🖼️ Terminal UI Preview

```
 | ETH Scanner | Scanned: 142 | Found: 0 | Balance: 0.000000 ETH |
────────────────────────────────────────────────────────────────────────────────

14:23:01 | Checking: 0x4aF3...c91B
14:23:01 | Mnemonic: word1 word2 word3 word4 word5 word6 word7 word8 ...
14:23:02 | Balance: 0.0 ETH
14:23:03 | Checking: 0x8bE2...f44A
14:23:03 | Mnemonic: apple banana cherry ...
14:23:04 | Balance: 0.0 ETH
...
```

The header line updates in-place on every scan cycle. Log lines roll upward, keeping the most recent 25 entries visible at all times.

---

## 📄 Output Files

When a wallet with a non-zero balance is found, it is appended to `eth_active.txt` in the following pipe-delimited format:

```
2026-05-02T14:35:22.418|word1 word2 ... word12|0xAddress|0.053200
```

| Field | Description |
|-------|-------------|
| Timestamp | ISO 8601 datetime of discovery |
| Mnemonic | The 12-word BIP39 seed phrase |
| Address | The derived wallet address |
| Balance | Balance in ETH (6 decimal places) |

---

## 📚 Concepts Demonstrated

This project is a practical hands-on exploration of several blockchain fundamentals:

**BIP39 — Mnemonic Code for Generating Deterministic Keys**
A 12-word phrase encodes 128 bits of entropy. The same phrase always produces the same wallet — this is the human-readable backup standard used by MetaMask, Ledger, Trezor, and virtually every modern crypto wallet.

**BIP32 — Hierarchical Deterministic Wallets**
From a single root seed, an entire tree of key pairs can be derived deterministically. Child keys are derived from parent keys using HMAC-SHA512, enabling one backup phrase to secure millions of addresses.

**BIP44 — Multi-Account Hierarchy for Deterministic Wallets**
Standardises the derivation path as `m / purpose' / coin_type' / account' / change / address_index`. Coin type `60'` is reserved for Ethereum; `2'` for Litecoin. This ensures interoperability across wallets and tools.

**Async I/O with asyncio + aiohttp**
The scan loop uses Python's native async/await model. HTTP requests to the balance API are non-blocking, so the UI can update and log entries can be written while awaiting a network response.

---

## ⚠️ Disclaimer

This project is created strictly for **educational and research purposes** to demonstrate how cryptocurrency wallet key derivation works at a technical level.

- It does **not** exploit any vulnerability or weakness in any blockchain network
- It does **not** attempt to access, control, or transfer funds from any wallet
- Randomly generating mnemonics and checking their public on-chain balance is **not illegal** — public blockchain data is openly queryable by design
- The author does **not** condone using this code for any unauthorized, unethical, or illegal activity
- Running this at scale against mainnet APIs without permission may violate the API provider's terms of service

Use responsibly. Learn freely.

---

## 👤 Author

**David Jeremiah**
[@mdavidjeremiah](https://github.com/mdavidjeremiah)
Litmus Tech Solutions · Kampala Uganda

---

<div align="center">

Built for learning · © 2026 Litmus Tech Solutions

</div>
