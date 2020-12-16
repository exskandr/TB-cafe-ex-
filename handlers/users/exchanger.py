import requests

from loader import dp
from aiogram import types


@dp.message_handler(commands=["exchanger"])
async def exchanger(message: types.Message):
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    response = requests.get(url).json()
    price_usd = response[0]['sale']
    price_eur = response[1]['sale']
    #await get_usd()
    await message.answer(f"курс продажі валюти згідно ПриватБанку: "
                         f"USD - {price_usd} grn, "
                         f"EUR - {price_eur} grn ")




