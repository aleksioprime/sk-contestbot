import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import telebot
import schedule
import time

token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)
URL = os.getenv('URL')
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

from app import models, forms, routes, routes_telegram

schedule.every().day.at("09:00").do(routes_telegram.sending_messages)
schedule.every().day.at("13:00").do(routes_telegram.sending_messages)
schedule.every().day.at("18:00").do(routes_telegram.sending_messages)

def schedule_run():
    now = time.time()
    while True:
        if int(time.time() - now) > 3:
            schedule.run_pending()
            print("Проверка:", time.time())
            now = time.time()