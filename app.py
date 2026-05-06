import os
from flask import Flask, render_template, request, jsonify
import requests
import joblib
import matplotlib.pyplot as plt

app = Flask(__name__)

API_KEY = "18aad610cd7aaf807c3e6f370dcde421"

# Load ML model
model = joblib.load("aqi_model.pkl")


# 🌍 Get coordinates
def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    data = requests.get(url).json()
    return data[0]['lat'], data[0]['lon']


# 🌫 Pollution data
def get_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    data = requests.get(url).json()
    return data['list'][0]['components']


# 📊 AQI Calculation
def calculate_aqi(pm25):
    if pm25 <= 30:
        return int((pm25 / 30) * 50)
    elif pm25 <= 60:
        return int(50 + ((pm25 - 30) / 30) * 50)
    else:
        return int(100 + ((pm25 - 60) / 30) * 100)


# 📈 AQI Graph
def generate_graph():

    values = [80, 95, 120, 150, 130, 170, 145]

    plt.figure(figsize=(6,3))
    plt.plot(values, marker='o')
    plt.title("7-Day AQI Trend")
    plt.xlabel("Days")
    plt.ylabel("AQI")

    plt.savefig("static/graph.png")
    plt.close()


# 🌿 AQI Category
def get_category(aqi):

    if aqi <= 50:
        return "Good 🌿"

    elif aqi <= 100:
        return "Satisfactory 🙂"

    elif aqi <= 200:
        return "Moderate 😐"

    else:
        return "Poor 😷"


# 🎨 Background
def get_bg_color(aqi):

    if aqi <= 50:
        return "good"

    elif aqi <= 100:
        return "moderate"

    elif aqi <= 200:
        return "poor"

    else:
        return "severe"


# 🤖 Smart Chatbot
@app.route("/chat", methods=["POST"])
def chat():

    user_msg = request.json.get("message", "").lower()

    if "aqi" in user_msg:
        reply = "AQI measures how polluted the air is. Higher AQI can affect health."

    elif "health" in user_msg:
        reply = "Poor AQI may cause breathing problems, asthma, and heart issues."

    elif "pollution" in user_msg:
        reply = "Pollution mainly comes from vehicles, industries, and burning fossil fuels."

    elif "trees" in user_msg:
        reply = "Trees absorb carbon dioxide and improve air quality."

    elif "environment" in user_msg:
        reply = "Protect the environment by saving energy and reducing plastic use."

    else:
        reply = "Ask me about AQI, pollution, health, or environment 😊"

    return jsonify({"response": reply})


# 📰 News
def get_news():

    return [
        "Delhi AQI rises due to pollution",
        "Climate change affecting global air quality",
        "WHO warns about rising urban pollution"
    ]


# 🌍 Main Route
@app.route("/", methods=["GET", "POST"])
def index():

    generate_graph()

    data = {"bg": "good"}

    if request.method == "POST":

        city = request.form["city"]

        lat, lon = get_coordinates(city)

        pollution = get_pollution(lat, lon)

        pm25 = pollution['pm2_5']
        pm10 = pollution['pm10']
        no2 = pollution['no2']
        co = pollution['co']

        prediction = model.predict([[pm25, pm10, no2, co]])
        predicted_aqi = int(prediction[0])

        current_aqi = calculate_aqi(pm25)

        category = get_category(current_aqi)

        bg = get_bg_color(current_aqi)

        # 🔔 Pollution Alert
        if current_aqi > 150:
            alert = "⚠ Air quality is unhealthy today. Wear a mask outdoors."

        else:
            alert = "🌿 Air quality is acceptable today."

        data = {
            "city": city,
            "pm25": pm25,
            "aqi": current_aqi,
            "category": category,
            "prediction": predicted_aqi,
            "bg": bg,
            "news": get_news(),
            "alert": alert
        }

    return render_template("index.html", data=data)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )