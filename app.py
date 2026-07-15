import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime


app = Flask(__name__)

client = MongoClient(os.environ["MONGODB_URI"])

db = client["fearless_fighter"]
collection = db["player_stat"]
suggestions_collection = db["suggestions"]
retired_collection= db['retired_player']


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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
