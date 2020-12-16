from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/menu"),
            KeyboardButton(text="/exchanger"),

        ],

    ],
    resize_keyboard=True
)

start_menu_admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/add_item"),
        ],
    ],
    resize_keyboard=True
)
