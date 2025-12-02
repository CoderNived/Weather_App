# train_models.py
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import xgboost as xgb

# load
df = pd.read_csv("iot_data.csv")
X = df[["temp","humidity","vibration","pressure"]].values
y = df["power"].values

# split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# scaler
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)

models = {}

# 1) Linear Regression
lr = LinearRegression()
lr.fit(X_train_s, y_train)
models["LinearRegression"] = lr

# 2) Random Forest
rf = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)  # RF on raw features (works fine)
models["RandomForest"] = rf

# 3) SVR (kernel rbf) — needs scaled data
svr = SVR(kernel="rbf", C=10, epsilon=0.5)
svr.fit(X_train_s, y_train)
models["SVR"] = svr

# 4) Polynomial Regression (degree 2) using pipeline
poly_pipe = make_pipeline(PolynomialFeatures(degree=2, include_bias=False), LinearRegression())
poly_pipe.fit(X_train_s, y_train)
models["Polynomial(2)"] = poly_pipe

# 5) XGBoost
xg = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42, n_jobs=4)
xg.fit(X_train, y_train)
models["XGBoost"] = xg

# evaluate
def evaluate(name, model, use_scaled=False):
    Xs = X_test_s if use_scaled else X_test
    y_pred = model.predict(Xs)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = (mean_squared_error(y_test, y_pred)) ** 0.5   # fixed version
    r2 = r2_score(y_test, y_pred)

    print(f"{name:15s}  MAE: {mae:.3f}  RMSE: {rmse:.3f}  R2: {r2:.3f}")
    return {"mae": mae, "rmse": rmse, "r2": r2}


results = {}
results["LinearRegression"] = evaluate("LinearRegression", lr, use_scaled=True)
results["RandomForest"] = evaluate("RandomForest", rf, use_scaled=False)
results["SVR"] = evaluate("SVR", svr, use_scaled=True)
results["Polynomial(2)"] = evaluate("Polynomial(2)", poly_pipe, use_scaled=True)
results["XGBoost"] = evaluate("XGBoost", xg, use_scaled=False)

# save models and scaler
joblib.dump(scaler, "scaler.joblib")
for name, model in models.items():
    joblib.dump(model, f"{name}.joblib")

# save a small summary CSV
pd.DataFrame(results).T.to_csv("model_results.csv")
print("Saved models, scaler, and model_results.csv")
