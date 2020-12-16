from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import admins
from loader import dp
from states.state_it import NewItem

from utils.db_api.models import Item


@dp.message_handler(user_id=admins, commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Ви відмінили створиння позиції")
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=["add_item"])
async def add_item(message: types.Message):
    await message.answer("Введіть страву (напій), яку бажаєте добавити, або відмініть операцію /cancel")
    await NewItem.Category_name.set()


@dp.message_handler(user_id=admins, state=NewItem.Category_name)
async def add_category_name(message: types.Message, state: FSMContext):
    category_name = message.text
    item = Item()
    item.category_name = category_name

    await message.answer("Введіть назву страви(напою) латиницею, або відмініть операцію /cancel")
    await NewItem.Category_code.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Category_code)
async def add_category_code(message: types.Message, state: FSMContext):
    category_code = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.category_code = category_code

    await message.answer("До чого відноситься блюдо, або відмініть операцію /cancel")
    await NewItem.Subcategory_name.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Subcategory_name)
async def add_subcategory_name(message: types.Message, state: FSMContext):
    subcategory_name = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.subcategory_name = subcategory_name

    await message.answer("До чого відноситься блюдо латинськими, або відмініть операцію /cancel")
    await NewItem.Subcategory_code.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Subcategory_code)
async def add_subcategory_code(message: types.Message, state: FSMContext):
    subcategory_code = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.subcategory_code = subcategory_code

    await message.answer("Введіть назву, або відмініть операцію /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Name)
async def add_dish(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.name = name

    await message.answer("Назва: {name}"
                         "\nВишліть фотографію блюда (не документ) або відмініть операцію /cancel".format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption="Назва: {name}"
                "\nПришліть ціну страви(напою) /cancel".format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Некоректне введення даних, потрібно ввести число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Підтвердити", callback_data="confirm")],
            [InlineKeyboardButton(text="Змінити", callback_data="change")],
        ]
    )
    await message.answer(("Ціна: {price:,}\n"
                          "Все коректно? Нажміть /cancel щоб відминити операцію"
                          ).format(price=price / 100), reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admins, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введіть заново ціну")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admins, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Страву(напій) успішно додано у меню.")
    await state.reset_state()
