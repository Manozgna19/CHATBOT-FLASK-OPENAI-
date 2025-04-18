# website/views/home.py
from flask import Blueprint, render_template

# Define the blueprint for views
views_blueprint = Blueprint('views', __name__)


@views_blueprint.route("/")
def home():
    return render_template("home.html")


@views_blueprint.route("/stchatbot")
def stchatbot():
    return render_template("stchatbot.html")


@views_blueprint.route("/history")
def history():
    return render_template("history.html")
