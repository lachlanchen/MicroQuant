#!/usr/bin/env python3
"""Simple CLI to fetch recent news for MetaTrader symbols."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.news_fetcher import fetch_quant_digest, fetch_news_sync, get_quant_symbols  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch macro/FX news for MetaTrader symbols")
    parser.add_argument("symbols", nargs="*", help="Symbols like EURUSD XAUUSD (defaults to preset)")
    parser.add_argument("--preset", choices=["core", "quant", "all"], default="core", help="Preset symbol basket when no symbols specified")
    parser.add_argument("--limit", type=int, default=10, help="Articles per symbol")
    parser.add_argument(
        "--providers",
        nargs="*",
        choices=["newsapi", "fmp", "alphavantage"],
        help="Restrict to specific providers",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of pretty text")
    parser.add_argument("--quant", action="store_true", help="Shortcut to fetch gold + majors basket")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.quant and not args.symbols:
        data = fetch_quant_digest(limit_per_symbol=args.limit, providers=args.providers)
    else:
        preset = "quant" if args.quant else args.preset
        data = fetch_news_sync(
            args.symbols,
            preset=preset,
            limit_per_symbol=args.limit,
            providers=args.providers,
        )

    if args.json:
        json.dump(data, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        for symbol, articles in data.items():
            print(f"=== {symbol} ({len(articles)} articles) ===")
            for art in articles:
                published = art.get("published_at", "")
                print(f"- [{published}] {art.get('headline', '')}")
                summary = art.get("summary")
                if summary:
                    print(f"  Summary: {summary}")
                print(f"  Source: {art.get('source', '')}")
                print(f"  Provider: {art.get('provider', '')}")
                print(f"  URL: {art.get('url', '')}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
