import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import requests


app = Flask(__name__)

client = MongoClient(os.environ["MONGODB_URI"])
# api_key= os.environ["WEATHER_API_KEY"]

db = client["fearless_fighter"]
collection = db["player_stat"]
suggestions_collection = db["suggestions"]
retired_collection= db['retired_player']
match_collection= db['match_center']


@app.route("/")
def home():
    stat = collection.find()
    return render_template("home.html", players=stat)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/details/<player_id>")
def details(player_id):
    player = collection.find_one({"_id": ObjectId(player_id)})
    return render_template("details.html", player=player)


@app.route("/retired")
def retired():
    players= retired_collection.find()
    return render_template("retired.html", players=players)

@app.route("/retired_details/<player_id>")
def retired_details(player_id):
    player= retired_collection.find_one({"_id":ObjectId(player_id)})
    return render_template("details.html", player=player)

@app.route("/follow", methods=["GET", "POST"])
def submit_suggestion():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        player_name = request.form["player_name"]
        suggestion = request.form["suggestion"]
        timestamp = datetime.now()

        suggestions_collection.insert_one(
            {
                "name": name,
                "email": email,
                "player_name": player_name,
                "suggestion": suggestion,
                "timestamp": timestamp,
            }
        )
    return render_template("follow.html")
# @app.route('/match')
# def match_center():
#     match= match_collection.find_one()
#     city= match["city"]
#     match_date=match['date']
#     url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7"
#     response= requests.get(url)
#     data= response.json()
    
#     # default values for prevent the error on not found match date (on if condition not true)
#     weather = "-"
#     temprature = "-"
#     humidity = "-"
#     rain_chance = "-"
#     wind = "-"
    
#     for day in data["forecast"]["forecastday"]:
#         if day["date"]==match_date:
#             weather= day["day"]["condition"]["text"]
#             temprature= day["day"]["avgtemp_c"]
#             humidity= day["day"]["avghumidity"]
#             rain_chance= day["day"]["daily_chance_of_rain"]
#             wind=day["day"]["maxwind_kph"]

#             break
#     return render_template(
#         "match_center.html",
#         match=match,
#         weather=weather,
#         temprature=temprature,
#         humidity=humidity,
#         rain_chance=rain_chance,
#         wind=wind
#     )
@app.route('/match')
def match_center():
    match = match_collection.find_one()

    city = match["city"]
    match_date = match["date"]

    # Coordinates for supported cities
    coordinates = {
        "Lahore": (31.5204, 74.3587),
        "Karachi": (24.8607, 67.0011),
        "Islamabad": (33.6844, 73.0479),
        "Rawalpindi": (33.5651, 73.0169),
        "Multan": (30.1575, 71.5249)
    }

    latitude, longitude = coordinates.get(city, (31.5204, 74.3587))

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&daily=weather_code,"
        f"temperature_2m_max,"
        f"precipitation_probability_max,"
        f"wind_speed_10m_max"
        f"&hourly=relative_humidity_2m"
        f"&timezone=auto"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return render_template(
            "match_center.html",
            match=match,
            weather="Unavailable",
            temprature="-",
            humidity="-",
            rain_chance="-",
            wind="-"
        )

    data = response.json()

    weather = "-"
    temprature = "-"
    humidity = "-"
    rain_chance = "-"
    wind = "-"

    weather_codes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        61: "Light Rain",
        63: "Rain",
        65: "Heavy Rain",
        71: "Snow",
        80: "Rain Showers",
        95: "Thunderstorm"
    }

    daily = data["daily"]

    for i, date in enumerate(daily["time"]):

        if date == match_date:

            code = daily["weather_code"][i]

            weather = weather_codes.get(code, "Unknown")

            temprature = daily["temperature_2m_max"][i]

            rain_chance = daily["precipitation_probability_max"][i]

            wind = daily["wind_speed_10m_max"][i]

            humidity = "Available Hourly"

            break

    return render_template(
        "match_center.html",
        match=match,
        weather=weather,
        temprature=temprature,
        humidity=humidity,
        rain_chance=rain_chance,
        wind=wind
    )


       










if __name__ == "__main__":
    app.run(debug=True, port=5000)
