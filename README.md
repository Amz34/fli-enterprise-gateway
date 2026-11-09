# fli Enterprise Gateway & Flight Intelligence Pipeline

[![Architecture: Zero-GDS-Overhead](https://img.shields.io/badge/Architecture-Zero--GDS--Overhead-blue.svg)](https://github.com/aamir1zahran/fli-enterprise-gateway)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Runtime: Python 3.12](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://python.org)

An enterprise-grade, zero-scraping flight intelligence and multi-origin corporate booking gateway built on reverse-engineered Google Flights RPCs and B2B fulfillment aggregators.

---

## ⚡ The Architecture: Solving the Look-to-Book (L2B) Dilemma

Traditional Online Travel Agencies (OTAs) and corporate booking systems suffer from punitive **Look-to-Book (L2B)** penalties when querying legacy GDS systems (Amadeus, Sabre) at scale ($0.01 – $0.03 per search, with 100:1 to 300:1 search-to-booking ratio caps).

**The Two-Tier Decoupled Pattern**:
```
┌────────────────────────────────────────────────────────┐
│         TIER 1: ULTRA-LOW-COST SHOPPING LAYER          │
│                  (fli Core Engine)                     │
│  • Unlimited calendar searches with 0 GDS fees         │
│  • Reverse-engineered Google Flights RPCs (curl-cffi)  │
│  • 60-day calendar matrices computed in <2 seconds     │
│  • Default enterprise currency: SAR (Saudi Riyals)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ (Only triggers on confirmed user checkout)
                            ▼
┌────────────────────────────────────────────────────────┐
│        TIER 2: PRECISION FULFILLMENT LAYER             │
│        (Akbar Travels B2B API / Wholesale GDS)         │
│  • Exactly 1 API call per paying passenger             │
│  • Look-to-Book ratio near 1:1                         │
│  • Automatic net fare deduction & instant PNR issuance │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Capabilities

1. **Zero-Scraping RPC Queries**:
   - Direct Protobuf / Batch RPC interaction with Google Flights endpoints using `curl-cffi` TLS browser impersonation.
   - Bypasses headless Chromium / Selenium overhead (sub-second queries, negligible RAM).

2. **Enterprise Currency Normalization (SAR)**:
   - Built-in enforcement for Middle Eastern and GCC corridors (e.g. `JED`, `RUH`, `DMM` to `DAC`, `CAI`, `LHR`).
   - Automatically passes `curr=SAR` across all search matrices.

3. **Multi-Origin Corporate Sync**:
   - Coordinates flight arrival windows for distributed teams meeting at a single conference hub, optimizing aggregate ticket spend and ground transportation logistics.

---

## 📦 Directory Structure

```
.
├── README.md
├── requirements.txt
├── gateway/
│   ├── __init__.py
│   ├── config.py
│   ├── router.py
│   └── corporate_sync.py
└── scripts/
    └── run_matrix.py
```

---

## 🛠️ Quickstart

### 1. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Multi-Origin Group Corporate Synchronization
```bash
python3 -m gateway.corporate_sync DAC 2027-01-11 2027-01-25 "JED,RUH,DMM" --currency SAR
```

---

## 📄 License
MIT License. Open source and ready for enterprise extension.
