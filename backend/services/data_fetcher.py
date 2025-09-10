import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

SYMBOL = "^NSEBANK"  # BankNifty symbol in Yahoo Finance
IST = pytz.timezone("Asia/Kolkata")

def get_data_for_date(date: datetime, interval="1m"):
    """
    Fetch BankNifty data for a specific date and convert to IST timezone.
    """
    start = date
    end = date + timedelta(days=1)

    df = yf.download(SYMBOL, start=start, end=end, interval=interval)

    if df.empty:
        raise ValueError(f"No data fetched for {date.date()}")

    # Handle timezone
    if df.index.tz is None:  
        df.index = df.index.tz_localize("UTC").tz_convert(IST)
    else:  
        df.index = df.index.tz_convert(IST)

    # Keep only rows matching that date in IST
    df = df[df.index.date == date.date()]

    return df


def get_yesterday_data(interval="1m"):
    yesterday = datetime.now(IST) - timedelta(days=1)
    return get_data_for_date(yesterday, interval)


def get_today_data(interval="1m"):
    today = datetime.now(IST)
    return get_data_for_date(today, interval)


if __name__ == "__main__":
    # Example: fetch Monday and Tuesday data
    monday = datetime(2025, 9, 9, tzinfo=IST)   # IST date
    tuesday = datetime(2025, 9, 8, tzinfo=IST)

    df_monday = get_data_for_date(monday, interval="5m")
    df_tuesday = get_data_for_date(tuesday, interval="5m")

    print("Monday Data (IST):", df_monday.head())
    print("\nTuesday Data (IST):", df_tuesday.head())
