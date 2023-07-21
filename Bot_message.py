import logging
from aiogram import Bot, Dispatcher, executor, types
from BOT_const import *
from aiogram.types import ReplyKeyboardRemove
from BOT_db import add_new_string, delete_user, check_if_user, check_if_in
from main import get_page_and_link, make_message_for_user
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3

API_TOKEN = token

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Подключить рассылку")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(start_mes, reply_markup=keyboard)


@dp.message_handler(commands=['about'])
async def send_welcome(message: types.Message):
    id = message.from_user.id
    k = check_if_user(id)
    if k == 0:
        kb = [
            [types.KeyboardButton(text="Подключить рассылку")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            about_mes_1, reply_markup=keyboard)
    else:
        kb = [
            [types.KeyboardButton(text="Посмотреть следующую новость")],
            [types.KeyboardButton(text="Отписаться")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            about_mes_2,
            reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Подключить рассылку")
async def send_on(message: types.Message):
    id = message.from_user.id
    k = check_if_user(id)
    if k != 0:
        kb = [
            [types.KeyboardButton(text="Посмотреть следующую новость")],
            [types.KeyboardButton(text="Отписаться")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Вы уже подключены к рассылке, чтобы отписаться, нажмите на кнопку Отписаться", reply_markup=keyboard)
    else:
        await message.answer(connect_mes, reply_markup=ReplyKeyboardRemove())
        url = get_page_and_link()
        mes = make_message_for_user(url)
        if mes == 0:
            while mes == 0:
                url = get_page_and_link()
                mes = make_message_for_user(url)
        add_new_string(id, url)
        kb = [
            [types.KeyboardButton(text="Посмотреть следующую новость")],
            [types.KeyboardButton(text="Отписаться")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Вот ваша первая новость: \n" + mes, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Посмотреть следующую новость")
async def send_on(message: types.Message):
    await message.answer("Новость генерируется...", reply_markup=ReplyKeyboardRemove())
    id = message.from_user.id
    url = get_page_and_link()
    k = check_if_in(id, url)
    mes = make_message_for_user(url)
    kb = [
        [types.KeyboardButton(text="Посмотреть следующую новость")],
        [types.KeyboardButton(text="Отписаться")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    if k > 0 or mes == 0:
        while k != 0 or mes == 0:
            url = get_page_and_link()
            mes = make_message_for_user(url)
            k = check_if_in(id, url)
    await message.answer(mes, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Отписаться")
async def send_on(message: types.Message):
    id = message.from_user.id
    delete_user(id)
    await message.answer("Вы отключены от рассылки. Чтобы подключиться заново, напишите /start", reply_markup=ReplyKeyboardRemove())


@dp.message_handler()
async def echo(message: types.Message):
    id = message.from_user.id
    k = check_if_user(id)
    if k == 0:
        kb = [
            [types.KeyboardButton(text="Подключить рассылку")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(confuse_mes_1, reply_markup=keyboard)
    else:
        kb = [
            [types.KeyboardButton(text="Посмотреть следующую новость")],
            [types.KeyboardButton(text="Отписаться")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(confuse_mes_2, reply_markup=keyboard)


async def sched():
    conn = sqlite3.connect(path, timeout=30)
    cursor = conn.cursor()
    cursor.execute('select userid from users')
    list = []
    for user in cursor:  # you can replace user_list with the information in the database
        if user[0] not in list:
            list.append(user[0])
    cursor.close()
    conn.close()
    for i in range (len(list)):
        url = get_page_and_link()
        mes = make_message_for_user(url)
        k = check_if_in(list[i], url)
        if k > 0 or mes == 0:
            while k != 0 or mes == 0:
                url = get_page_and_link()
                mes = make_message_for_user(url)
                k = check_if_in(list[i], url)
        kb = [
            [types.KeyboardButton(text="Посмотреть следующую новость")],
            [types.KeyboardButton(text="Отписаться")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        add_new_string(list[i], url)
        await bot.send_message(chat_id=list[i], text="Ежедневная новость!\n" + mes, reply_markup=keyboard)

scheduler = AsyncIOScheduler()
scheduler.add_job(sched, trigger='cron', hour='19', minute=20)
scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)