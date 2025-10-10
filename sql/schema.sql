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

-- STL decomposition components cache
CREATE TABLE IF NOT EXISTS stl_components (
    symbol       TEXT NOT NULL,
    timeframe    TEXT NOT NULL,
    period       INTEGER NOT NULL,
    ts           TIMESTAMPTZ NOT NULL,
    close        DOUBLE PRECISION,
    trend        DOUBLE PRECISION,
    seasonal     DOUBLE PRECISION,
    resid        DOUBLE PRECISION,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (symbol, timeframe, period, ts)
);

CREATE INDEX IF NOT EXISTS idx_stl_components_lookup
    ON stl_components(symbol, timeframe, period, created_at DESC, ts DESC);
