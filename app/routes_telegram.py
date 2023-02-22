from app import app, token, bot, db
import telebot
from flask import request

from .models import UserTg, Group, Contest
from .markups import main_menu, subjects, register

@bot.message_handler(commands=['start'])
def start(message):
    print(message.from_user.id)
    with app.app_context():
        user = UserTg.query.filter_by(user_id=message.from_user.id).first()
    print(message.from_user.username)
    if user is not None:
        bot.send_message(message.chat.id, f'Здравствуйте, {user.username}!', reply_markup=main_menu)
    else:
        bot.send_message(message.chat.id, f'Уважаемый, {message.from_user.username}, вы не зарегистрированы в системе!', reply_markup=register)

@bot.message_handler(content_types=['text'])
def handler(message):
   if message.text == "Все олимпиады":
       with app.app_context():
           groups = Group.query.all()
       subjects = telebot.types.InlineKeyboardMarkup(row_width=3)
       for group in groups:
           subjects.add(telebot.types.InlineKeyboardButton(group.title, callback_data='sub__' + group.code))
       bot.send_message(message.chat.id, "Выберите предметную кафедру", reply_markup=subjects)
   else:
       bot.send_message(message.chat.id, "Выберите пукнт меню")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == "register":
                print(call.message.chat.id)
                with app.app_context():
                    user_add = UserTg(user_id=call.message.chat.id, username=call.message.chat.username)
                    db.session.add(user_add)
                    db.session.commit()
                bot.send_message(call.message.chat.id, "Поздравляем, вы зарегистрированы!", reply_markup=main_menu)
            elif call.data.split('__')[0] == "sub":
                with app.app_context():
                    group = Group.query.filter_by(code=call.data.split('__')[1]).first()
                    contests = Contest.query.filter_by(group_id=group.id).all()
                if len(contests):
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "{group.title}"\n\n'
                                                           f'<b>{contests[0].title}</b>\n'
                                                           f'<b>Описание:</b> <i>{contests[0].description}</i>\n'
                                                           f'<b>Ссылка:</b> <i>{contests[0].link}</i>\n',
                                     parse_mode="HTML")
                else:
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "{group.title}"\n\n'
                                                           f'<b>Олимпиад в этой категории пока нет!</b>', parse_mode="HTML")
            elif call.data.split('__')[0] == "pag":
                pass
    except Exception as e:
        print(repr(e))

@app.route("/" + token, methods=['POST'])
def getMessage():
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200