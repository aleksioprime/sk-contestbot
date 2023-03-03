import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

import telebot

token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)
URL = os.getenv('URL')
# ngrok http 5000
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

from app import models, forms, routes, routes_telegram