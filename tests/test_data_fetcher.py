import requests
import pandas as pd
from datetime import datetime, timedelta

# NSE requires headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def get_yesterday_banknifty(period_hours=1):
    """
    Fetches BANKNIFTY spot index data for yesterday from NSE API.
    Returns timestamp + close price for last `period_hours` hours.
    """

    url = "https://www.nseindia.com/api/chart-databyindex?index=BankNifty&preopen=true&segmentLink=17"

    session = requests.Session()
    session.headers.update(HEADERS)

    # First hit NSE homepage to set cookies
    session.get("https://www.nseindia.com", headers=HEADERS)

    # Now fetch BankNifty chart data
    res = session.get(url, headers=HEADERS)
    data = res.json()

    # NSE returns candles in format [timestamp, open, high, low, close, volume]
    candles = data["grapthData"]

    # Convert into DataFrame
    df = pd.DataFrame(candles, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Filter only yesterday
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    df = df[df["timestamp"].dt.date == yesterday]

    # Keep only last N hours
    cutoff = df["timestamp"].max() - timedelta(hours=period_hours)
    df = df[df["timestamp"] >= cutoff]

    return df

if __name__ == "__main__":
    df = get_yesterday_banknifty(period_hours=1)
    print(df.head())
