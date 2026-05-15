import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)
import joblib

# ==============================
# LOAD DATASET
# ==============================

# Make sure your CSV file name is correct
df = pd.read_csv("aqi_dataset.csv")

print("Dataset Loaded Successfully!")
print(df.head())

# ==============================
# CHECK MISSING VALUES
# ==============================

print("\nMissing Values:")
print(df.isnull().sum())

# Remove missing values if any
df = df.dropna()

# ==============================
# FEATURES AND TARGET
# ==============================

# Input Features
X = df[["pm25", "pm10", "no2", "co"]]
y = df["aqi"]
# ==============================
# TRAIN TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining Data Shape:", X_train.shape)
print("Testing Data Shape:", X_test.shape)

# ==============================
# MODEL CREATION
# ==============================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# ==============================
# MODEL TRAINING
# ==============================

model.fit(X_train, y_train)

print("\nModel Training Completed!")

# ==============================
# PREDICTIONS
# ==============================

y_pred = model.predict(X_test)

# ==============================
# EVALUATION METRICS
# ==============================

r2 = r2_score(y_test, y_pred)

mae = mean_absolute_error(y_test, y_pred)

mse = mean_squared_error(y_test, y_pred)

rmse = np.sqrt(mse)

# ==============================
# PRINT RESULTS
# ==============================

print("\n========== MODEL PERFORMANCE ==========")

print(f"R2 Score        : {r2:.4f}")

print(f"MAE             : {mae:.4f}")

print(f"MSE             : {mse:.4f}")

print(f"RMSE            : {rmse:.4f}")

print("=======================================\n")

# ==============================
# SAVE MODEL
# ==============================

joblib.dump(model, "aqi_model.pkl")

print("Model Saved Successfully as aqi_model.pkl")

# ==============================
# SAMPLE PREDICTION
# ==============================

sample_data = np.array([[80, 120, 40, 1.2]])

sample_prediction = model.predict(sample_data)

print("\nSample AQI Prediction:")
print(sample_prediction[0])