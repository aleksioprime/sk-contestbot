from app import app, token, bot, db
from datetime import datetime
import telebot
from flask import request
import json
# https://habr.com/ru/post/675404/



from .models import UserTg, Group, Contest
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .markups import main_menu, register

def sending_messages():
    print("Рассылка напоминаний")
    with app.app_context():
        users = UserTg.query.all()
        for user in users:
            print(user)
            for contest in user.contests:
                print(contest)
                stages_list = [(stage.title, stage.deadline) for stage in contest.stages if stage.deadline > datetime.now().date()]
                if len(stages_list): 
                    nearest_datetime = min(stages_list, key=lambda x: x[1] - datetime.now().date())
                    time_left = (nearest_datetime[1] - datetime.now().date()).days
                    print(time_left)
                    if time_left < 2:
                        bot.send_message(user.user_id, f"До ближайшего этапа олимпиады {contest.title} осталось менее 2 дней")

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
        page = 1
        with app.app_context():
            user = UserTg.query.filter_by(user_id = message.from_user.id).first()
            contests = [x for x in user.contests]
        count = len(contests)
        if count:
            with app.app_context():
                user = UserTg.query.filter_by(user_id = message.from_user.id).first()
                contests = [x for x in user.contests]
                subjects = ", ".join([subject.name for subject in contests[page-1].subjects])
                stages = "\n".join([f"{stage.title}: {stage.deadline.strftime('%d.%m.%Y')}" for stage in contests[page-1].stages])
                stages_list = [(stage.title, stage.deadline) for stage in contests[page-1].stages if stage.deadline > datetime.now().date()]
            if len(stages_list): 
                nearest_datetime = min(stages_list, key=lambda x: x[1] - datetime.now().date())
                time_left = (nearest_datetime[1] - datetime.now().date()).days
            else:
                time_left = '-'
                nearest_datetime = ('-', '-')
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text='Удалить', callback_data='del__' + str(contests[0].id)))
            if count <= 1:
                        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
            else:
                markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                        InlineKeyboardButton(text=f'Вперёд --->', callback_data='{"method":"PagMy","NumberPage":' + str(page + 1) + ',"CountPage":' + str(count) + ',"User":' + str(user.id) + '}'))
            bot.send_message(message.chat.id, f'Мои олимпиады\n\n'
                                              f'<b>{contests[page - 1].title}</b>\n'
                                              f'<i>{contests[page - 1].description}</i>\n'
                                              f'<a href="{contests[page - 1].link}">Перейти на сайт</a>\n'
                                              f'<b>Классы:</b> <i>{contests[page - 1].grade}</i>\n'
                                              f'{contests[page - 1].type} ({contests[page - 1].level} уровень)\n'
                                              f'{subjects}\n'
                                              f'<b>Этапы:</b>\n<i>{stages}</i>\n'
                                              f'Дней до ближайшего дедлайна: <b>{time_left}</b> (Этап: {nearest_datetime[0]})\n',
                                              parse_mode="HTML", reply_markup = markup)
        else:
            bot.send_message(message.chat.id, f'Мои олимпиады"\n\n'
                                              f'<b>Вы пока не добавили себе олимпиад!</b>', parse_mode="HTML")
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
                page = 1
                with app.app_context():
                    group = Group.query.filter_by(code=call.data.split('__')[1]).first()
                    contests = Contest.query.filter_by(group_id=group.id).all()
                count = len(contests)
                if count:
                    with app.app_context():
                        contests = Contest.query.filter_by(group_id=group.id).all()
                        subjects = ", ".join([subject.name for subject in contests[page-1].subjects])
                        stages = "\n".join([f"{stage.title}: {stage.deadline.strftime('%d.%m.%Y')}" for stage in contests[page-1].stages])
                        user = UserTg.query.filter_by(user_id = call.from_user.id).first()
                        user_has_contest = contests[page - 1] in user.contests
                    markup = InlineKeyboardMarkup()
                    if user_has_contest:
                        markup.add(InlineKeyboardButton(text='Добавлен', callback_data=f' '))
                    else:
                        markup.add(InlineKeyboardButton(text='Добавить', callback_data='add__' + str(contests[0].id)))
                    if count <= 1:
                        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
                    else:
                        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                                   InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"PagDep\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "<b>{group.title}</b>"\n\n'
                                                           f'<b>{contests[page - 1].title}</b>\n'
                                                           f'<i>{contests[page - 1].description}</i>\n'
                                                           f'<a href="{contests[page - 1].link}">Перейти на сайт</a>\n'
                                                           f'<b>Классы:</b> <i>{contests[page - 1].grade}</i>\n'
                                                           f'{contests[page - 1].type} ({contests[page - 1].level} уровень)\n'
                                                           f'{subjects}\n'
                                                           f'<b>Этапы:</b>\n<i>{stages}</i>\n',
                                                           parse_mode="HTML", reply_markup = markup)
                else:
                    bot.send_message(call.message.chat.id, f'Просмотр олимпиад кафедры "<b>{group.title}</b>"\n\n'
                                                           f'<b>Олимпиад в этой категории пока нет!</b>', parse_mode="HTML")
            elif "PagDep" in call.data:
                json_string = json.loads(call.data)
                count = json_string['CountPage']
                page = json_string['NumberPage']
                group_id = json_string['Group']
                with app.app_context():
                    group = Group.query.filter_by(id=group_id).first()
                    contests = Contest.query.filter_by(group_id=group.id).all()
                    subjects = ", ".join([subject.name for subject in contests[page-1].subjects])
                    stages = "\n".join([f"{stage.title}: {stage.deadline.strftime('%d.%m.%Y')}" for stage in contests[page-1].stages])
                    user = UserTg.query.filter_by(user_id = call.from_user.id).first()
                    user_has_contest = contests[page - 1] in user.contests
                markup = InlineKeyboardMarkup()
                if user_has_contest:
                    markup.add(InlineKeyboardButton(text='Добавлен', callback_data=f' '))
                else:
                    markup.add(InlineKeyboardButton(text='Добавить', callback_data='add__' + str(contests[page-1].id)))
                if count <= 1:
                    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
                elif page == 1:
                    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"PagDep\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                elif page == count:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"PagDep\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
                else:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"PagDep\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"PagDep\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"Group\":" + str(group.id) + "}"))
                bot.edit_message_text(f'Просмотр олимпиад кафедры "<b>{group.title}</b>"\n\n'
                                      f'<b>{contests[page - 1].title}</b>\n'
                                      f'<i>{contests[page - 1].description}</i>\n'
                                      f'<a href="{contests[page - 1].link}">Перейти на сайт</a>\n'
                                      f'<b>Классы:</b> <i>{contests[page - 1].grade}</i>\n'
                                      f'{contests[page - 1].type} ({contests[page - 1].level} уровень)\n'
                                      f'{subjects}\n'
                                      f'<b>Этапы:</b>\n<i>{stages}</i>\n',
                                      parse_mode="HTML",reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif "PagMy" in call.data:
                json_string = json.loads(call.data)
                count = json_string['CountPage']
                page = json_string['NumberPage']
                user_id = json_string['User']
                with app.app_context():
                    user = UserTg.query.filter_by(id = user_id).first()
                    contests = [x for x in user.contests]
                    subjects = ", ".join([subject.name for subject in contests[page-1].subjects])
                    stages = "\n".join([f"{stage.title}: {stage.deadline.strftime('%d.%m.%Y')}" for stage in contests[page-1].stages])
                    stages_list = [(stage.title, stage.deadline) for stage in contests[page-1].stages if stage.deadline > datetime.now().date()]
                if len(stages_list): 
                    nearest_datetime = min(stages_list, key=lambda x: x[1] - datetime.now().date())
                    time_left = (nearest_datetime[1] - datetime.now().date()).days
                else:
                    time_left = '-'
                    nearest_datetime = ('-', '-')
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(text='Удалить', callback_data='del__' + str(contests[page - 1].id)))
                if page == 1:
                    markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"PagMy\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"User\":" + str(user_id) + "}"))
                elif page == count:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"PagMy\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"User\":" + str(user_id) +"}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
                else:
                    markup.add(InlineKeyboardButton(text=f'<--- Назад', callback_data="{\"method\":\"PagMy\",\"NumberPage\":" + str(page - 1) + ",\"CountPage\":" + str(count) + ",\"User\":" + str(user_id) + "}"),
                               InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                               InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"PagMy\",\"NumberPage\":" + str(page + 1) + ",\"CountPage\":" + str(count) + ",\"User\":" + str(user_id) + "}"))
                bot.edit_message_text(f'Мои олимпиады\n\n'
                                      f'<b>{contests[page - 1].title}</b>\n'
                                      f'<i>{contests[page - 1].description}</i>\n'
                                      f'<a href="{contests[page - 1].link}">Перейти на сайт</a>\n'
                                      f'<b>Классы:</b> <i>{contests[page - 1].grade}</i>\n'
                                      f'{contests[page - 1].type} ({contests[page - 1].level} уровень)\n'
                                      f'{subjects}\n'
                                      f'<b>Этапы:</b>\n<i>{stages}</i>\n'
                                      f'Дней до ближайшего дедлайна: <b>{time_left}</b> (Этап: {nearest_datetime[0]})\n',
                                      parse_mode="HTML",reply_markup = markup, chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif call.data.split('__')[0] == "add":
                with app.app_context():
                    user_tg = UserTg.query.filter_by(user_id=call.from_user.id).first()
                    contest = Contest.query.filter_by(id=call.data.split('__')[1]).first()
                    title = contest.title
                    user_tg.contests.append(contest)
                    db.session.add(user_tg)
                    db.session.commit()
                bot.send_message(call.message.chat.id, f'Олимпиада "<b>{title}</b>" успешно добавлена в ваш список', parse_mode="HTML")
            elif call.data.split('__')[0] == "del":
                with app.app_context():
                    user_tg = UserTg.query.filter_by(user_id=call.from_user.id).first()
                    contest = Contest.query.filter_by(id=call.data.split('__')[1]).first()
                    title = contest.title
                    user_tg.contests.remove(contest)
                    db.session.add(user_tg)
                    db.session.commit()
                bot.send_message(call.message.chat.id, f'Олимпиада "<b>{title}</b>" успешно удалена из вашего списка', parse_mode="HTML")
    except Exception as e:
        print(repr(e))

@app.route("/" + token, methods=['POST'])
def getMessage():
  bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200
