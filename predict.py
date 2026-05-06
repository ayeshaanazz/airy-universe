import joblib

model = joblib.load("aqi_model.pkl")

# Example input (9 features)
sample = [[150,260,55,960,22,40,18,75,2.0]]

prediction = model.predict(sample)

print("Predicted AQI:", int(prediction[0]))