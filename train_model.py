import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load dataset
df = pd.read_csv("aqi_dataset.csv")

# Features
X = df[['pm25','pm10','no2','co']]

# Target
y = df['aqi']

# Train model
model = RandomForestRegressor()
model.fit(X, y)

# Save model
joblib.dump(model, "aqi_model.pkl")

print("Model trained successfully ✅")