from telebot import types

# Меню регистрации
btn_reg = types.InlineKeyboardButton('😀 Регистрация', callback_data='register')
reg_buttons = types.InlineKeyboardMarkup(row_width=2)
reg_buttons.add(btn_reg)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_list_olymp = types.KeyboardButton('Все олимпиады')
btn_my_olymp = types.KeyboardButton('Мои олимпиады')
main_menu.add(btn_list_olymp, btn_my_olymp)

# Список предметных областей
subjects = types.InlineKeyboardMarkup(row_width=3)
math = types.InlineKeyboardButton('Математика', callback_data='math')
techno = types.InlineKeyboardButton('Дизайн и технологии', callback_data='techno')
science = types.InlineKeyboardButton('Естественные науки', callback_data='science')
subjects.add(math, techno, science)

register = types.InlineKeyboardMarkup(row_width=1)
reg = types.InlineKeyboardButton('Регистрация', callback_data='register')
register.add(reg)