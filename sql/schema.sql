-- Simple OHLC bars storage
CREATE TABLE IF NOT EXISTS ohlc_bars (
    symbol       TEXT        NOT NULL,
    timeframe    TEXT        NOT NULL,
    ts           TIMESTAMPTZ NOT NULL,
    open         NUMERIC     NOT NULL,
    high         NUMERIC     NOT NULL,
    low          NUMERIC     NOT NULL,
    close        NUMERIC     NOT NULL,
    tick_volume  BIGINT,
    spread       INTEGER,
    real_volume  BIGINT,
    PRIMARY KEY (symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_ohlc_bars_symbol_tf_ts
    ON ohlc_bars(symbol, timeframe, ts DESC);

-- App preferences (simple key/value store) for persisting UI choices
CREATE TABLE IF NOT EXISTS app_prefs (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- STL decomposition metadata + components
CREATE TABLE IF NOT EXISTS stl_runs (
    id          BIGSERIAL PRIMARY KEY,
    symbol      TEXT        NOT NULL,
    timeframe   TEXT        NOT NULL,
    period      INTEGER     NOT NULL,
    start_ts    TIMESTAMPTZ NOT NULL,
    end_ts      TIMESTAMPTZ NOT NULL,
    rows_count  INTEGER     NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stl_runs_symbol_tf_created
    ON stl_runs(symbol, timeframe, created_at DESC);

CREATE TABLE IF NOT EXISTS stl_run_components (
    run_id    BIGINT        NOT NULL REFERENCES stl_runs(id) ON DELETE CASCADE,
    ts        TIMESTAMPTZ   NOT NULL,
    close     DOUBLE PRECISION,
    trend     DOUBLE PRECISION,
    seasonal  DOUBLE PRECISION,
    resid     DOUBLE PRECISION,
    PRIMARY KEY (run_id, ts)
);

CREATE INDEX IF NOT EXISTS idx_stl_run_components_run_ts
    ON stl_run_components(run_id, ts DESC);


-- News articles storage
CREATE TABLE IF NOT EXISTS news_articles (
    id            BIGSERIAL PRIMARY KEY,
    symbol        TEXT        NOT NULL,
    url           TEXT        NOT NULL,
    title         TEXT,
    source        TEXT,
    site          TEXT,
    image         TEXT,
    published_at  TIMESTAMPTZ,
    summary       TEXT,
    body          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, url)
);

CREATE INDEX IF NOT EXISTS idx_news_symbol_published
    ON news_articles(symbol, published_at DESC);
-- Health check runs (LLM-based question answering over news)
CREATE TABLE IF NOT EXISTS health_runs (
    id           BIGSERIAL PRIMARY KEY,
    kind         TEXT        NOT NULL,      -- 'forex_pair' | 'stock'
    symbol       TEXT,                      -- ticker or pair symbol (e.g., EURUSD) when applicable
    base_ccy     TEXT,                      -- for forex_pair
    quote_ccy    TEXT,                      -- for forex_pair
    news_count   INTEGER     NOT NULL,
    news_ids     TEXT[]      NOT NULL,      -- list of identifiers/URLs used
    answers_json JSONB       NOT NULL,      -- {questions:[{id,answer}], score, signal, meta}
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_runs_kind_symbol_created
    ON health_runs(kind, COALESCE(symbol, base_ccy || quote_ccy), created_at DESC);

-- Account balances over time
CREATE TABLE IF NOT EXISTS account_balances (
    user_name    TEXT         NOT NULL,
    account_id   BIGINT       NOT NULL,
    ts           TIMESTAMPTZ  NOT NULL,
    balance      DOUBLE PRECISION NOT NULL,
    equity       DOUBLE PRECISION,
    margin       DOUBLE PRECISION,
    free_margin  DOUBLE PRECISION,
    currency     TEXT,
    PRIMARY KEY (user_name, account_id, ts)
);

CREATE INDEX IF NOT EXISTS idx_account_balances_acct_ts
    ON account_balances(account_id, ts DESC);

-- Closed deals history (persisted from MT5)
CREATE TABLE IF NOT EXISTS closed_deals (
    account_id   BIGINT       NOT NULL,
    deal_id      BIGINT       NOT NULL,
    order_id     BIGINT,
    ts           TIMESTAMPTZ  NOT NULL,
    symbol       TEXT,
    profit       DOUBLE PRECISION,
    commission   DOUBLE PRECISION,
    swap         DOUBLE PRECISION,
    volume       DOUBLE PRECISION,
    entry        INTEGER,
    comment      TEXT,
    PRIMARY KEY (account_id, deal_id)
);

CREATE INDEX IF NOT EXISTS idx_closed_deals_acct_ts
    ON closed_deals(account_id, ts ASC);

-- Signal-triggered trade logs (UI/strategy-originated orders)
CREATE TABLE IF NOT EXISTS signal_trades (
    id         BIGSERIAL     PRIMARY KEY,
    ts         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    symbol     TEXT          NOT NULL,
    timeframe  TEXT,
    action     TEXT          NOT NULL,            -- 'buy' | 'sell'
    strategy   TEXT,                              -- e.g., 'sma_crossover'
    fast       INTEGER,
    slow       INTEGER,
    volume     DOUBLE PRECISION,
    sl         DOUBLE PRECISION,
    tp         DOUBLE PRECISION,
    order_id   BIGINT,                            -- MT5 order id (if any)
    deal_id    BIGINT,                            -- MT5 deal id (if any)
    retcode    INTEGER,
    source     TEXT,                              -- 'panel' | 'topbar' | 'auto'
    reason     TEXT,                              -- signal reason (e.g., 'fast_cross_up')
    result     JSONB                              -- raw broker response or extra metadata
);

CREATE INDEX IF NOT EXISTS idx_signal_trades_sym_tf_ts
    ON signal_trades(symbol, COALESCE(timeframe, ''), ts DESC);
