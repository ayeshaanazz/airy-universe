from flask import Flask, render_template, request, jsonify
import requests
import joblib
import os

app = Flask(__name__)

API_KEY = "18aad610cd7aaf807c3e6f370dcde421"

# Load model
model = joblib.load("aqi_model.pkl")


def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    data = requests.get(url).json()
    return data[0]['lat'], data[0]['lon']


def get_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    data = requests.get(url).json()
    return data['list'][0]['components']


def calculate_aqi(pm25):
    if pm25 <= 30:
        return int((pm25 / 30) * 50)
    elif pm25 <= 60:
        return int(50 + ((pm25 - 30) / 30) * 50)
    else:
        return int(100 + ((pm25 - 60) / 30) * 100)


def get_category(aqi):
    if aqi <= 50:
        return "Good 🌿"
    elif aqi <= 100:
        return "Satisfactory 🙂"
    elif aqi <= 200:
        return "Moderate 😐"
    else:
        return "Poor 😷"


def get_bg_color(aqi):
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 200:
        return "poor"
    else:
        return "severe"


# 🔥 Chatbot route
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    if "aqi" in user_msg:
        reply = "AQI shows how polluted the air is. Lower is better."
    elif "health" in user_msg:
        reply = "High AQI can cause breathing issues. Avoid outdoor exposure."
    elif "environment" in user_msg:
        reply = "Plant trees, reduce plastic use, and save energy."
    else:
        reply = "Ask about AQI, health, or environment 😊"

    return jsonify({"response": reply})


# 🔥 News API (optional)
def get_news():
    try:
        url = "https://newsapi.org/v2/everything?q=air pollution&apiKey=YOUR_NEWS_API_KEY"
        data = requests.get(url).json()

        articles = []
        for item in data.get("articles", [])[:3]:
            articles.append(item["title"])

        return articles
    except:
        return []


@app.route("/", methods=["GET", "POST"])
def index():
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

        data = {
            "city": city,
            "pm25": pm25,
            "aqi": current_aqi,
            "category": category,
            "prediction": predicted_aqi,
            "bg": bg,
            "news": get_news()
        }

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
