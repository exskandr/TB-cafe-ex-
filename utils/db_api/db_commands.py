from typing import List

import requests
from aiogram import types

from sqlalchemy import and_

from utils.db_api.models import Item, User
from utils.db_api.database import db


# Функция для создания нового товара в базе данных. Принимает все возможные аргументы, прописанные в Item
async def add_item(**kwargs):
    new_item = await Item(**kwargs).create()
    return new_item


# Функция для вывода товаров с РАЗНЫМИ категориями
async def get_categories() -> List[Item]:
    return await Item.query.distinct(Item.category_name).gino.all()


# Функция для вывода товаров с РАЗНЫМИ подкатегориями в выбранной категории
async def get_subcategories(category) -> List[Item]:
    return await Item.query.distinct(Item.subcategory_name).where(Item.category_code == category).gino.all()


# Функция для подсчета товаров с выбранными категориями и подкатегориями
async def count_items(category_code, subcategory_code=None):
    # Прописываем условия для вывода (категория товара равняется выбранной категории)
    conditions = [Item.category_code == category_code]

    # Если передали подкатегорию, то добавляем ее в условие
    if subcategory_code:
        conditions.append(Item.subcategory_code == subcategory_code)

    # Функция подсчета товаров с указанными условиями
    total = await db.select([db.func.count()]).where(
        and_(*conditions)
    ).gino.scalar()
    return total


# Функция вывода всех товаров, которые есть в переданных категории и подкатегории
async def get_items(category_code, subcategory_code) -> List[Item]:
    item = await Item.query.where(
        and_(Item.category_code == category_code,
             Item.subcategory_code == subcategory_code)
    ).gino.all()
    return item


# Функция для получения объекта товара по его айди
async def get_item(item_id) -> Item:
    item = await Item.query.where(Item.id == item_id).gino.first()
    return item


async def get_user(user_id) -> User:
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def add_new_user(referral=None):
    user = types.User.get_current()
    old_user = await get_user(user.id)
    if old_user:
        return old_user
    new_user = User()
    new_user.user_id = user.id
    new_user.username = user.username
    new_user.full_name = user.full_name

    if referral:
        new_user.referral = int(referral)
    await new_user.create()
    return new_user


async def get_usd():
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    response = requests.get(url).json()
    price_usd = response[0]['sale']
    price_eur = response[1]['sale']
    # print(response)
    print('usd - ' + str(price_usd) + ' grn', end='\n')
    print('eur - ' + str(price_eur) + ' grn', end='\n')
    return (str(price_usd) + ' usd',
            str(price_eur) + 'eur')
