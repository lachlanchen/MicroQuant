#!/usr/bin/env python3
"""Probe several Financial Modeling Prep endpoints with the current API key."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

if load_dotenv is not None:
    env_path = ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

API_KEY = os.getenv("FMP_API_KEY") or os.getenv("FINANCIAL_MODELING_PREP_KEY")

ENDPOINTS = {
    "stock_quote": "https://financialmodelingprep.com/api/v3/quote/AAPL",
    "stock_profile": "https://financialmodelingprep.com/api/v3/profile/AAPL",
    "stock_news": "https://financialmodelingprep.com/api/v3/stock_news?tickers=AAPL&limit=3",
    "historical_price": "https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?timeseries=5",
    "ratios": "https://financialmodelingprep.com/api/v3/ratios/AAPL?period=annual",
    "forex_intraday": "https://financialmodelingprep.com/api/v3/historical-chart/1hour/EURUSD",
    "forex_daily": "https://financialmodelingprep.com/api/v3/historical-price-full/FX/EURUSD?serietype=line&timeseries=5",
    "crypto_quote": "https://financialmodelingprep.com/api/v3/quote/BTCUSD",
    "economic_calendar": "https://financialmodelingprep.com/api/v3/economic_calendar?from=2025-10-01&to=2025-10-10",
    "fx_news": "https://financialmodelingprep.com/api/v3/fx/news?symbol=EURUSD&size=3",
}


def main() -> int:
    if not API_KEY:
        print("FMP API key missing. Set FMP_API_KEY or FINANCIAL_MODELING_PREP_KEY.", file=sys.stderr)
        return 1

    report = {}
    with httpx.Client(timeout=10.0) as client:
        for name, base_url in ENDPOINTS.items():
            url = f"{base_url}&apikey={API_KEY}" if "?" in base_url else f"{base_url}?apikey={API_KEY}"
            try:
                resp = client.get(url)
                report[name] = {
                    "status": resp.status_code,
                    "ok": resp.status_code == 200,
                }
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        report[name]["items"] = len(data)
                        report[name]["sample"] = data[:1]
                    elif isinstance(data, dict):
                        report[name]["keys"] = list(data.keys())[:5]
                        report[name]["sample"] = data
                else:
                    report[name]["body"] = resp.text[:200]
            except Exception as exc:
                report[name] = {"ok": False, "error": str(exc)}

    json.dump(report, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
