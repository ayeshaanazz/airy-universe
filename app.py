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

    if request.method == "POST":

        city = request.form.get("city")

        try:

            # =====================================
            # GET LATITUDE & LONGITUDE
            # =====================================

            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"

            geo_response = requests.get(geo_url).json()

            if not geo_response:

                data["city"] = city
                data["alert"] = "City not found."

                return render_template(
                    "index.html",
                    data=data
                )

            lat = geo_response[0]["lat"]
            lon = geo_response[0]["lon"]

            # =====================================
            # GET AQI DATA
            # =====================================

            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

            aqi_response = requests.get(aqi_url).json()

            components = aqi_response["list"][0]["components"]

            # =====================================
            # POLLUTANTS
            # =====================================

            pm25 = components.get("pm2_5", 0)

            pm10 = components.get("pm10", 0)

            no2 = components.get("no2", 0)

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
            # ML PREDICTION
            # =====================================

            features = np.array([[pm25, pm10, no2, co]])

            prediction = model.predict(features)[0]

            prediction = round(prediction, 2)

            # =====================================
            # CATEGORY + ALERT
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
            # NEWS
            # =====================================

            news = [

                "Global pollution levels continue to rise.",

                "WHO advises monitoring AQI regularly.",

                "Governments are investing in smart environmental systems."

            ]

            # =====================================
            # STORE DATA
            # =====================================

            data = {

                "city": city,

                "pm25": pm25,
                "pm10": pm10,
                "no2": no2,
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

            data["alert"] = f"Error: {str(e)}"

    return render_template(
        "index.html",
        data=data
    )

# =====================================
# CHATBOT
# =====================================

@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message")

    response = ""

    msg = user_message.lower()

    if "aqi" in msg:

        response = "AQI means Air Quality Index. Higher AQI means worse air quality."

    elif "pollution" in msg:

        response = "Pollution can cause respiratory and health problems."

    elif "mask" in msg:

        response = "Masks are recommended during high AQI conditions."

    else:

        response = "Air quality awareness is important for environmental sustainability."

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