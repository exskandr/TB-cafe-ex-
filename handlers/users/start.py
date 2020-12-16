from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import admins
from keyboards.default.start_menu import start_menu
from loader import dp, bot
from utils.db_api import db_commands


# хендлер старт
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    user = await db_commands.add_new_user()
    #id = user.id
    #bot_username = (await bot.me).username
    #bot_link = f"https://t.me/{bot_username}?start={id}"
    text = (f'Привіт, {message.from_user.full_name}! '
            f'Жми /menu для заказу їжі '
            f'або /exchanger , щоб взнати курс валюти')
    if message.from_user.id == admins:
        text += ("\n"
                 "Добавити нову страву в меню: /add_item")
    await bot.send_message(chat_id, text, reply_markup=start_menu)

# async def bot_start(message: types.Message):
#     await message.answer(f'Привет, {message.from_user.full_name}! '
#                          f'Жми /menu '
#                          f'или /add_item',
#                          reply_markup=start_menu)
