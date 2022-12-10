import random
from datetime import datetime, timedelta

import aiogram.utils.exceptions

import messages
import config
import inline_keyboard
from ban_words import lst_ban_words

import sqlite3
import logging
import asyncio
import aioschedule
from contextlib import suppress
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os
import json
import wave
from pathlib import Path
from vosk import Model, KaldiRecognizer

scheduler = AsyncIOScheduler()
scheduler.start()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

delay_flood = 10
conn = sqlite3.connect('./mydatabase.db')
cur = conn.cursor()

model = Model(r"vosk-model-small-ru-0.22")


class Form(StatesGroup):
    zodiac = State()
    day = State()


async def anti_flood_command(*args, **kwargs):
    m = args[0]
    await delete_message(m)


@dp.message_handler(commands=['help', 'start'])
@dp.throttled(anti_flood_command, rate=delay_flood)
async def show_help(message: types.Message):
    await message.answer(text=messages.helper())


@dp.message_handler(commands=['gsl'])
async def sonya(message: types.Message):
    cur.execute(f"SELECT * FROM users where userid='1232593975';")
    sonya_data = cur.fetchall()
    wallet = sonya_data[0][3]+1000
    sql_update_query = f"""Update users set balance = {wallet} where userid = 1232593975"""  # Обновление баланса
    cur.execute(sql_update_query)
    conn.commit()
    await message.answer("Добавил тебе 1000 LY любимая❤")


@dp.message_handler(commands=['getdatacasino'])
async def show_data_casino(message: types.Message):
    await message.answer_document(open("mydatabase.db", 'rb'))


async def daily_accrual():
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    for i in users:
        balance = i[3]
        sql_update_query = f"""Update users set balance = {balance+1000} where userid = {i[0]}"""  # Обновление баланса
        cur.execute(sql_update_query)
        conn.commit()


async def scheduler_timer():
    aioschedule.every().day.at("00:00").do(daily_accrual)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(scheduler_timer())


@dp.message_handler(commands=['casinorule'])
async def casinorule(message: types.Message):
    casino_scale_img = open("casino_scale.jpg", 'rb')
    hello_msg = f'Правила:\n' \
                f'Ежедневно в 00:00 по МСК начисляется 1000 LY\n' \
                f'Для того что-бы попытать свою удачу напишите: /casino 100 (где 100 это ваша ставка)\n' \
                f'Для того что-бы посмотреть свой баланс просто напишите: /casino\n' \
                f'Множители комбинаций вы можете увидеть выше\n\n' \
                f'Удачи и приятной игры✊'
    await bot.send_photo(chat_id=message.chat.id, photo=casino_scale_img, caption=hello_msg, disable_notification=True)
    casino_scale_img.close()


@dp.message_handler(commands=['casino'])
@dp.throttled(anti_flood_command, rate=3)
async def response_casino(message: types.Message):
    msg_user_id = message.from_user.id  # Получение id отправителя сообщения
    cur.execute(f"SELECT * FROM users where userid='{msg_user_id}';")
    user_data = cur.fetchall()
    bet = message.text.replace('/casino', '')
    bet = bet.replace('@DJLYbot', '')
    bet = bet.strip()
    if not user_data:
        user = (msg_user_id, message.from_user.full_name, message.from_user.username, '1000', '0')
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?);", user)
        conn.commit()
        casino_scale_img = open("casino_scale.jpg", 'rb')
        hello_msg = f'Привет, {message.from_user.full_name}👋\n' \
                    f'Добро пожаловать в CASINO🎰\n' \
                    f'Правила:\n' \
                    f'Ежедневно в 00:00 по МСК начисляется 1000 LY\n' \
                    f'Для того что-бы попытать свою удачу напишите: /casino 100 (где 100 это ваша ставка)\n' \
                    f'Для того что-бы посмотреть свой баланс просто напишите: /casino\n' \
                    f'Для просмотра правил напишите: /casinorule\n' \
                    f'Множители комбинаций вы можете увидеть выше\n\n' \
                    f'Ваш баланс: 1000 LY\n\n' \
                    f'Удачи и приятной игры✊'
        await bot.send_photo(chat_id=message.chat.id,
                             photo=casino_scale_img,
                             caption=hello_msg,
                             disable_notification=True)
        casino_scale_img.close()
    else:
        balance = user_data[0][3]
        all_spins = user_data[0][4]
        if bet == '':
            await message.answer(f'Для игры введите ставку (Пример: /casino 100)\n'
                                 f'Для просмотра правил напишите: /casinorule\n'
                                 f'Ваш баланс: {balance} LY\n'
                                 f'Спинов за все время: {all_spins}', disable_notification=True)
        else:
            try:
                bet = float(bet)
                await show_roll(message, user_data, bet, msg_user_id, all_spins)
            except Exception:
                await message.answer(f'Ставка должна быть числом', disable_notification=True)


