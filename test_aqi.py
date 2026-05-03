import requests
import csv
from datetime import datetime

API_KEY = "18aad610cd7aaf807c3e6f370dcde421"

# 🔹 Step 1: Get coordinates
def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if isinstance(data, dict) and "cod" in data:
        print("API Error:", data["message"])
        return None, None

    if isinstance(data, list) and len(data) > 0:
        return data[0]['lat'], data[0]['lon']
    else:
        print("City not found ❌")
        return None, None


# 🔹 Step 2: Get pollution data
def get_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    return data['list'][0]['components']


# 🔥 Step 3: Advanced AQI Calculation (Multi-pollutant)

def aqi_pm25(pm25):
    if pm25 <= 30:
        return (pm25 / 30) * 50
    elif pm25 <= 60:
        return 50 + ((pm25 - 30) / 30) * 50
    elif pm25 <= 90:
        return 100 + ((pm25 - 60) / 30) * 100
    elif pm25 <= 120:
        return 200 + ((pm25 - 90) / 30) * 100
    elif pm25 <= 250:
        return 300 + ((pm25 - 120) / 130) * 100
    else:
        return 400 + ((pm25 - 250) / 250) * 100


def aqi_pm10(pm10):
    if pm10 <= 50:
        return (pm10 / 50) * 50
    elif pm10 <= 100:
        return 50 + ((pm10 - 50) / 50) * 50
    elif pm10 <= 250:
        return 100 + ((pm10 - 100) / 150) * 100
    elif pm10 <= 350:
        return 200 + ((pm10 - 250) / 100) * 100
    elif pm10 <= 430:
        return 300 + ((pm10 - 350) / 80) * 100
    else:
        return 400 + ((pm10 - 430) / 80) * 100


def aqi_no2(no2):
    if no2 <= 40:
        return (no2 / 40) * 50
    elif no2 <= 80:
        return 50 + ((no2 - 40) / 40) * 50
    elif no2 <= 180:
        return 100 + ((no2 - 80) / 100) * 100
    else:
        return 200 + ((no2 - 180) / 100) * 100


# 🔹 Final AQI = max of all
def calculate_final_aqi(pm25, pm10, no2):
    aqi1 = aqi_pm25(pm25)
    aqi2 = aqi_pm10(pm10)
    aqi3 = aqi_no2(no2)

    return int(max(aqi1, aqi2, aqi3))


# 🔹 AQI Category
def get_category(aqi):
    if aqi <= 50:
        return "Good 🌿"
    elif aqi <= 100:
        return "Satisfactory 🙂"
    elif aqi <= 200:
        return "Moderate 😐"
    elif aqi <= 300:
        return "Poor 😷"
    elif aqi <= 400:
        return "Very Poor ☠️"
    else:
        return "Severe 🚨"


# 🔹 Save data
def save_data(city, pm25, pm10, no2, co, aqi):
    with open("aqi_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["datetime", "city", "pm25", "pm10", "no2", "co", "aqi"])

        writer.writerow([datetime.now(), city, pm25, pm10, no2, co, aqi])


# 🔥 MAIN
city = input("Enter city name: ")

lat, lon = get_coordinates(city)

if lat is not None:
    pollution = get_pollution(lat, lon)

    pm25 = pollution['pm2_5']
    pm10 = pollution['pm10']
    no2 = pollution['no2']
    co = pollution['co']

    # 🔥 Advanced AQI
    aqi_value = calculate_final_aqi(pm25, pm10, no2)
    category = get_category(aqi_value)

    # Save data
    save_data(city, pm25, pm10, no2, co, aqi_value)

    print("\n🌍 City:", city)
    print("PM2.5:", pm25)
    print("PM10:", pm10)
    print("NO2:", no2)
    print("CO:", co)
    print("Final AQI:", aqi_value)
    print("Category:", category)

else:
    print("Try again later ❌")