import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

import telebot

token = "1504490782:AAE1_ttpgf_asklWrXxi3Gw3EaKnHlzdt88"
bot = telebot.TeleBot(token)
URL = "https://17df-185-107-243-81.eu.ngrok.io/"
# ngrok http 5000
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

from app import models, forms, routes, routes_telegram