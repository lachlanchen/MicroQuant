MetaTrader Project — Agents Guide

Scope
- This file applies to the entire repository.

Commit/Push Etiquette
- Always commit and push after making functional changes.
- Use concise commit messages that describe intent and scope.
- Prefer small, focused patches over sweeping refactors.

Frontend Chart Sync (Lightweight Charts + indicators)
- Source of truth: use logical-range sync only. Do not mirror time ranges.
- Debounce range propagation (requestAnimationFrame) to avoid oscillation.
- One-time fit: call `fitContent()` only on the first render per symbol/TF.
- Gate sync: keep `lwSubscriptionsEnabled = false` during context switches (symbol/TF/chart type); enable after first data render.
- Avoid repeated auto-fit or programmatic range changes during refresh flows.
- Only apply Chart.js viewport constraints when the line chart is active.

STL Overlay
- Trend line color must not conflict with Bollinger bands.
- Show period bands with dashed boundaries and alternating shaded background.
- Support both auto period and manual period; manual period should be a run parameter.

News AI
- Requires a valid provider key in `.env` (e.g., `OPENAI_API_KEY` or configured MixedAI provider).
- If unavailable, UI must degrade gracefully and clearly communicate the disabled state.

Volume Data
- FX symbols often provide `tick_volume`. Prefer `real_volume`, then `tick_volume`, then `volume` as a fallback.
- Ensure Market Watch visibility in MT5 so volume populates.

General Coding Guidelines
- Favor simple, readable code; avoid premature abstraction.
- Don’t reintroduce startup jitter. Never call `fitContent()` on every refresh.
- Guard nullable ranges (`getVisibleRange()`/`getVisibleLogicalRange()` can be null).
- Beware Windows line endings (CRLF). Keep files UTF‑8; let Git normalize.

Local Run
- Start the server: `python -m app.server`
- Configure `.env` from `.env.example` as needed.

