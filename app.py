from flask import Flask, render_template, request
import requests
import joblib
import numpy as np
import os

app = Flask(__name__)

# ==============================
# LOAD MACHINE LEARNING MODEL
# ==============================

model = joblib.load("aqi_model.pkl")

# ==============================
# OPENWEATHER API KEY
# ==============================

API_KEY = os.environ.get("OPENAI_API_KEY")

# ==============================
# HOME ROUTE
# ==============================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        city = request.form.get("city")

        try:

            # ==============================
            # GET LATITUDE & LONGITUDE
            # ==============================

            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"

            geo_response = requests.get(geo_url).json()

            if not geo_response:
                return render_template(
                    "index.html",
                    error="City not found."
                )

            lat = geo_response[0]["lat"]
            lon = geo_response[0]["lon"]

            # ==============================
            # GET AQI DATA
            # ==============================

            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

            aqi_response = requests.get(aqi_url).json()

            components = aqi_response["list"][0]["components"]

            # ==============================
            # POLLUTANTS
            # ==============================

            pm25 = components.get("pm2_5", 0)
            pm10 = components.get("pm10", 0)
            no2 = components.get("no2", 0)

            # Convert CO scale for better ML compatibility
            co = components.get("co", 0) / 100

            # ==============================
            # MACHINE LEARNING PREDICTION
            # ==============================

            features = np.array([[pm25, pm10, no2, co]])

            predicted_aqi = model.predict(features)[0]

            predicted_aqi = round(predicted_aqi, 2)

            # ==============================
            # AQI CATEGORY
            # ==============================

            if predicted_aqi <= 50:
                category = "Good"
                alert = "Air quality is good."

            elif predicted_aqi <= 100:
                category = "Moderate"
                alert = "Air quality is acceptable."

            elif predicted_aqi <= 150:
                category = "Poor"
                alert = "Sensitive people should avoid outdoor activities."

            elif predicted_aqi <= 200:
                category = "Very Poor"
                alert = "Wear masks and limit outdoor exposure."

            else:
                category = "Severe"
                alert = "Avoid going outside."

            # ==============================
            # RENDER RESULT
            # ==============================

            return render_template(
                "index.html",
                city=city,
                pm25=pm25,
                pm10=pm10,
                no2=no2,
                co=co,
                predicted_aqi=predicted_aqi,
                category=category,
                alert=alert,
                lat=lat,
                lon=lon
            )

        except Exception as e:

            return render_template(
                "index.html",
                error=f"Error occurred: {str(e)}"
            )

    return render_template("index.html")


# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)