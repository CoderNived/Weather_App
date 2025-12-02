# app.py
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# ---------------------------------------------------
# LOAD ML MODELS + SCALER
# ---------------------------------------------------

try:
    scaler = joblib.load("scaler.joblib")

    models = {
        "LinearRegression": joblib.load("LinearRegression.joblib"),
        "RandomForest": joblib.load("RandomForest.joblib"),
        "SVR": joblib.load("SVR.joblib"),
        "Polynomial(2)": joblib.load("Polynomial(2).joblib"),
        "XGBoost": joblib.load("XGBoost.joblib")
    }

    print("✅ Models loaded successfully.")

except Exception as e:
    print("❌ Error loading models:", e)
    scaler = None
    models = {}

# ---------------------------------------------------
# HOME PAGE (Weather UI)
# ---------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")   # this loads your weather HTML


# ---------------------------------------------------
# ML PREDICTION API
# ---------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    if not models or scaler is None:
        return jsonify({"error": "Models not loaded"}), 500

    try:
        data = request.json

        # Extract values
        temp = float(data.get("temp"))
        humidity = float(data.get("humidity"))
        vibration = float(data.get("vibration"))
        pressure = float(data.get("pressure"))

        # Convert to array
        X = np.array([[temp, humidity, vibration, pressure]])

        # Scaled version (for LR, SVR, Polynomial)
        X_scaled = scaler.transform(X)

        # Predictions dictionary
        preds = {
            "LinearRegression": float(models["LinearRegression"].predict(X_scaled)[0]),
            "SVR": float(models["SVR"].predict(X_scaled)[0]),
            "Polynomial(2)": float(models["Polynomial(2)"].predict(X_scaled)[0]),
            "RandomForest": float(models["RandomForest"].predict(X)[0]),
            "XGBoost": float(models["XGBoost"].predict(X)[0])
        }

        return jsonify(preds)

    except Exception as e:
        print("❌ Prediction Error:", e)
        return jsonify({"error": "Prediction failed"}), 400


# ---------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
