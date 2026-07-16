import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import requests


app = Flask(__name__)

client = MongoClient(os.environ["MONGODB_URI"])
api_key= os.environ["WEATHER_API_KEY"]

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
@app.route('/match')
def match_center():
    match= match_collection.find_one()
    city= match["city"]
    match_date=match['match']
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7"
    response= requests.get(url)
    data= response.json()
    
    # default values for prevent the error on not found match date (on if condition not true)
    weather = "-"
    temprature = "-"
    humidity = "-"
    rain_chance = "-"
    wind = "-"
    
    for day in data["forecast"]["forecastday"]:
        if day["date"]==match_date:
            weather= day["day"]["condition"]["text"]
            temprature= day["day"]["avgtemp_c"]
            humidity= day["day"]["avghumidity"]
            rain_chance= day["day"]["daily_chance_of_rain"]
            wind=day["day"]["maxwind_kph"]

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
