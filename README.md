# 🚀 Link Hunter & Vuln Runner

**Dual-mode toolkit for recon + triage**

> 🔎 Collect. 🛡️ Scan. ✅ Decide.

| Mode | Script | What it does |
| --- | --- | --- |
| 🔍 Harvest | [linkSearcher.py](linkSearcher.py) | Pulls clean, de-duplicated links from DuckDuckGo, Bing/Edge, Brave, Google, Yahoo, or all engines at once. |
| 🧪 Attack Surface | [VulnerabilityScanner.py](VulnerabilityScanner.py) | Fans out a stack of OSS scanners across your URL list, stores artifacts, and can ping Telegram. |

## ⚡ Quick Start
1) **Install core deps (Python 3.10+):**
```cmd
pip install requests beautifulsoup4 rich openpyxl
```
2) **Have the external tools available:** sqlmap, dalfox, nuclei, commix, XSRFProbe, arjun, dirsearch, waybackurls, gf, XSStrike (update paths inside the scripts if your layout differs).
3) **Optional Telegram alerts:**
```cmd
set TELEGRAM_TOKEN=your_bot_token
set TELEGRAM_CHAT_ID=your_chat_id
```

## 🔎 linkSearcher.py — Harvest Faster
- De-duplicates across pages; supports single-engine or `-e all` aggregation.
- Output file defaults to `links_<engine>.txt` (override with `-o`).

Examples
```cmd
python linkSearcher.py -q "bug bounty" -p 2 -e duckduckgo
python linkSearcher.py -q "python requests" -p 1 -e all
python linkSearcher.py -q "devops" -p 3 -e bing -o links_bing.txt
```

## 🛡️ VulnerabilityScanner.py — Triage in Batches
- Orchestrates SQLi, XSS, LFI/RFI, RCE, CSRF, open redirect, directory traversal, command injection checks via OSS tools.
- Streams progress, saves artifacts, and can ship hits to Telegram.

Setup checklist
- URLs file: one `http...` per line.
- Optional proxies: `proxy.txt`, one per line.
- Templates/binaries: ensure required assets exist (for example nuclei templates under `tools/nuclei-templates`).

Run it
```cmd
python VulnerabilityScanner.py
```
- Pick your URLs file via the dialog.
- Choose threads (default: half your CPU cores).
- Watch the progress bar while scans run in parallel.

Outputs
- `dumps/` per-finding raw data
- `cards.txt` for Luhn-validated card hits
- `sensitive_data.txt` for extracted emails/usernames/password-like tokens/phones/IPs/JWTs/API keys/SSNs
- `dump.xlsx` cumulative summary (appends if present)
- `logs/errors.log` rotating log
- Telegram messages/documents if env vars are set

## ✅ Safety First
Scan only assets you own or have explicit permission to test. Keep tool paths and templates aligned with your environment.

## 👤 Author
Built by [Ahmed-GoCode](https://github.com/Ahmed-GoCode). Contributions and tweaks welcome.
