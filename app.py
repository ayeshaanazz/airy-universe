from flask import Flask, render_template, request, jsonify
import requests
import joblib
import numpy as np
import os

app = Flask(__name__)

# =====================================
# LOAD ML MODEL
# =====================================

model = joblib.load("aqi_model.pkl")

# =====================================
# API KEY
# =====================================

API_KEY = os.environ.get("OPENAI_API_KEY")

# =====================================
# HOME ROUTE
# =====================================

@app.route("/", methods=["GET", "POST"])
def index():

    data = {}
    city = ""

    if request.method == "POST":

        city = request.form.get("city")

        try:

            # =====================================
            # GET LATITUDE & LONGITUDE
            # =====================================

            geo_url = (
                f"http://api.openweathermap.org/geo/1.0/direct?"
                f"q={city}&limit=1&appid={API_KEY}"
            )

            geo_response = requests.get(geo_url).json()

            if not geo_response:

                data = {
                    "city": city,
                    "alert": "City not found.",
                    "bg": "moderate"
                }

                return render_template(
                    "index.html",
                    data=data
                )

            lat = geo_response[0]["lat"]
            lon = geo_response[0]["lon"]

            # =====================================
            # GET AQI DATA
            # =====================================

            aqi_url = (
                f"http://api.openweathermap.org/data/2.5/air_pollution?"
                f"lat={lat}&lon={lon}&appid={API_KEY}"
            )

            aqi_response = requests.get(aqi_url).json()

            components = aqi_response["list"][0]["components"]

            # =====================================
            # POLLUTANTS
            # =====================================

            pm25 = components.get("pm2_5", 0)
            pm10 = components.get("pm10", 0)
            no2 = components.get("no2", 0)

            # CO scaled for model compatibility
            co = components.get("co", 0) / 100

            # =====================================
            # REAL AQI
            # =====================================

            api_aqi = aqi_response["list"][0]["main"]["aqi"]

            aqi_scale = {
                1: 50,
                2: 100,
                3: 150,
                4: 200,
                5: 300
            }

            current_aqi = aqi_scale.get(api_aqi, 0)

            # =====================================
            # MACHINE LEARNING PREDICTION
            # =====================================

            features = np.array([[pm25, pm10, no2, co]])

            prediction = model.predict(features)[0]

            prediction = round(float(prediction), 2)

            # =====================================
            # AQI CATEGORY
            # =====================================

            if current_aqi <= 50:

                category = "Good 🌿"
                alert = "Air quality is good today."
                bg = "good"

            elif current_aqi <= 100:

                category = "Moderate 😐"
                alert = "Air quality is acceptable today."
                bg = "moderate"

            elif current_aqi <= 150:

                category = "Poor 😷"
                alert = "Sensitive people should avoid outdoor activities."
                bg = "poor"

            elif current_aqi <= 200:

                category = "Very Poor ⚠️"
                alert = "Wear masks and limit outdoor exposure."
                bg = "verypoor"

            else:

                category = "Severe 🚨"
                alert = "Avoid going outside today."
                bg = "severe"

            # =====================================
            # FAKE NEWS DATA
            # =====================================

            news = [

                "WHO recommends monitoring AQI regularly.",

                "Governments are investing in smart environmental systems.",

                "Global air pollution remains a major concern."

            ]

            # =====================================
            # FINAL DATA
            # =====================================

            data = {

                "city": city,

                "pm25": round(pm25, 2),
                "pm10": round(pm10, 2),
                "no2": round(no2, 2),
                "co": round(co, 2),

                "aqi": current_aqi,

                "prediction": prediction,

                "category": category,

                "alert": alert,

                "bg": bg,

                "news": news,

                "lat": lat,
                "lon": lon

            }

        except Exception as e:

            print("ERROR:", e)

            data = {

                "city": city,

                "alert": f"Error occurred: {str(e)}",

                "bg": "moderate"

            }

    return render_template(
        "index.html",
        data=data
    )

# =====================================
# CHATBOT ROUTE
# =====================================

@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message")

    msg = user_message.lower()

    if "aqi" in msg:

        response = (
            "AQI stands for Air Quality Index. "
            "Higher AQI means worse air quality."
        )

    elif "pollution" in msg:

        response = (
            "Pollution can affect lungs, heart, "
            "and overall health."
        )

    elif "mask" in msg:

        response = (
            "Masks are recommended during poor "
            "AQI conditions."
        )

    else:

        response = (
            "Environmental awareness is important "
            "for sustainability."
        )

    return jsonify({
        "response": response
    })

# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=10000
    )