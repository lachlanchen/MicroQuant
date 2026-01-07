# Repository Guidelines

## Project Structure & Module Organization
- `app/` — Python backend (e.g., `server.py`, `mt5_client.py`, `strategy.py`, `news_fetcher.py`, `db.py`).
- `templates/index.html` — Frontend UI (Lightweight Charts + Chart.js).
- `scripts/` — Utilities and smoke tests (e.g., `test_mixed_ai.py`, `test_fmp.py`).
- `references/` — Documentation and setup notes.
- `sql/schema.sql` — Database schema.

## Build, Test, and Development Commands
- Create env and install: `python -m venv .venv && .venv\Scripts\activate` (Win) then `pip install -r requirements.txt`.
- Run locally: `python -m app.server` (serves on port 8888).
- Smoke tests: `python scripts/test_mixed_ai.py`, `python scripts/test_fmp.py`.
- Windows helpers: `scripts/run_windows.ps1`, `scripts/setup_windows.ps1`.

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indents, type hints where practical, small focused functions.
- JS/HTML (`templates/index.html`): use `const/let`, camelCase, avoid globals; keep chart logic simple. Use logical‑range sync and a one‑time `fitContent()` per symbol/TF to prevent jitter.
- Commits: imperative mood with area prefix (e.g., `UI: …`, `Server: …`, `References: …`).

## Testing Guidelines
- No formal suite yet; rely on smoke tests and manual UI checks (pan/zoom sync, STL overlay, trading actions, news panel fallback).
- Keep tests targeted to changed behavior; avoid adding slow or flaky tests.
- Run server locally and verify in browser before pushing.

## STL & Period Lines
- Period lines render as dashed overlay on the candlestick chart.
- Toggle via the Period lines switch (default off).
- Avoid marker squares/text on LW charts; use the overlay only.

## Commit & Pull Request Guidelines
- Small, scoped patches; explain motivation and user impact.
- Include screenshots/GIFs for UI changes; link issues where applicable.
- Avoid unrelated formatting churn; keep diffs minimal and readable.

## Security & Configuration Tips
- Configure `.env` (e.g., `OPENAI_API_KEY` or configured provider) and do not commit secrets.
- MT5/volume: prefer `real_volume` → `tick_volume` → `volume`; ensure instruments are visible in MT5 Market Watch.
