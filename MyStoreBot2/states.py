"""Состояния FSM."""
from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    name = State()
    phone = State()
    comment = State()


class AdminAddProduct(StatesGroup):
    category = State()
    name = State()
    price = State()
    sizes = State()
    colors = State()
    material = State()
    country = State()
    description = State()
    photo = State()


class AdminEditText(StatesGroup):
    value = State()