async def show_roll(message: types.Message, user_data, bet: float, msg_user_id, all_spins):
    wallet = user_data[0][3]
    date = datetime.now() + timedelta(seconds=2.5)
    point = bet
    random_phrases_win = ["Сегодня определенно твой день😎",
                          "Ты меня обокрасть хочешь?😄",
                          "Мне бы твою удачу😊",
                          "А ты со мной поделишься?😍",
                          "Да как такое возможно?😱"]

    random_phrases_lose = ["А что я? Я тут не при чем😂",
                           "Ну давай, скажи популярную фразу про казино😏",
                           "Может пора остановиться?🤨",
                           "Попробуй напиши разрабу, может подкрутит😉",
                           "Хорошо что это не реальные деньги, правда?😜"]
    await delete_message(message)
    if point == '':
        await message.answer(text="Сделайте ставку")
    else:
        point = float(point)
        if 0 < point <= wallet:
            roll = await message.answer_dice(emoji='🎰')
            result_msg = await message.answer(f'ИГРАЕМ\n{message.from_user.full_name}\n'
                                              f'Ставка: {point} LY\n'
                                              f'Ваш баланс: {wallet} LY', disable_notification=True)
            result = roll.dice.value
            scale = {11: 1.25,
                     27: 1.25,
                     35: 1.25,
                     39: 1.25,
                     41: 1.25,
                     42: 1.25,
                     44: 1.25,
                     47: 1.25,
                     59: 1.25,
                     16: 1.5,
                     32: 1.5,
                     48: 1.5,
                     52: 1.5,
                     56: 1.5,
                     60: 1.5,
                     61: 1.5,
                     62: 1.5,
                     63: 1.5,
                     1: 2,
                     22: 5,
                     43: 7,
                     64: 10}
            try:
                win = scale[result]
                wallet += point * win
                all_spins += 1
                win_msg = f'{random.choice(random_phrases_win)}\n' \
                          f'{message.from_user.full_name}\n' \
                          f'Ставка: {point} LY\n' \
                          f'Ваш выйгрыш: {point * win} LY\n' \
                          f'Ваш баланс: {wallet} LY'
                scheduler.add_job(edit_msg, "date", run_date=date, kwargs={"message": result_msg, "m_text": win_msg})
                sql_update_query = f"""Update users set balance = {wallet}, spins={all_spins} where userid = {msg_user_id}"""  # Обновление баланса
                cur.execute(sql_update_query)
                conn.commit()
            except KeyError:
                wallet -= point
                all_spins += 1
                lose_msg = f'{random.choice(random_phrases_lose)}\n' \
                           f'{message.from_user.full_name}\n' \
                           f'Ставка: {point} LY\n' \
                           f'Ваш баланс: {wallet} LY'
                scheduler.add_job(edit_msg, "date", run_date=date, kwargs={"message": result_msg, "m_text": lose_msg})
                sql_update_query = f"""Update users set balance = {wallet}, spins={all_spins} where userid = {msg_user_id}"""  # Обновление баланса
                cur.execute(sql_update_query)
                conn.commit()
        else:
            await message.answer(f'Вы не можете сделать такую ставку\nВаш баланс: {wallet} LY', disable_notification=True)


async def edit_msg(message: types.Message, m_text: str):
    await message.edit_text(m_text)


@dp.message_handler(commands=['weather'])
@dp.throttled(anti_flood_command, rate=delay_flood)
async def show_weather(message: types.Message):
    await message.answer(text=messages.weather())


@dp.message_handler(commands=['horoscope'])
@dp.throttled(anti_flood_command, rate=delay_flood)
async def show_horoscope(message: types.Message):
    await Form.zodiac.set()
    await message.answer(text="Какой у тебя знак зодиака?", reply_markup=inline_keyboard.ZODIAC_SIGN)


@dp.message_handler(state=Form.zodiac)
async def process_zodiac(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['zodiac'] = message.text
    await Form.next()
    await message.answer("На какой день ты хочешь увидеть гороскоп?", reply_markup=inline_keyboard.DAY)


@dp.message_handler(state=Form.day)
async def process_day(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
    await message.answer(messages.horoscope_message(data['zodiac'], data['day']), reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(content_types=["text"])
async def delete_ban_word(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    for i in lst_ban_words:
        if i in message.text.lower():
            with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
                await message.delete()
            break


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def somebody_added(message: types.Message):
    for user in message.new_chat_members:
        await message.answer(f"Привет, {user.full_name}")


async def convert_ogg_to_wav(msg_name: str, path: str):
    os.system(f'ffmpeg -i {path}/{msg_name}.ogg -ar 16000 -ac 2 -ab 192K -f wav {path}/{msg_name}.wav')
    # os.remove(f'{path}/{msg_name}.ogg')

async def speech_to_text(model: Model, msg_name: str, path: str):

    wf = wave.open(f'{path}/{msg_name}.wav', "rb")
    rec = KaldiRecognizer(model, 44100)
    result = ''
    last_n = False
    while True:
        data = wf.readframes(44100)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if res['text'] != '':
                result += f" {res['text']}"
                last_n = False
            elif not last_n:
                result += '\n'
                last_n = True
    res = json.loads(rec.FinalResult())
    result += f" {res['text']}"
    wave.Wave_read.close(wf)
    os.remove(f'{path}/{msg_name}.ogg')
    os.remove(f'{path}/{msg_name}.wav')
    return result


async def handle_file(file: types.File, file_name: str, path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)
    await bot.download_file(file_path=file.file_path, destination=f"{path}/{file_name}")


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_message_handler(message: types.Message):
    voice = await message.voice.get_file()
    path = "./files/voices"
    await handle_file(file=voice, file_name=f"{voice.file_id}.ogg", path=path)
    await convert_ogg_to_wav(msg_name=f"{voice.file_id}", path=path)
    msg_response = await speech_to_text(model=model, msg_name=f"{voice.file_id}", path=path)
    try:
        await message.reply(msg_response)
    except aiogram.utils.exceptions.BadRequest:
        await message.reply('Не удалось распознать слова в сообщении')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
