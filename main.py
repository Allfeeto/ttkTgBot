import os
import sqlite3
import telebot
import io
from PIL import Image as PILImage
from telebot import types
from PIL import Image
import pytesseract as pt
from pytesseract import Output
import cv2
import numpy as np

# Устанавливаем переменную окружения для хранения токена
os.environ['BOT_TOKEN'] = '6615067520:AAEj7GMOkYx-YwxNpQiCMqh_XaV0BBgSb9s'

# Загрузим переменные окружения из файла .env (если используется)
# Для этого нужно установить библиотеку python-dotenv (pip install python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

pt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
mYconfig = r"--oem 3 --psm 6"

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
user_data = {}


def create_database():
    conn = sqlite3.connect('itproger.db')
    with conn:
        cur = conn.cursor()
        cur.execute(f'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, FIO VARCHAR(50), '
                    f'passport VARCHAR(50), train VARCHAR(50), van VARCHAR(50), place VARCHAR(50))')
        populate_database(cur)


def populate_database(cur):
    sample_data = [
        ('Мельников А.Р.', '60190369853', '003А', '09', '015'),
        ('Манаков В.А.', '60200470064', '015Ш', '07', '014'),
        ('Михин М.П.', '60199369853', '013Д', '06', '013'),
        ('Астапенко П.А.', '60200470964', '020E', '05', '007'),
        ('Фролов К.Л.', '60200470974', '035Г', '08', '012'),
    ]

    cur.execute(f'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, FIO VARCHAR(50), '
                f'passport VARCHAR(50), train VARCHAR(50), van VARCHAR(50), place VARCHAR(50))')

    cur.executemany("INSERT INTO users (FIO, passport, train, van, place) VALUES (?, ?, ?, ?, ?)", sample_data)


class Train:
    pass


# Добавим элементы в класс Train
Train.names = ["ПОЕЗД.", "ВАГОН", "МЕСТО"]


def process_image(img):
    global extracted_text
    height, width = img.shape[:2]

    data = pt.image_to_data(img, config=mYconfig, lang='rus', output_type=Output.DICT)

    table1 = img.copy()  # Используйте копию оригинального изображения по умолчанию

    keywords = ["поезд", "вагон", "место"]

    amount_boxes = len(data["text"])
    found_keywords = set()

    for i in range(amount_boxes):
        # Проверка наличия ключевого слова и его уверенности
        if (
                any(keyword.lower() in data["text"][i].lower() for keyword in keywords)
                and float(data["conf"][i]) > 40
        ):
            found_keywords.add(data["text"][i].lower())

        # Если все ключевые слова найдены, выходим из цикла
        if set(map(str.lower, keywords)) <= found_keywords:
            break

    # Выделение текста ниже найденных ключевых слов
    for i in range(amount_boxes):
        if float(data["conf"][i]) > 40 and data["text"][i].strip().lower() not in found_keywords:
            (x, y, w, h) = (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), -1)
            table1 = img[y + h + 10:, :]

            # Извлечение текста из области
            extracted_text = pt.image_to_string(table1, lang='rus')
            break  # Завершаем цикл после извлечения первой строки ниже ключевых слов

    # Выводим информацию в левом верхнем углу
    cv2.putText(img, extracted_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    return table1


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('itproger.db')
    create_database()
    sent_message = bot.send_message(message.chat.id, 'Привет, сейчас тебя зарегистрируем! Загрузите фото вашего '
                                                     'паспорта или билета.')

    user_data[message.chat.id] = {'sent_message_id': sent_message.message_id}


def send_message_with_link(chat_id, text, link, param=None, param1=None):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти', url=link)
    markup.row(btn1)

    if param is not None and param1 is not None:
        text += f'\nДополнительные параметры: {param}, {param1}'

    bot.send_message(chat_id, text, reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    try:
        # Get the photo file ID
        file_id = message.photo[-1].file_id

        # Download the photo
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save the photo locally
        photo_path = f'photo_{message.from_user.id}.jpg'
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            improved_photo_path = improve_photo_quality(photo_path)
            img = cv2.imread(improved_photo_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            table1 = process_image(gray)
        # Check the file extension and save accordingly
        if file_info.file_path.endswith(".png"):
            photo_path = f'photo_{message.from_user.id}.png'
        elif file_info.file_path.endswith(".heic"):
            # Convert .heic to .jpg
            photo_path = f'photo_{message.from_user.id}.jpg'
            with open(photo_path, 'wb') as new_file:
                new_file.write(convert_heic_to_jpg(downloaded_file))
        else:
            # Default to .jpg for other formats
            photo_path = f'photo_{message.from_user.id}.jpg'
            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)

        # Image processing with the new parser
        img = cv2.imread(photo_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        table1 = process_image(gray)

        pil_image = Image.fromarray(table1)
        np_array = np.array(table1)

        extracted_text = pt.image_to_string(table1, lang='rus')

        # Выводим только первую строку информации
        first_line = extracted_text.split('\n')[0]

        # Проверяем данные в базе данных
        if check_user_data(first_line):
            # Отправляем сообщение с возможностью вставки ссылки
            send_message_with_link(message.chat.id, 'Пора сделать заказ!', 'https://example.com')
        else:
            bot.send_message(message.chat.id, 'Повторите еще раз')

    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')


def improve_photo_quality(photo_path):
    img = cv2.imread(photo_path)

    # Увеличиваем размер изображения (увеличиваем в 2 раза)
    img = cv2.resize(img, (0, 0), fx=2, fy=2)

    # Применяем фильтр для улучшения четкости
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    img = cv2.filter2D(img, -1, kernel)

    # Сохраняем улучшенное фото
    improved_photo_path = f'improved_{os.path.basename(photo_path)}'
    cv2.imwrite(improved_photo_path, img)

    return improved_photo_path


def convert_heic_to_jpg(heic_data):
    # Use PIL to open and save as jpg
    with PILImage.open(io.BytesIO(heic_data)) as img:
        jpg_data = io.BytesIO()
        img.convert("RGB").save(jpg_data, format="JPEG")
    return jpg_data.getvalue()


def check_user_data(extracted_text):
    conn = sqlite3.connect('itproger.db')
    with conn:
        cur = conn.cursor()
        # Разделяем строку на части
        parts = extracted_text.split()
        if len(parts) >= 3:
            train, van, place = parts[:3]
            # Проверяем данные в базе данных
            cur.execute("SELECT * FROM users WHERE train = ? AND van = ? AND place = ?", (train, van, place))
            result = cur.fetchone()
            print("Extracted text:", extracted_text)
            print("Result from database:", result)
            return result is not None
        else:
            return False


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'shop':
        bot.send_message(call.message.chat.id, 'Добро пожаловать в магазин!')
    else:
        bot.send_message(call.message.chat.id, 'Неверная команда')


if __name__ == "__main__":
    create_database()
    bot.polling(none_stop=True)
