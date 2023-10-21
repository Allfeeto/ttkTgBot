import telebot
from telebot import types

bot = telebot.TeleBot('6615067520:AAEj7GMOkYx-YwxNpQiCMqh_XaV0BBgSb9s')

user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Войти')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Зарегистрироваться')
    markup.row(btn2)

    bot.send_message(message.chat.id, 'Привет', reply_markup=markup)
    bot.register_next_step_handler(message, process_start_command)


def process_start_command(message):
    if message.text == 'Войти':
        bot.send_message(message.chat.id, 'Введите логин:')
        bot.register_next_step_handler(message, process_login_step)
    elif message.text == 'Зарегистрироваться':
        bot.send_message(message.chat.id, 'Введите данные для регистрации (логин и пароль, разделенные пробелом):')
        bot.register_next_step_handler(message, process_registration_step)


def process_login_step(message):
    login = message.text
    if login not in user_data:
        bot.send_message(message.chat.id, 'Логин не найден. Пожалуйста, зарегистрируйтесь.')
        return

    user_data[message.chat.id] = {'login': login}
    bot.send_message(message.chat.id, f'Вы вошли под логином {login}')


def process_registration_step(message):
    data = message.text.split()
    if len(data) != 2:
        bot.send_message(message.chat.id, 'Некорректный формат ввода. Попробуйте еще раз.')
        return

    login, password = data
    if login in user_data:
        bot.send_message(message.chat.id, 'Логин уже занят. Пожалуйста, выберите другой.')
        return

    user_data[message.chat.id] = {'login': login, 'password': password}
    bot.send_message(message.chat.id, f'Вы успешно зарегистрированы под логином {login}')

    # Дополнительный код для обработки регистрации, например, отправка подтверждения или дополнительных инструкций


# Оставшаяся часть твоего кода
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти на сайт', url='https://translate.yandex.ru/')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Удалить фото', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Изменить текст', callback_data='edit')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Идёт обработка фото!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Изменённый текст', callback.message.chat.id, callback.message.message_id)


bot.polling(none_stop=True)
