# backend/services/option_selector.py

import numpy as np
import requests
from datetime import datetime
from model import y_pred_percent, df

def fetch_option_chain(symbol="BANKNIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com",
        "Connection": "keep-alive"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # establishes cookies
    resp = session.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def parse_chain(json_data):
    data = json_data['records']['data']
    chain = {}
    for rec in data:
        strike = rec['strikePrice']
        ce_ltp = rec.get('CE', {}).get('lastPrice', None)
        pe_ltp = rec.get('PE', {}).get('lastPrice', None)
        chain[strike] = {"CE": ce_ltp, "PE": pe_ltp}
    return chain

def suggest_option(y_pred_percent, df, budget, horizon=6, threshold=0.05):
    last_preds = y_pred_percent[-horizon:]
    avg_move = np.mean(last_preds)

    current_price = df["Close"].iloc[-1]
    atm_strike = round(current_price / 100) * 100

    if avg_move > threshold:
        option_type = "CE"
    elif avg_move < -threshold:
        option_type = "PE"
    else:
        return {"preds": last_preds.tolist(), "avg_move": float(avg_move),
                "suggestion": f"NO TRADE (ATM {atm_strike})"}

    chain_json = fetch_option_chain("BANKNIFTY")
    chain = parse_chain(chain_json)

    affordable = [(strike, prices[option_type]) for strike, prices in chain.items()
                  if prices[option_type] is not None and prices[option_type] <= budget]

    if not affordable:
        return {"preds": last_preds.tolist(), "avg_move": float(avg_move),
                "suggestion": "NO AFFORDABLE OPTION within budget"}

    best_strike, premium = min(affordable, key=lambda x: abs(x[0] - atm_strike))
    suggestion = f"BUY {option_type} {best_strike} (Premium ~ ₹{premium})"

    return {
        "preds": last_preds.tolist(),
        "avg_move": float(avg_move),
        "strike": int(best_strike),
        "premium": float(premium),
        "suggestion": suggestion
    }

if __name__ == "__main__":
    budget = float(input("Enter your budget in ₹: "))
    result = suggest_option(y_pred_percent, df, budget)
    print("\nPredictions:", result.get("preds"))
    print("Average move:", result.get("avg_move"), "%")
    print("Suggested Action:", result["suggestion"])
