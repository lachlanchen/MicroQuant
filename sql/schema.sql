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
