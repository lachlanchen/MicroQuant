# MT4 vs MT5 for Quantitative Trading on Ubuntu

Summary: Choose MT5 for new quantitative development on Ubuntu. Keep MT4 only if your broker or legacy EAs require it.

## Why MT5 is better for quant

- Strategy Tester: 64‑bit, multi‑threaded, tick‑by‑tick, forward + genetic optimization, and MQL5 Cloud Network. MT4 is single‑threaded and far more limited.
- Python Integration: Official `MetaTrader5` Python package for data/trading via a running MT5 terminal. MT4 has no official Python API.
- Language & Libraries: MQL5 has richer standard library, event model, structures/classes, and more robust order handling. Porting from MQL4 to MQL5 is possible but not automatic.
- Markets & Data: MT5 is multi‑asset (FX, stocks, futures) with more timeframes, Depth of Market, and better tick history handling.
- Ongoing Support: MT5 is actively enhanced; MT4 is maintenance‑only. Ecosystem momentum favors MT5.

## When to keep MT4 around

- Broker constraint: Your broker only offers MT4 accounts or required symbols.
- Legacy code: You rely on production EAs/indicators written for MQL4.
- Marketplace items: Purchased tools available only for MT4.

## Ubuntu (Wine) considerations

- Both MT4/MT5 run under Wine (your `mt4ubuntu.sh` / `mt5linux.sh` scripts set this up). MT5 generally runs smoothly; install location depends on the script.
- Python API requires MT5 (not MT4). You may need to pass the terminal path to `MetaTrader5.initialize()` when on Linux/Wine.
- File I/O paths inside MQL refer to the terminal’s Wine prefix (e.g., drive_c). Use `TerminalInfoString(TERMINAL_DATA_PATH)` to locate folders at runtime.

## Recommended approach

1) Use MT5 for research, backtesting, and new EAs/indicators.
2) Use Python (`MetaTrader5` + `pandas/numpy`) for data handling, feature engineering, model inference, and orchestration.
3) Execute trades via either:
   - MQL5 EA reading your model’s signals; or
   - Directly through Python’s `MetaTrader5` API (terminal must be running/logged in).
4) Keep MT4 installed only if you must support legacy/broker constraints.

## Minimal project layout suggestion

```
metatrader_qt/
  references/
    mt4_vs_mt5.md
    mt5_python_setup_ubuntu.md
  research/
    notebooks/
  strategies/
    mql5/
    python/
```
