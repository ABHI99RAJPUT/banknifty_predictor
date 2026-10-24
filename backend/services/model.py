import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime, timedelta

from .preprocess import preprocess_data
from .lstm_prepare import prepare_data

# Parameters
SEQ_LENGTH = 60
INTERVAL = "5m"
EPOCHS = 30
BATCH_SIZE = 32
N_DAYS = 30

# Fetch last N trading days robustly
dfs = []
valid_days = 0
day = datetime.now()

while valid_days < N_DAYS:
    try:
        df_day = preprocess_data(date=day, interval=INTERVAL)
        if not df_day.empty:
            dfs.append(df_day)
            valid_days += 1
            print(f"✅ Got data for {day.date()}, shape={df_day.shape}")
        else:
            print(f"⚠️ Skipping {day.date()} (no data)")
    except Exception as e:
        print(f"⚠️ Skipping {day.date()} due to error: {e}")
    day -= timedelta(days=1)

df = pd.concat(dfs).sort_index()
print("\n📊 Final dataset shape:", df.shape)

# Prepare sequences
X, y, scaler_X, scaler_y = prepare_data(df, seq_length=SEQ_LENGTH)

# Train/test split
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build LSTM model
model = Sequential([
    tf.keras.Input(shape=(SEQ_LENGTH, X.shape[2])),
    LSTM(128, return_sequences=True),
    Dropout(0.3),
    LSTM(64),
    Dropout(0.3),
    Dense(32, activation="relu"),
    Dense(1, activation="linear")  # regression
])

model.compile(
    loss="mse",
    optimizer="adam",
    metrics=["mae"]
)

early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

# Train
print("\n🚀 Training...")
history = model.fit(
    X_train, y_train,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_split=0.1,
    verbose=1,
    callbacks=[early_stop]
)

# Predict & inverse scale
y_pred_scaled = model.predict(X_test)
y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten()
y_test_actual = scaler_y.inverse_transform(y_test.reshape(-1,1)).flatten()

# Convert to % for readability
y_pred_percent = y_pred * 100
y_test_percent = y_test_actual * 100

print("\nMAE:", mean_absolute_error(y_test_percent, y_pred_percent))
print("MSE:", mean_squared_error(y_test_percent, y_pred_percent))

print("\nPredicted % change (last 10):", y_pred_percent[-10:])
print("Actual % change     (last 10):", y_test_percent[-10:])
