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
