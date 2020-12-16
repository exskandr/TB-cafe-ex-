from aiogram.dispatcher.filters.state import StatesGroup, State


class Purchase(StatesGroup):
    EnterQuantity = State()
    Approval = State()
    Payment = State()


class NewItem(StatesGroup):
    Name = State()

    Category_name = State()  # -> Dish = State()
    Category_code = State()  # -> Name = State()

    Subcategory_name = State()
    Subcategory_code = State()

    Photo = State()
                            # -> Ingredient = State()
    Price = State()
    Confirm = State()


