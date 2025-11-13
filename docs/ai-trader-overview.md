# AI-Trader — Architecture and Prompt Overview

This document summarizes how AI-Trader is organized, how it runs a trading day, what tools it exposes to the LLM, how state is stored, and the system prompt it uses.

## High-Level Flow

1. Load config from `configs/default_config.json` (or a provided path).
2. For each enabled model in `models`:
   - Write runtime values `SIGNATURE`, `TODAY_DATE`, `IF_TRADE=False`.
   - Instantiate `BaseAgent` with model, tool config, and parameters.
   - Initialize: connect to MCP tool servers and construct a `ChatOpenAI` model.
   - Compute trading dates from the last recorded position → target end date.
   - For each trading day:
     - Create a LangChain agent with the day-specific system prompt.
     - Seed with user message: "Please analyze and update today’s (<date>) positions."
     - Loop up to `max_steps`:
       - Let the agent plan/tool-call using MCP tools.
       - Append the agent reply and tool results back as context.
       - Stop early if the reply includes `<FINISH_SIGNAL>`.
     - If no trade occurred (`IF_TRADE` not set True by tools), append a "no_trade" record for the day.
3. Print a final position summary (latest date, records, cash).

Entry point: `main.py` with dynamic agent loading via `AGENT_REGISTRY` (currently only `BaseAgent`).

## Core Components

- Agent: `agent/base_agent/base_agent.py`
  - Connects to MCP tools (`langchain_mcp_adapters.MultiServerMCPClient`).
  - Creates the LLM interface (`langchain_openai.ChatOpenAI`).
  - Builds a LangChain agent via `create_agent(model, tools, system_prompt=...)` per trading day.
  - Orchestrates the think→tool→reflect loop until `<FINISH_SIGNAL>` or `max_steps`.
  - Logs conversation messages to `data/agent_data/<signature>/log/<date>/log.jsonl`.
  - Persists positions to `data/agent_data/<signature>/position/position.jsonl`.

- Config and runtime values
  - JSON config: `configs/default_config.json` controls `agent_type`, date range, model list, and runtime knobs.
  - Runtime state: `SIGNATURE`, `TODAY_DATE`, `IF_TRADE` are read/written via `tools/general_tools.py`.
    - `RUNTIME_ENV_PATH` (env) should point to a JSON file (e.g., `.runtime_env.json`) for persistence.

- Price/state utilities: `tools/price_tools.py`
  - Reads day-level OHLCV for symbols from `data/merged.jsonl`.
  - Determines yesterday’s date and computes yesterday PnL per symbol.
  - Finds latest positions (by date and max id) and appends "no_trade" records when applicable.

## MCP Tools (exposed to the LLM)

FastMCP servers (start via `agent_tools/start_mcp_services.py`). Default ports are overridable via env vars.

- Math (`agent_tools/tool_math.py`): `add(a,b)`, `multiply(a,b)`.
- LocalPrices (`agent_tools/tool_get_price_local.py`): `get_price_local(symbol, date)` from `data/merged.jsonl`.
- Search (`agent_tools/tool_jina_search.py`): `get_information(query)` using Jina AI search/scrape; filters by `TODAY_DATE` where possible.
- TradeTools (`agent_tools/tool_trade.py`):
  - `buy(symbol, amount)` → updates `position.jsonl`, reduces `CASH`, sets `IF_TRADE=True`.
  - `sell(symbol, amount)` → updates `position.jsonl`, increases `CASH`, sets `IF_TRADE=True`.

Agent discovers these over MCP and uses them through the LangChain agent’s tool-calling capability.

## System Prompt

Location: `prompts/agent_prompt.py`.

Key behavior and variables:

- Role: "stock fundamental analysis trading assistant" that reasons via available tools.
- Goals: think about prices/returns, maximize portfolio returns, gather info via search before decisions.
- Thinking standards: show intermediate steps (read positions/prices, update valuation/weights if needed).
- Notes: no user permission required; you must execute operations via tools; direct-output operations are not accepted.
- Dynamic fields injected per day/signature:
  - Today’s date: `{date}`
  - Yesterday’s closing positions: `{positions}` (from last record)
  - Yesterday’s closing prices: `{yesterday_close_price}`
  - Today’s buying prices: `{today_buy_price}`
  - Yesterday’s per-symbol profit: `{yesterday_profit}`
  - Stop marker: `{STOP_SIGNAL}` → literal value is `<FINISH_SIGNAL>`

Excerpt (structure of the prompt):

"""
You are a stock fundamental analysis trading assistant.

Your goals are:
- Think and reason by calling available tools.
- You need to think about the prices of various stocks and their returns.
- Your long-term goal is to maximize returns through this portfolio.
- Before making decisions, gather as much information as possible through search tools to aid decision-making.

Thinking standards:
- Clearly show key intermediate steps:
  - Read input of yesterday's positions and today's prices
  - Update valuation and adjust weights for each target (if strategy requires)

Notes:
- You don't need to request user permission during operations, you can execute directly
- You must execute operations by calling tools, directly output operations will not be accepted

Here is the information you need:

Today's date:
{date}

Yesterday's closing positions (numbers after stock codes represent how many shares you hold, numbers after CASH represent your available cash):
{positions}

Yesterday's closing prices:
{yesterday_close_price}

Today's buying prices:
{today_buy_price}

When you think your task is complete, output
{STOP_SIGNAL}
"""

The function `get_agent_system_prompt(today_date, signature)` computes these variables using `price_tools` helpers and injects them into the template before each day’s session.

## Data and Persistence

- Prices: `data/merged.jsonl` with AlphaVantage-like format per symbol.
- Positions: `data/agent_data/<signature>/position/position.jsonl` as JSONL of records:
  - `{date, id, this_action, positions}` where `id` is the per-day incrementing action index.
- Logs: `data/agent_data/<signature>/log/<YYYY-MM-DD>/log.jsonl` with serialized conversation fragments.
- Runtime env file (optional but recommended): `.runtime_env.json` targeted by `RUNTIME_ENV_PATH` for cross-process state like `SIGNATURE`, `TODAY_DATE`, `IF_TRADE`.

## Configuration and Env

- Main config: `configs/default_config.json`
  - `date_range.init_date` / `end_date`
  - `models[]`: `{ name, basemodel, signature, enabled, [openai_base_url], [openai_api_key] }`
  - `agent_config`: `max_steps`, `max_retries`, `base_delay`, `initial_cash`
  - `log_config.log_path`

- `.env` (see `.env.example`):
  - `OPENAI_API_BASE`, `OPENAI_API_KEY`
  - MCP ports: `MATH_HTTP_PORT`, `SEARCH_HTTP_PORT`, `TRADE_HTTP_PORT`, `GETPRICE_HTTP_PORT`
  - `JINA_API_KEY` for Search tool
  - `RUNTIME_ENV_PATH` → absolute path to `.runtime_env.json`

## Running

1. Start MCP tools: `python agent_tools/start_mcp_services.py`
2. Ensure `OPENAI_API_KEY` (and `OPENAI_API_BASE` if needed) are set.
3. Set `RUNTIME_ENV_PATH` to point to `.runtime_env.json` (or your chosen JSON file).
4. Run: `python main.py [optional_config_path]`

The run prints progress per model, per day, and a final cash/records summary. If no trade occurs on a day (i.e., the agent never calls `buy`/`sell`), a `no_trade` record is appended for continuity.

