import joblib
import numpy as np
import pandas as pd

model = joblib.load("co_model.pkl")
scaler = joblib.load("scaler.pkl")

def test(value):
    value_df = pd.DataFrame([[value]], columns=["CO"])
    scaled = scaler.transform(value_df)
    pred = model.predict(scaled)
    return "ANOMALY" if pred[0] == -1 else "NORMAL"

# Test values
print("1.0 →", test(1.0))
print("2.0 →", test(2.0))
print("8.0 →", test(8.0))
print("12.0 →", test(12.0))