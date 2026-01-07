# Session Summary — SSH, AI-Trader, Intelligent-Trading-Bot, Signals, Trend, Recommendations

This document captures our recent work, outcomes, and artifacts.

## SSH Setup (GitHub)
- Generated key: `~/.ssh/id_codex_cli` (private) and `~/.ssh/id_codex_cli.pub` (public)
- Configured `~/.ssh/config` for GitHub with `IdentityFile ~/.ssh/id_codex_cli` and `IdentitiesOnly yes`
- Verified access: `ssh -T git@github.com` returned success message for user `lachlanchen`

## AI-Trader — Repo Overview
- Entry: `AI-Trader/main.py` dynamically loads `BaseAgent`, iterates enabled models, and runs a per-day loop.
- Agent: `agent/base_agent/base_agent.py` connects to MCP tools (Math, LocalPrices, Search, TradeTools), builds a LangChain agent (`ChatOpenAI`), and runs tool-driven loops until `<FINISH_SIGNAL>`.
- Prompt: `prompts/agent_prompt.py` composes a day-specific system prompt with positions, prices, and STOP signal.
- State/Data: positions under `data/agent_data/<signature>/position/position.jsonl`, logs under `.../log/<date>/log.jsonl`, prices in `data/merged.jsonl`.
- Config: `configs/default_config.json` controls date range, models, and agent settings.
- Artifact created: `references/ai-trader-overview.md` (created under home: `/home/lachlan/references/ai-trader-overview.md`) summarizing architecture, tools, prompt, and run steps.

## Intelligent-Trading-Bot — Logic Analysis
- Modes:
  - Offline (batch): `scripts/` pipeline → download → merge → features → labels → train → predict → signals → output.
  - Online (service): `service/server.py` schedules `main_task` to fetch new data (Binance/MT5), analyze via `Analyzer`, and execute outputs (notifiers/trader).
- Features/Labels/Signals:
  - Generators in `common/generators.py` (TA-Lib, LINEARREG_SLOPE, tsfresh, label generators `highlow2` etc.).
  - ML algorithms in `common/classifiers.py` (lc, gb, svc, nn). Models stored via `common/model_store.py`.
  - Signals via `common/gen_signals.py` (`combine`, `threshold_rule`) to produce buy/sell and trade_score.
- Data collection: `inputs/collector_binance.py` and `inputs/collector_mt5.py`.
- Trading outputs: `outputs/trader_binance.py`, `outputs/trader_mt5.py`; notifications via Telegram notifiers.

## Near‑Realtime Change Detection (Markdown guidance)
- Provided a config-only guide (message) for jump/spike, volatility shift, and reversal detection using:
  - Z‑score spikes, ATR/Bollinger/Keltner breakouts, CUSUM/Page–Hinkley, and optional Kalman innovation.
  - Parameter defaults, gating (volume/ADX), hysteresis/persistence, and validation checklist.

## Trend Detection (Up/Down/Range) — Config Only
- Added doc: `intelligent-trading-bot/docs/trend-detection.md` describing off‑the‑shelf trend classifiers without code changes:
  - ADX+DI, MA slope+ATR, MACD histogram, Aroon, Linear regression slope+R².
  - Recipes using `feature_sets` (talib + LINEARREG_SLOPE) and `signal_sets` (`combine`, `threshold_rule`).
  - Suggested defaults, hysteresis, debounce, and validation tips.

## AI Model for Rough Trend/Direction
- Recommended supervised models already supported (config-only): Logistic Regression (lc), LightGBM (gb), SVC (svc), NN (nn).
- Approach: use `highlow2` (e.g., high_20/low_20) as labels, train models, and combine predicted scores to a single `trade_score` for Up/Down/Range (dead‑zone around 0).
- Unsupervised regimes (e.g., HMM) are possible but require small code additions.

## Most Stable Choice (in this setup)
- Logistic Regression (lc) is the most stable for live intraday streams:
  - Regularized, smooth probability outputs, works well with existing features.
  - Stabilize via dead‑zone thresholds, persistence, hysteresis, and optional ADX gate.
- Runner‑up: LightGBM with strong regularization; more sensitive to drift than lc.

## Curated GitHub Repos (for reference)
- Bots/Frameworks: `freqtrade/freqtrade`, `QuantConnect/Lean`, `tensortrade-org/tensortrade`, `quantopian/zipline`.
- Backtesting: `mementum/backtrader`, `kernc/backtesting.py`.
- Finance ML: `microsoft/qlib`, `hudson-and-thames/mlfinlab`, `AI4Finance-Foundation/FinRL`.
- Time series/CPD: `deepcharles/ruptures`, `facebookresearch/Kats`, `unit8co/darts`.
- Streaming/Drift: `online-ml/river`, `scikit-multiflow/scikit-multiflow`.
- Indicators/Models: `mrjbq7/ta-lib`, `twopirllc/pandas-ta`, `hmmlearn/hmmlearn`, `pykalman/pykalman`.

## Artifacts Created
- SSH: `~/.ssh/id_codex_cli`, `~/.ssh/id_codex_cli.pub`, `~/.ssh/config:1` (GitHub host entry)
- AI-Trader doc: `/home/lachlan/references/ai-trader-overview.md:1`
- Trend detection doc: `intelligent-trading-bot/docs/trend-detection.md:1`

## Next Options
- Want a ready‑to‑paste config block for: (a) jump detection, or (b) trend classification? I can draft it with thresholds tuned for your bar size.
