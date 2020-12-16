from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql
from utils.db_api.database import db


# Створення таблиці клієнтів (User)
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))
    referral = Column(Integer)
    query: sql.Select

    def __repr__(self):
        return f"""
Клієнт: {self.full_name} {self.username} (id={self.id})
"""


# створення таблиці товарів
class Item(db.Model):
    __tablename__ = 'items'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)

    # Код категории (для отображения в колбек дате)
    category_code = Column(String(20))

    # Название категории (для отображения в кнопке)
    category_name = Column(String(50))

    # Код подкатегории (для отображения в колбек дате)
    subcategory_code = Column(String(50))

    # Название подкатегории (для отображения в кнопке)
    subcategory_name = Column(String(20))

    # Название, фото и цена товара
    name = Column(String(50))
    photo = Column(String(250))
    price = Column(Integer)

    def __repr__(self):
        return f"""
Товар № {self.id} - "{self.name}"
Цена: {self.price}"""


# створення таблиці покупців
class Purchase(db.Model):
    __tablename__ = 'purchases'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    item_id = Column(Integer)
    amount = Column(Integer)  # Ціна в копійках (потім ділимо на 100)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)


