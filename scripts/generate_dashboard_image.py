#!/usr/bin/env python3
"""
Generate a branded dashboard poster image for Micro Quant using OpenAI Images API.

Requirements:
  - OPENAI_API_KEY in environment (loads from .env if present)
  - pip install openai (already in requirements.txt)

Outputs:
  - static/exports/micro_quant_poster.png (and prints the path)
"""
from __future__ import annotations

import os
import base64
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

try:
    from openai import OpenAI  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"OpenAI SDK not available: {exc}")


PROMPT = (
    "Design a clean, modern trading dashboard poster named 'Micro Quant' in a bright,\n"
    "crisp UI style (light theme, subtle shadows, precise gridlines, high readability).\n\n"
    "Layout:\n"
    "- Header: 'Micro Quant' title on the left, a slim horizontal quotes ticker to the right.\n"
    "- Main grid: left = primary candlestick chart; right = vertical control/insight panel.\n\n"
    "Primary chart (left):\n"
    "- Candlesticks with green up and red down bodies; slim wicks.\n"
    "- Overlays:\n"
    "  • STL trend as a smooth colored line (slightly thicker than indicators).\n"
    "  • Dashed vertical period markers aligned to bars (subtle, non-intrusive).\n"
    "- Indicator chips anchored in the top-left corner of the plot area (not scrolling with data):\n"
    "  • SMA, STL, STLSpeed, RSI, MACD, VOL, ATR, ADX — each a small rounded pill\n"
    "    showing BUY, SELL, or – with green/red/neutral accents.\n"
    "- Sub-panes below the chart: RSI line, MACD histogram/lines, Volume bars, plus ATR and ADX panels.\n\n"
    "Right panel (stacked cards):\n"
    "- News & Intel: compact headlines list with timestamps; sticky header.\n"
    "- Analysis: dropdowns (templates), 'Basic Health Check' and 'Tech Snapshot' buttons;\n"
    "  freshness pills indicating New news / Latest; a 'Tech+AI Check' button.\n"
    "- AI Trade Plan: leverage input and two buttons — AI Buy (green) and AI Sell (red);\n"
    "  below them, show a compact plan preview pill set (Position, SL, TP).\n"
    "- STL controls: 'Auto period' toggle, period input, Show STL speed/accel switches,\n"
    "  'Period lines' toggle; saved runs dropdown.\n"
    "- Strategy: 'SMA Crossover' with Fast/Slow inputs and 'Run Strategy' button; status line.\n"
    "- Positions box: a simple scrollable list with tickets and PnL.\n"
    "- Bottom: a narrow quotes tape (iframe-like) panel.\n\n"
    "Footer/Widgets:\n"
    "- A fixed bottom-center 728×90 affiliate banner (placeholder art, tasteful).\n"
    "- A small dismiss button in the banner corner.\n\n"
    "Branding & visuals:\n"
    "- Accent color: #1976d2; secondary: #607d8b; success: #2ecc71; danger: #e74c3c.\n"
    "- Light background (#f7f9fc), panels with soft borders and gentle drop shadows.\n"
    "- Typography: clean, system-ui; numeric values use tabular figures.\n"
    "- Keep everything readable, balanced, and production-grade — like a real app screenshot,\n"
    "  but as an illustrated poster. No real logos; use generic placeholders for external widgets.\n"
)


def main() -> None:
    load_dotenv(override=True)
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set. Put it in .env or environment.")

    client = OpenAI()

    # Generate a large, crisp image
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=PROMPT,
        size="1536x1024",
        background="opaque",
    )

    image_b64 = resp.data[0].b64_json
    img_bytes = base64.b64decode(image_b64)

    out_dir = Path("static/exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"micro_quant_poster_{ts}.png"
    out_path.write_bytes(img_bytes)
    print(str(out_path))


if __name__ == "__main__":
    main()
