import duckdb
from pathlib import Path

SILVER_PATH = "storage/data/silver/prices_clean.parquet"
GOLD_PATH = Path("storage/data/gold")
GOLD_PATH.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

# Charger les données Silver
con.execute(f"""
    CREATE OR REPLACE TABLE prices AS
    SELECT *
    FROM read_parquet('{SILVER_PATH}')
""")

# Calcul KPIs financiers
kpis = con.execute("""
WITH daily AS (
    SELECT
        ticker,
        Date,
        return
    FROM prices
    WHERE return IS NOT NULL
),
stats AS (
    SELECT
        ticker,
        AVG(return) * 252 AS annual_return,
        STDDEV(return) * SQRT(252) AS volatility,
        COUNT(*) AS n_obs
    FROM daily
    GROUP BY ticker
),
cum_returns_table AS (
    -- Étape A : On calcule d'abord le rendement cumulé seul
    SELECT
        ticker,
        Date,
        EXP(SUM(LN(1 + return)) OVER (PARTITION BY ticker ORDER BY Date)) AS cum_return
    FROM daily
),
drawdown_calc AS (
    -- Étape B : On calcule le pic (peak) et le drawdown quotidien
    SELECT
        ticker,
        cum_return,
        MAX(cum_return) OVER (PARTITION BY ticker ORDER BY Date) AS peak
    FROM cum_returns_table
),
drawdown_final AS (
    -- Étape C : On récupère le pire drawdown par ticker
    SELECT
        ticker,
        MIN(cum_return / peak - 1) AS max_drawdown
    FROM drawdown_calc
    GROUP BY ticker
)

SELECT
    s.ticker,
    s.annual_return,
    s.volatility,
    s.annual_return / NULLIF(s.volatility, 0) AS sharpe_ratio, -- NULLIF évite la division par zéro
    d.max_drawdown,
    s.n_obs
FROM stats s
LEFT JOIN drawdown_final d ON s.ticker = d.ticker
""").df()

# Sauvegarde GOLD
kpis.to_parquet(GOLD_PATH / "asset_kpis.parquet")

print("✅ KPIs financiers calculés (Gold)")

import pandas as pd
pd.read_parquet("storage/data/gold/asset_kpis.parquet")