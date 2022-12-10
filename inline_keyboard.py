from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

ZODIAC_SIGN = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
DAY = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

BTN_TODAY = KeyboardButton('Сегодня', callback_data='Сегодня')
BTN_TOMORROW = KeyboardButton('Завтра', callback_data='Сегодня')

BTN_1 = KeyboardButton('Овен♈', callback_data='Овен♈')
BTN_2 = KeyboardButton('Телец♉', callback_data='Телец♉')
BTN_3 = KeyboardButton('Близнецы♊', callback_data='Близнецы♊')
BTN_4 = KeyboardButton('Рак♋', callback_data='Рак♋')
BTN_5 = KeyboardButton('Лев♌', callback_data='Лев♌')
BTN_6 = KeyboardButton('Дева♍', callback_data='Дева♍')
BTN_7 = KeyboardButton('Весы♎', callback_data='Весы♎')
BTN_8 = KeyboardButton('Скорпион♏', callback_data='Скорпион♏')
BTN_9 = KeyboardButton('Стрелец♐', callback_data='Стрелец♐')
BTN_10 = KeyboardButton('Козерог♑', callback_data='Козерог♑')
BTN_11 = KeyboardButton('Водолей♒', callback_data='Водолей♒')
BTN_12 = KeyboardButton('Рыбы♓', callback_data='Рыбы♓')

ZODIAC_SIGN.row(BTN_1, BTN_2, BTN_3)
ZODIAC_SIGN.add(BTN_4, BTN_5, BTN_6)
ZODIAC_SIGN.add(BTN_7, BTN_8, BTN_9)
ZODIAC_SIGN.add(BTN_10, BTN_11, BTN_12)

DAY.row(BTN_TODAY, BTN_TOMORROW)
