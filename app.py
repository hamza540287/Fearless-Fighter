from flask import Flask, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://ah540223_db_user:mongodbatlas540223@cluster0.cxzselc.mongodb.net/fearless_fighter?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["fearless_fighter"]
collection = db["player_stat"]
suggestions_collection = db["suggestions"]


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
    return render_template("retired.html")


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
