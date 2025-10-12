#!/usr/bin/env python3
"""Quick check that FMP FX news endpoint works."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

if load_dotenv is not None:
    env_path = ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

from app.news_fetcher import fetch_news_sync  # type: ignore


def main() -> int:
    api_key = os.getenv("FMP_API_KEY") or os.getenv("FINANCIAL_MODELING_PREP_KEY")
    if not api_key:
        print("FMP API key not found. Set FMP_API_KEY or FINANCIAL_MODELING_PREP_KEY first.", file=sys.stderr)
        return 1

    symbols = ["XAUUSD", "EURUSD", "USDJPY"]
    data = fetch_news_sync(symbols, limit_per_symbol=5, providers=["fmp"], fmp_key=api_key)
    print(json.dumps(data, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
