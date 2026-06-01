"""Клавиатуры бота."""
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# === ПОЛЬЗОВАТЕЛЬ ===
async def main_menu():
    from database import get_text
    kb = InlineKeyboardBuilder()
    kb.button(text=f"📋 {await get_text('menu_catalog', 'Каталог')}", callback_data="catalog")
    kb.button(text=f"🔍 {await get_text('menu_selector', 'Подбор')}", callback_data="selector")
    kb.button(text=f"🛒 {await get_text('menu_cart', 'Корзина')}", callback_data="cart")
    kb.button(text=f"💬 {await get_text('menu_info', 'Информация')}", callback_data="info")
    kb.adjust(2, 2)
    return kb.as_markup()


def categories_kb(categories):
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c["name"], callback_data=f"cat:{c['id']}")
    kb.button(text="← В меню", callback_data="main")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products, cat_id):
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p['name']} - {int(p['price'])}₽", callback_data=f"prod:{p['id']}")
    kb.button(text="← Назад", callback_data="catalog")
    kb.adjust(1)
    return kb.as_markup()


def product_kb(prod_id, cat_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 В корзину", callback_data=f"add:{prod_id}")
    kb.button(text="← Назад", callback_data=f"cat:{cat_id}")
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items):
    kb = InlineKeyboardBuilder()
    for it in items:
        kb.button(text=f"✕ {it['name']}", callback_data=f"rm:{it['id']}")
    if items:
        kb.button(text="✅ Оформить заказ", callback_data="checkout")
        kb.button(text="🗑 Очистить", callback_data="clear_cart")
    kb.button(text="← В меню", callback_data="main")
    kb.adjust(1)
    return kb.as_markup()


def info_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📍 Адреса", callback_data="info:addr")
    kb.button(text="🚚 Доставка", callback_data="info:delivery")
    kb.button(text="💳 Оплата", callback_data="info:pay")
    kb.button(text="🔁 Обмен", callback_data="info:return")
    kb.button(text="📷 Instagram", callback_data="info:inst")
    kb.button(text="← В меню", callback_data="main")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()


def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="← В меню", callback_data="main")
    return kb.as_markup()


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# === АДМИН ===
def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Товары", callback_data="adm:prods")
    kb.button(text="🗂 Категории", callback_data="adm:cats")
    kb.button(text="🛒 Заказы", callback_data="adm:orders")
    kb.button(text="📝 Тексты", callback_data="adm:texts")
    kb.button(text="💳 Реквизиты", callback_data="adm:pay")
    kb.button(text="🔧 Меню", callback_data="adm:menu")
    kb.button(text="👥 Админы", callback_data="adm:admins")
    kb.button(text="📊 Статистика", callback_data="adm:stats")
    kb.button(text="📣 Рассылка", callback_data="adm:broadcast")
    kb.button(text="← Закрыть", callback_data="main")
    kb.adjust(2, 2, 2, 2, 2)
    return kb.as_markup()


TEXT_FIELDS = [
    ("start_text", "✨ Текст /start"),
    ("shop_name", "🏷 Название"),
    ("shop_addresses", "📍 Адреса"),
    ("shop_schedule", "🕐 График"),
    ("delivery_info", "🚚 Доставка"),
    ("payment_info", "💳 Оплата"),
    ("exchange_info", "🔁 Обмен"),
    ("instagram_url", "📷 Instagram"),
    ("operator_username", "💬 Оператор"),
]


def admin_texts_kb():
    kb = InlineKeyboardBuilder()
    for key, label in TEXT_FIELDS:
        kb.button(text=label, callback_data=f"adm:edtxt:{key}")
    kb.button(text="← Назад", callback_data="adm:menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_menu_edit_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="adm:edmenu:catalog")
    kb.button(text="🔍 Подбор", callback_data="adm:edmenu:selector")
    kb.button(text="🛒 Корзина", callback_data="adm:edmenu:cart")
    kb.button(text="💬 Информация", callback_data="adm:edmenu:info")
    kb.button(text="← Назад", callback_data="adm:menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_cats_kb(categories):
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=f"🗑 {c['name']}", callback_data=f"adm:delcat:{c['id']}")
    kb.button(text="➕ Добавить", callback_data="adm:addcat")
    kb.button(text="← Назад", callback_data="adm:menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_pick_cat_kb(categories):
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c["name"], callback_data=f"adm:pickcat:{c['id']}")
    kb.button(text="← Отмена", callback_data="adm:menu")
    kb.adjust(2)
    return kb.as_markup()


def admin_prods_kb(products):
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"🗑 {p['name']}", callback_data=f"adm:delprod:{p['id']}")
    kb.button(text="← Назад", callback_data="adm:prods")
    kb.adjust(1)
    return kb.as_markup()


def admin_orders_kb(orders):
    kb = InlineKeyboardBuilder()
    for o in orders:
        kb.button(text=f"#{o['id']} - {o['name']}", callback_data=f"adm:ord:{o['id']}")
    kb.button(text="← Назад", callback_data="adm:menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_order_kb(order_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"adm:ordok:{order_id}")
    kb.button(text="❌ Отменить", callback_data=f"adm:ordno:{order_id}")
    kb.button(text="← Назад", callback_data="adm:orders")
    kb.adjust(1)
    return kb.as_markup()


def admin_admins_kb(admins):
    kb = InlineKeyboardBuilder()
    for a in admins:
        kb.button(text=f"🗑 {a['username'] or a['user_id']}", callback_data=f"adm:deladm:{a['user_id']}")
    kb.button(text="➕ Добавить", callback_data="adm:addadm")
    kb.button(text="← Назад", callback_data="adm:menu")
    kb.adjust(1)
    return kb.as_markup()
