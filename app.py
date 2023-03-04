from app import app, db, bot, URL, token
import time
import os

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(URL + token)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.10.10.1', port=int(os.getenv('PORT')))