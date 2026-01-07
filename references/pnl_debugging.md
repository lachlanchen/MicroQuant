PnL Rendering and Debugging Notes

- Symptom: PnL chart shows too few points or a flat tail even though MT5 lists more recent deals.
- Root cause: MT5 queries include a small future buffer (default +12h) so newest deals are inserted with timestamps slightly ahead of “now”. The prior DB read‑back used the unbuffered end time, so those just‑inserted rows were not included.
- Fix implemented:
  - Backend now reads from DB with the same future buffer for auto/db sources so the latest deals appear immediately after upsert.
  - Frontend logs and recomputes cumulative PnL from raw deals as a fallback, preferring whichever series is longer.

Configuration
- `MT5_HISTORY_FUTURE_HOURS` (default 12): forward buffer added to both MT5 history queries and DB read‑backs.
- `MT5_HISTORY_BACK_HOURS` (optional): back buffer (defaults to the same value as forward when unset).

Endpoints and UI
- Manual refresh: `/api/account/closed_deals?days=5000&source=auto&debug=1&account=...`
  - With `debug=1`, the server logs head/tail samples for both MT5 and DB.
  - WebSocket event `closed_deals_update` prompts the UI to refresh automatically after sync/purge.
- Filter zero-PnL deals: add `&nonzero=1` to hide rows where `profit+commission+swap==0`.
  - The UI now passes `nonzero=1` by default for PnL so flat segments from zero-profit rows don’t clutter the chart.
- Purge then refetch (UI): “Purge + Refetch” button above the PnL chart removes rows for the selected account and reloads from MT5.

What you’ll see in logs
- Server
  - `[closed_deals debug] mt5 sample=...` — sample rows returned by MT5.
  - `[closed_deals debug] db count after upsert=...` — rows present after upsert.
  - `[closed_deals debug] deals head=... / tail=...` — DB rows used to compute cumulative series.
- Browser console
  - `[PnL] acct=..., deals=..., cum(server)=..., cum(recomp)=...` — sizes of server series and recomputed fallback.
  - `[PnL] deals head=... tail=...` and `[PnL] cum head=... tail=...` — quick samples to verify alignment.

Code References
- Backend
  - `app/server.py:2243` — ClosedDealsHandler; resolves window and source, applies future‑buffered DB reads for `auto`.
  - `app/server.py:2361` — additional debug logs for deals head/tail.
  - `app/server.py:2410` — ClosedDealsSyncHandler; uses future buffer in DB verification listing.
  - `app/mt5_client.py:516` — MT5 close deals retrieval with ±buffer and naive local timestamps.
- Frontend
  - `templates/index.html:1849` — `refreshClosedDealsSeries()` with explicit console logs and client‑side cumulative fallback.

Known behaviors
- With `nonzero=1`, zero-profit rows are hidden; otherwise a flat tail is expected if the last few MT5 deals have zero profit (administrative entries).
- Transfers (symbol='') are currently included (user requested “no filters”). If needed, add a UI toggle to exclude them.

Quick checklist
1) Click “Fetch Closed” — console should report 10/10 (or more) points and show head/tail samples.
2) If DB shows fewer rows than MT5 immediately after a sync, ensure the server was restarted with these changes and the future buffer env is set as desired.
3) If you switch accounts, the UI passes `account=...` to all requests; confirm via logs.
