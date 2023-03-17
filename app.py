from app import app, db, bot, URL, token, schedule_run
import time
import os
from threading import Thread

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(URL + token)
    with app.app_context():
        db.create_all()
    Thread(target=schedule_run, daemon=True).start()
    app.run(debug=True, use_reloader=False, host=os.getenv('HOST'), port=int(os.getenv('PORT')))