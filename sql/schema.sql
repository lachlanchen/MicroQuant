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
