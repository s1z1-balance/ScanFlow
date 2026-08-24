# ScanFlow

Fast, modular network reconnaissance and security audit toolkit with an interactive terminal interface.

ScanFlow provides intelligence gathering, port scanning, DNS exploration, and security assessment utilities without complex setup.

---

## Features

- **DNS Records Extractor (`funcs/dtip.py`)** — Resolves complete DNS record sets: A, AAAA, MX, NS, TXT, SOA, CAA, SRV, and more.
- **IP Geolocation & ASN Lookup (`funcs/iplp.py`)** — Queries ISP, organization, country, geographic coordinates, and ASN metadata.
- **ICMP Traceroute (`funcs/tracert.py`)** — Network route tracer with hop latency and reverse DNS resolution.
- **Async TCP Port Scanner (`funcs/pscan.py`)** — High-speed pure Python `asyncio` port scanner with banner grabbing and service detection. Includes Top 100, Top 1000, Full 1-65535, and custom port range presets (no external `nmap` binary required).
- **Subdomain Enumeration (`funcs/subdomains.py`)** — Passive OSINT aggregator (AlienVault OTX, HackerTarget, crt.sh fallback) paired with concurrent DNS validation and active wordlist brute-force.
- **WHOIS Lookup (`funcs/whois.py`)** — Raw socket WHOIS queries for domain registration, expiration, and registrar intelligence.
- **SSL/TLS Certificate Inspector (`funcs/ctls.py`)** — Deep certificate inspection, SAN extraction, expiration countdown, and certificate chain validation.
- **Nmap CLI Wrapper (`funcs/wnmap.py`)** — Wrapper for Nmap vulnerability scripts (`--script vuln`, `-sC`, `-sV`).

---

## Architecture & Controls

- **Interactive TUI** — Formatted tables, status output, and progress indicators powered by `rich`.
- **Fast Navigation** — Press `ESC` at any input prompt inside any module to return immediately to the main menu.
- **Automated Environment** — Automatically creates `.venv` and installs required packages on first launch.

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/s1z1-balance/ScanFlow.git
cd ScanFlow
```

### 2. Run ScanFlow
```bash
python sncflw.py
```
> *Dependencies (`rich`, `requests`, `dnspython`, `cryptography`, `scapy`) will be installed automatically on first run if missing.*

---

## Manual Installation (Optional)

```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python sncflw.py
```