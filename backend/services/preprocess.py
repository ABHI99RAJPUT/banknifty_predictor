import pandas as pd
import ta
from datetime import datetime
from .data_fetcher import get_data_for_date

MARKET_START = "09:15"
MARKET_END = "15:30"

def preprocess_data(date: datetime, interval="1m"):
    """
    Fetch BankNifty data, keep Close + indicators,
    filter market hours, and add Target column as next % change.
    """
    df = get_data_for_date(date, interval=interval)

    if df.empty:
        print(f"⚠️ No data for {date.date()} with interval={interval}")
        return pd.DataFrame()  # return empty DF instead of raising

    # Filter market hours (safely)
    if df.index.min().time() > pd.to_datetime(MARKET_END).time() or \
       df.index.max().time() < pd.to_datetime(MARKET_START).time():
        print(f"⚠️ Market hours missing for {date.date()}")
        return pd.DataFrame()

    df = df.between_time(MARKET_START, MARKET_END)

    if df.empty:
        print(f"⚠️ Empty after market hours filter for {date.date()}")
        return pd.DataFrame()

    df = df[["Close"]].copy()
    close = df["Close"].squeeze()

    # Technical indicators
    df["SMA_5"] = ta.trend.sma_indicator(close, window=5)
    df["SMA_10"] = ta.trend.sma_indicator(close, window=10)
    df["RSI"] = ta.momentum.rsi(close, window=14)
    df["MACD"] = ta.trend.macd_diff(close)

    df.dropna(inplace=True)

    if len(df) < 2:
        # Not enough data to calculate target
        return pd.DataFrame()

    # Target = next % change
    df["Target"] = df["Close"].pct_change().shift(-1)
    df = df.iloc[:-1]  # remove last row (no target)

    return df


if __name__ == "__main__":
    date = datetime(2025, 9, 9)
    df = preprocess_data(date, interval="1m")
    print(df.head())
