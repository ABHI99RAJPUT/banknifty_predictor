import numpy as np
from sklearn.preprocessing import MinMaxScaler

def create_sequences(X, y, seq_length=30):
    Xs, ys = [], []
    for i in range(len(X) - seq_length):
        Xs.append(X[i:i+seq_length])
        ys.append(y[i+seq_length])
    return np.array(Xs), np.array(ys)

def prepare_data(df, seq_length=30):
    """
    Scale features and target, create sequences for LSTM regression.
    Returns X, y, feature scaler, target scaler
    """
    if df.empty:
        raise ValueError("Empty DataFrame received in prepare_data()")

    features = df.drop(columns=["Target"]).values
    target = df["Target"].values.reshape(-1, 1)

    # Scale features & target
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    features_scaled = scaler_X.fit_transform(features)
    target_scaled = scaler_y.fit_transform(target)

    X, y = create_sequences(features_scaled, target_scaled, seq_length)

    if len(X) == 0:
        raise ValueError("Sequence length too long for the data")

    return X, y, scaler_X, scaler_y

if __name__ == "__main__":
    from preprocess import preprocess_data
    from datetime import datetime

    df = preprocess_data(datetime(2025, 8, 25), interval="1m")
    if not df.empty:
        X, y, scaler_X, scaler_y = prepare_data(df)
        print("X shape:", X.shape, "y shape:", y.shape)
