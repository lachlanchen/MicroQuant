#!/usr/bin/env python3
"""Convert static/favicon.png to static/favicon.ico with multiple sizes.

Run: python3 scripts/convert_favicon.py
Output: static/favicon.ico
"""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image  # type: ignore
except Exception as exc:
    raise SystemExit("Pillow not installed. pip install pillow")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "static" / "favicon.png"
    dst = root / "static" / "favicon.ico"
    if not src.exists():
        raise SystemExit(f"Source favicon not found: {src}")
    img = Image.open(src).convert("RGBA")
    sizes = [16, 32, 48, 64, 128]
    icons = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    # Save multiple sizes into one .ico
    icons[0].save(dst, format="ICO", sizes=[(s, s) for s in sizes])
    print(str(dst))


if __name__ == "__main__":
    main()

