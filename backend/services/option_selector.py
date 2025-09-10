# backend/services/option_selector.py

import requests
import json
from datetime import datetime
import pytz

NSE_OPTION_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_option_chain():
    """Fetch latest BankNifty option chain from NSE."""
    session = requests.Session()
    session.headers.update(HEADERS)

    resp = session.get(NSE_OPTION_CHAIN_URL)
    if resp.status_code != 200:
        raise Exception("Failed to fetch option chain data")

    data = resp.json()
    return data["records"]["data"]

def get_atm_strike(spot_price, strikes):
    """Find nearest ATM strike price."""
    return min(strikes, key=lambda x: abs(x - spot_price))

def suggest_option(avg_prediction: float, budget: float):
    """
    Suggest CALL or PUT option based on predicted move.
    avg_prediction: average % change predicted (positive → CALL, negative → PUT)
    budget: user budget in INR
    """
    data = fetch_option_chain()

    # Get spot price
    spot_price = data[0]["PE"]["underlyingValue"]  # spot price
    strikes = [d["strikePrice"] for d in data if "CE" in d and "PE" in d]

    atm_strike = get_atm_strike(spot_price, strikes)

    if avg_prediction > 0:
        option_type = "CE"  # CALL
    else:
        option_type = "PE"  # PUT

    # Find option chain entry for ATM
    atm_data = [d for d in data if d["strikePrice"] == atm_strike][0]
    option_info = atm_data[option_type]

    ltp = option_info["lastPrice"]
    lot_size = 15  # BankNifty lot size
    cost = ltp * lot_size

    if cost > budget:
        return {
            "decision": f"{option_type} at {atm_strike} not affordable with ₹{budget}",
            "required": cost,
            "ltp": ltp
        }

    return {
        "decision": f"BUY {option_type} at strike {atm_strike}",
        "strike": atm_strike,
        "ltp": ltp,
        "lot_size": lot_size,
        "total_cost": cost,
        "spot": spot_price,
        "prediction": avg_prediction
    }


if __name__ == "__main__":
    # Example: user inputs prediction & budget
    avg_prediction = float(input("Enter avg % prediction (e.g. 0.5 for +0.5%): "))
    budget = float(input("Enter your budget in INR: "))

    suggestion = suggest_option(avg_prediction, budget)
    print("\n📊 Option Suggestion:", json.dumps(suggestion, indent=2))
