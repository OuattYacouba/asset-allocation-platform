import pandas as pd
from pathlib import Path

BRONZE_PATH = Path("storage/data/bronze/prices.parquet")
SILVER_PATH = Path("storage/data/silver")
SILVER_PATH.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(BRONZE_PATH)

df_long = df.melt(
    id_vars=["Date", "ingestion_date"],
    var_name="ticker",
    value_name="price"
)

df_long = df_long.sort_values(["ticker", "Date"])
df_long["return"] = df_long.groupby("ticker")["price"].pct_change()

df_long.to_parquet(SILVER_PATH / "prices_clean.parquet")

print("✅ Nettoyage terminé")