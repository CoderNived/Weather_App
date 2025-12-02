# generate_data.py
import numpy as np
import pandas as pd

np.random.seed(42)

def generate_rows(n=2000):
    # timestamp not necessary for model, but nice to have
    timestamps = pd.date_range("2024-01-01", periods=n, freq="H")
    # sensors
    temp = 20 + 10 * np.sin(np.linspace(0, 12*np.pi, n)) + np.random.normal(0, 1.5, n)  # cyclic + noise
    humidity = 40 + 20 * np.cos(np.linspace(0, 6*np.pi, n)) + np.random.normal(0, 4, n)
    vibration = np.abs(np.random.normal(0.5, 0.3, n))  # small positive
    pressure = 1000 + 5 * np.sin(np.linspace(0, 3*np.pi, n)) + np.random.normal(0, 1.0, n)
    # target: power consumption (some nonlinear function)
    power = (0.8*temp + 0.5*humidity + 15*vibration + 0.01*(pressure-1000)**2) \
            + 5*np.sin(np.linspace(0,2*np.pi,n)) + np.random.normal(0,3,n)
    df = pd.DataFrame({
        "timestamp": timestamps,
        "temp": temp,
        "humidity": humidity,
        "vibration": vibration,
        "pressure": pressure,
        "power": power
    })
    return df

if __name__ == "__main__":
    df = generate_rows(3000)
    df.to_csv("iot_data.csv", index=False)
    print("Saved iot_data.csv with", len(df), "rows")
