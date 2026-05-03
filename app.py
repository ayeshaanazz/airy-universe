from flask import Flask, render_template, request, jsonify
import requests
import joblib

app = Flask(__name__)

# 🌍 OpenWeather API
API_KEY = "18aad610cd7aaf807c3e6f370dcde421"

# Load ML model
model = joblib.load("aqi_model.pkl")


# 📍 Get coordinates
def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    data = requests.get(url).json()
    return data[0]['lat'], data[0]['lon']


# 🌫 Get pollution data
def get_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    data = requests.get(url).json()
    return data['list'][0]['components']


# 📊 AQI calculation
def calculate_aqi(pm25):
    if pm25 <= 30:
        return int((pm25 / 30) * 50)
    elif pm25 <= 60:
        return int(50 + ((pm25 - 30) / 30) * 50)
    else:
        return int(100 + ((pm25 - 60) / 30) * 100)


# 📊 AQI category
def get_category(aqi):
    if aqi <= 50:
        return "Good 🌿"
    elif aqi <= 100:
        return "Satisfactory 🙂"
    elif aqi <= 200:
        return "Moderate 😐"
    else:
        return "Poor 😷"


# 🎨 Background color
def get_bg_color(aqi):
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 200:
        return "poor"
    else:
        return "severe"


# 🤖 FREE SMART CHATBOT
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    if "aqi" in user_msg:
        reply = "AQI (Air Quality Index) measures air pollution. Lower AQI means cleaner air, higher AQI is harmful."
    
    elif "health" in user_msg:
        reply = "Poor air quality can cause asthma, lung damage, breathing problems, and heart issues."
    
    elif "pollution" in user_msg:
        reply = "Pollution is caused by vehicles, industries, and burning fuels. Reducing emissions improves air quality."
    
    elif "environment" in user_msg:
        reply = "Protect the environment by planting trees, reducing plastic use, and conserving energy."
    
    elif "trees" in user_msg:
        reply = "Trees absorb carbon dioxide and release oxygen, improving air quality."
    
    elif "animals" in user_msg:
        reply = "Air pollution harms animals by damaging their lungs and affecting ecosystems."
    
    elif "reduce" in user_msg:
        reply = "Use public transport, save electricity, avoid plastic, and plant trees to reduce pollution."
    
    else:
        reply = "Ask me about AQI, pollution, environment, or health 😊"

    return jsonify({"response": reply})


# 📰 Dummy news
def get_news():
    return [
        "Delhi AQI rises due to pollution",
        "Air pollution affecting global health",
        "Steps to improve environmental sustainability"
    ]


# 🌐 MAIN ROUTE
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

        # ML prediction
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


# ▶ RUN APP
if __name__ == "__main__":
    app.run(debug=True, port=5001)
