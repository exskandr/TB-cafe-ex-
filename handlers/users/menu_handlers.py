from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, Message

from data.config import admins
from keyboards.inline.menu_keyboards import menu_cd, categories_keyboard, subcategories_keyboard, \
    items_keyboard, item_keyboard
from loader import dp
from utils.db_api.db_commands import get_item


# Хендлер на команду /menu
@dp.message_handler(Command("menu"))
async def show_menu(message: types.Message):
    await list_categories(message)


async def list_categories(message: Union[CallbackQuery, Message], **kwargs):
    markup = await categories_keyboard()

    # перевіряємо, що за тип апдейта. якщо Message - відправляємо нове повідомлення
    if isinstance(message, Message):
        await message.answer("У нас в меню є: ", reply_markup=markup)

    # якщо CallbackQuery - змінюємо це повідомлення
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


# Функція, яка віддає кнопки з підкатегорії, по вибраній категорії
async def list_subcategories(callback: CallbackQuery, category, **kwargs):
    markup = await subcategories_keyboard(category)

    # Змінюємо повідомлення і передаємо кнопки з новими підкатегоріями
    await callback.message.edit_reply_markup(markup)


# Функція, яка передає кнопки з Назвою і ціною товара, по вибраній категорії і підкатегорії
async def list_items(callback: CallbackQuery, category, subcategory, **kwargs):
    markup = await items_keyboard(category, subcategory)

    # Змінюємо повідомлення і передаємо кнопки з новими підкатегоріями
    await callback.message.edit_text(text="Що, Ви, бажаєте?", reply_markup=markup)


# Функція, яка передає кнопки Купити товар по вибранному товару
async def show_item(callback: CallbackQuery, category, subcategory, item_id):
    markup = item_keyboard(category, subcategory, item_id)

    # Берем товар із БД
    item = await get_item(item_id)
    text = f"Заказ прийнятий на: {item.subcategory_name} - {item.name}"
    await callback.message.edit_text(text=text, reply_markup=markup)
    for admin in admins:
        await dp.bot.send_message(admin, text)


# Функція, яка обробляє ВСІ активації кнопок в цій менюшці
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    """

    :param call: Тип обєкта CallbackQuery, який летить в хендлер
    :param callback_data: Словник з данними, які зберігаються в нажатій кнопці
    """

    current_level = callback_data.get("level")
    category = callback_data.get("category")
    subcategory = callback_data.get("subcategory")
    item_id = int(callback_data.get("item_id"))

    # Прописуємо "рівні" в які будуть відправлятися нові кнопки користавача
    levels = {
        "0": list_categories,  # Віддаємо категорії
        "1": list_subcategories,  # Віддаємо підкатегорії
        "2": list_items,  # Віддаємо товар
        "3": show_item,   # Пропонуємо купити товар
    }

    # Забираєм потрібну функцію для вибранного рівня
    current_level_function = levels[current_level]

    # Виконуємо потрібну функцію і передаємо параметри, отримані з кнопки
    await current_level_function(
        call,
        category=category,
        subcategory=subcategory,
        item_id=item_id
    )
