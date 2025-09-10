# backend/main.py

from services import option_selector
import numpy as np
from services import model  # model.py runs & produces y_pred_percent, y_test_percent

def run_pipeline(budget: float):
    """
    End-to-end pipeline:
    1. Take LSTM predictions from model.py
    2. Compute average predicted % move (next 6 steps)
    3. Suggest CALL/PUT option based on budget
    """
    # Take last 6 predictions (as per your 30-min horizon)
    avg_prediction = np.mean(model.y_pred_percent[-6:])

    print("\n🔮 LSTM Avg Prediction (next 30m):", round(avg_prediction, 3), "%")

    suggestion = option_selector.suggest_option(avg_prediction, budget)

    print("\n📊 Final Suggestion:")
    for k, v in suggestion.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    budget = float(input("Enter your budget (INR): "))
    run_pipeline(budget)
