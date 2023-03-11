from app import app, token, bot, db
import telebot
from flask import request
import json
# https://habr.com/ru/post/675404/

from .models import UserTg, Group, Contest
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .markups import main_menu, register

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
    elif message.text == "Мои олимпиады":
        with app.app_context():
            user = UserTg.query.filter_by(user_id = message.from_user.id).first()
            contests = [x for x in user.contests]
        if len(contests):
            str_contests = "\n".join([x.title for x in contests])
            bot.send_message(message.chat.id, f'Мои олимпиады\n\n'
                                              f'<b>{str_contests}</b>', parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда")

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
                page = 1
                count = len(contests)
                if count:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton(text='Добавить', callback_data='add__' + str(contests[0].id)))
                    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                                InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "{group.title}"\n\n'
                                                           f'<b>{contests[0].title}</b>\n'
                                                           f'<b>Описание:</b> <i>{contests[0].description}</i>\n'
                                                           f'<b>Ссылка:</b> <i>{contests[0].link}</i>\n', parse_mode="HTML", reply_markup = markup)
                else:
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "{group.title}"\n\n'
                                                           f'<b>Олимпиад в этой категории пока нет!</b>', parse_mode="HTML")
            elif "pagination" in call.data:
                json_string = json.loads(call.data)
                count = json_string['CountPage']
                page = json_string['NumberPage']
                group_id = json_string['Group']
                with app.app_context():
                    group = Group.query.filter_by(id=group_id).first()
                    contests = Contest.query.filter_by(group_id=group.id).all()
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(text='Добавить', callback_data='add__' + str(contests[page - 1].id)))
                if page == 1:
                    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                elif page == count:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
                else:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                bot.edit_message_text(f'Просмотр олимпиад кафедры "{group.title}"\n\n'
                                      f'<b>{contests[page - 1].title}</b>\n'
                                      f'<b>Описание:</b> <i>{contests[page - 1].description}</i>\n'
                                      f'<b>Ссылка:</b> <i>{contests[page - 1].link}</i>\n',
                                      parse_mode="HTML",reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif call.data.split('__')[0] == "add":
                with app.app_context():
                    user_tg = UserTg.query.filter_by(user_id=call.from_user.id).first()
                    contest = Contest.query.filter_by(id=call.data.split('__')[1]).first()
                    user_tg.contests.append(contest)
                    db.session.add(user_tg)
                    db.session.commit()
                bot.send_message(call.message.chat.id, "Конкурс успешно добавлен!", reply_markup=main_menu)
    except Exception as e:
        print(repr(e))

@app.route("/" + token, methods=['POST'])
def getMessage():
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200