import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("storage/data/bronze")
DATA_PATH.mkdir(parents=True, exist_ok=True)

TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "SPY"]

def fetch_prices(tickers, start="2018-01-01"):
    df = yf.download(tickers, start=start, auto_adjust=True)
    df = df["Close"].reset_index()
    df["ingestion_date"] = datetime.utcnow()
    return df

if __name__ == "__main__":
    df_prices = fetch_prices(TICKERS)
    df_prices.to_parquet(DATA_PATH / "prices.parquet")
    print("✅ Ingestion terminée")
