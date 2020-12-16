import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, \
    PreCheckoutQuery

import states
from data.config import lp_token
from keyboards.inline.menu_keyboards import buy_item
from loader import dp, bot
from utils.db_api import db_commands, models


@dp.callback_query_handler(buy_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    item = await db_commands.Item.get(item_id)
    if not item:
        await call.message.answer("Такої страви не має можливості заказати")
        return

    text = ("Ви хочете заказати \"<b>{name}</b>\" по ціні: <i>{price:,}/шт.</i>\n"
            "Введіть кількість порцій, або натисніть /Cancel").format(name=item.name,
                                                                      price=item.price / 100)
    await call.message.answer(text)
    await states.Purchase.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        item=item,
        purchase=models.Purchase(
            item_id=item_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase"].quantity = quantity
        item = data["item"]
        amount = item.price * quantity
        data["purchase"].amount = amount

    # Создаем кнопки
    agree_button = InlineKeyboardButton(
        text="Погоджуюся",
        callback_data="agree"
    )
    change_button = InlineKeyboardButton(
        text="Ввести кількість зново",
        callback_data="change"
    )
    cancel_button = InlineKeyboardButton(
        text="Відмінити оплату",
        callback_data="cancel"
    )

    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [agree_button],  # Первый ряд кнопок
            [change_button],  # Второй ряд кнопок
            [cancel_button]  # Третий ряд кнопок
        ]
    )
    await message.answer(
        "Ви бажаєте придбати <i>{quantity}</i> {name} по ціні <b>{price:,} грн/шт.</b>\n\n"
        "В сумі: <b>{amount:,}</b>. Підтверджуєте?".format(
            quantity=quantity,
            name=item.name,
            amount=amount / 100,
            price=item.price / 100
        ),
        reply_markup=markup)
    await states.Purchase.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer("Невірне значення, введіть число")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Відміна покупки")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase.Approval)
async def approval(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Введіть кількість товару заново.")
    await states.Purchase.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase: models.Purchase = data.get("purchase")
    item: models.Item = data.get("item")
    # Тепер можно внести данні про покупку в базу данных через .create()
    await purchase.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=("Здійсніть оплату <b>{amount:,}</b> по методу вказаному нижче і натисніть "
                                 "на кнопку нижче").format(amount=purchase.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "UAH"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = False

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.name,
                           description=item.name,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=item.name, amount=purchase.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase=purchase)
    await states.Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase: models.Purchase = data.get("purchase")
    success = await check_payment(purchase)

    if success:
        await purchase.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, "Дякуємо за оплату, СМАЧНОГО!")
    else:
        await bot.send_message(query.from_user.id, "Оплата не була підтверджена, "
                                                   "спробуйте здійснити оплату пізніше...")


@dp.message_handler()
async def other_echo(message: Message):
    await message.answer(message.text)


async def check_payment(purchase: models.Purchase):
    return True
