"""Пользовательские хендлеры."""
import os
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, ReplyKeyboardRemove

import database as db
import keyboards as kb
from states import OrderForm, AdminEditText
from config import ADMIN_IDS

router = Router()
ASSETS = os.path.join(os.path.dirname(__file__), "assets")


# === /START ===
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    # Фото
    photo_path = os.path.join(ASSETS, "start.png")
    text = await db.get_text("start_text", "Натуральный шёлк Premium Turkey")
    
    if os.path.exists(photo_path):
        await message.answer_photo(photo=FSInputFile(photo_path), caption=f"<b>{text}</b>", reply_markup=await kb.main_menu())
    else:
        await message.answer(f"<b>{text}</b>", reply_markup=await kb.main_menu())


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 Ваш ID: <code>{message.from_user.id}</code>")


@router.callback_query(F.data == "main")
async def to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    text = await db.get_text("start_text", "Натуральный шёлк Premium Turkey")
    photo_path = os.path.join(ASSETS, "start.png")
    
    try:
        if os.path.exists(photo_path) and call.message.photo:
            await call.message.edit_caption(caption=f"<b>{text}</b>", reply_markup=await kb.main_menu())
        else:
            await call.message.edit_text(f"<b>{text}</b>", reply_markup=await kb.main_menu())
    except:
        if os.path.exists(photo_path):
            await call.message.answer_photo(photo=FSInputFile(photo_path), caption=f"<b>{text}</b>", reply_markup=await kb.main_menu())
        else:
            await call.message.answer(f"<b>{text}</b>", reply_markup=await kb.main_menu())
    await call.answer()


# === КАТАЛОГ ===
@router.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    cats = await db.list_categories()
    if not cats:
        await call.answer("Каталог пуст", show_alert=True)
        return
    
    photo_path = os.path.join(ASSETS, "catalog.png")
    text = "📋 <b>Каталог</b>\nВыберите категорию:"
    
    try:
        if os.path.exists(photo_path) and call.message.photo:
            await call.message.edit_caption(caption=text, reply_markup=kb.categories_kb(cats))
        else:
            await call.message.edit_text(text, reply_markup=kb.categories_kb(cats))
    except:
        if os.path.exists(photo_path):
            await call.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb.categories_kb(cats))
        else:
            await call.message.answer(text, reply_markup=kb.categories_kb(cats))
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category(call: CallbackQuery):
    cat_id = int(call.data.split(":")[1])
    prods = await db.list_products(cat_id)
    cat = await db.get_category(cat_id)
    
    if not prods:
        await call.answer("Пусто", show_alert=True)
        return
    
    text = f"<b>{cat['name']}</b>\nВыберите товар:"
    await call.message.edit_text(text, reply_markup=kb.products_kb(prods, cat_id))
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery, bot: Bot):
    prod_id = int(call.data.split(":")[1])
    p = await db.get_product(prod_id)
    if not p:
        await call.answer("Не найдено", show_alert=True)
        return
    
    text = f"<b>{p['name']}</b>\n💰 {int(p['price'])}₽"
    if p['sizes']:
        text += f"\n📏 {p['sizes']}"
    if p['colors']:
        text += f"\n🎨 {p['colors']}"
    
    try:
        await call.message.delete()
    except:
        pass
    
    if p['photo_file_id']:
        await bot.send_photo(call.from_user.id, photo=p['photo_file_id'], caption=text, reply_markup=kb.product_kb(p['id'], p['category_id']))
    else:
        await bot.send_message(call.from_user.id, text, reply_markup=kb.product_kb(p['id'], p['category_id']))
    await call.answer()


# === КОРЗИНА ===
@router.callback_query(F.data.startswith("add:"))
async def add_cart(call: CallbackQuery):
    prod_id = int(call.data.split(":")[1])
    await db.add_to_cart(call.from_user.id, prod_id)
    await call.answer("✅ Добавлено в корзину", show_alert=True)


@router.callback_query(F.data.startswith("rm:"))
async def rm_cart(call: CallbackQuery):
    prod_id = int(call.data.split(":")[1])
    await db.remove_from_cart(call.from_user.id, prod_id)
    await show_cart(call)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery):
    await db.clear_cart(call.from_user.id)
    await show_cart(call)


@router.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    items = await db.get_cart(call.from_user.id)
    
    photo_path = os.path.join(ASSETS, "cart.png")
    
    if not items:
        text = "🛒 <b>Корзина пуста</b>"
    else:
        total = sum(it['price'] * it['qty'] for it in items)
        lines = ["🛒 <b>Ваша корзина</b>\n"]
        for it in items:
            lines.append(f"• {it['name']} x{it['qty']} = {int(it['price']*it['qty'])}₽")
        lines.append(f"\n<b>Итого: {int(total)}₽</b>")
        text = "\n".join(lines)
    
    try:
        if os.path.exists(photo_path) and call.message.photo:
            await call.message.edit_caption(caption=text, reply_markup=kb.cart_kb(items))
        else:
            await call.message.edit_text(text, reply_markup=kb.cart_kb(items))
    except:
        if os.path.exists(photo_path):
            await call.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb.cart_kb(items))
        else:
            await call.message.answer(text, reply_markup=kb.cart_kb(items))
    await call.answer()


# === ОФОРМЛЕНИЕ ===
@router.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery, state: FSMContext):
    items = await db.get_cart(call.from_user.id)
    if not items:
        await call.answer("Корзина пуста", show_alert=True)
        return
    
    await state.set_state(OrderForm.name)
    await call.message.answer("Введите ваше <b>имя</b>:")
    await call.answer()


@router.message(OrderForm.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.phone)
    await message.answer("Введите <b>телефон</b>:", reply_markup=kb.phone_kb())


@router.message(OrderForm.phone)
async def order_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.comment)
    await message.answer("Комментарий к заказу (или /skip):", reply_markup=ReplyKeyboardRemove())


@router.message(OrderForm.comment, Command("skip"))
async def order_skip(message: Message, state: FSMContext):
    await state.update_data(comment="")
    await order_finish(message, state)


@router.message(OrderForm.comment)
async def order_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await order_finish(message, state)


async def order_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    items = await db.get_cart(message.from_user.id)
    total = sum(it['price'] * it['qty'] for it in items)
    items_text = "; ".join(f"{it['name']} x{it['qty']}" for it in items)
    
    order_id = await db.create_order({
        "user_id": message.from_user.id,
        "name": data.get("name"),
        "phone": data.get("phone"),
        "items": items_text,
        "total": total,
        "comment": data.get("comment", "")
    })
    
    await db.clear_cart(message.from_user.id)
    await state.clear()
    
    # Уведомление админам
    from bot import bot
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"🆕 <b>Заказ #{order_id}</b>\n👤 {data.get('name')}\n📞 {data.get('phone')}\n💰 {int(total)}₽\n\n{items_text}")
        except:
            pass
    
    await message.answer(f"✅ <b>Заказ #{order_id} создан!</b>\nОжидайте подтверждения.", reply_markup=kb.back_kb())


# === ИНФО ===
@router.callback_query(F.data == "info")
async def show_info(call: CallbackQuery):
    photo_path = os.path.join(ASSETS, "info.png")
    text = "ℹ️ <b>Информация</b>"
    
    try:
        if os.path.exists(photo_path) and call.message.photo:
            await call.message.edit_caption(caption=text, reply_markup=kb.info_kb())
        else:
            await call.message.edit_text(text, reply_markup=kb.info_kb())
    except:
        if os.path.exists(photo_path):
            await call.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb.info_kb())
        else:
            await call.message.answer(text, reply_markup=kb.info_kb())
    await call.answer()


@router.callback_query(F.data.startswith("info:"))
async def info_page(call: CallbackQuery):
    key = call.data.split(":")[1]
    
    texts = {
        "addr": ("shop_addresses", "📍 Адреса"),
        "delivery": ("delivery_info", "🚚 Доставка"),
        "pay": ("payment_info", "💳 Оплата"),
        "return": ("exchange_info", "🔁 Обмен"),
        "inst": ("instagram_url", "📷 Instagram"),
    }
    
    if key in texts:
        db_key, label = texts[key]
        val = await db.get_text(db_key)
        text = f"<b>{label}</b>\n\n{val}"
    else:
        text = "Раздел не найден"
    
    await call.message.edit_text(text, reply_markup=kb.back_kb())
    await call.answer()


# === ПОДБОР ===
@router.callback_query(F.data == "selector")
async def show_selector(call: CallbackQuery):
    photo_path = os.path.join(ASSETS, "selector.png")
    text = "🔍 <b>Подбор товара</b>\nДля подбора напишите оператору."
    
    try:
        if os.path.exists(photo_path) and call.message.photo:
            await call.message.edit_caption(caption=text, reply_markup=kb.back_kb())
        else:
            await call.message.edit_text(text, reply_markup=kb.back_kb())
    except:
        if os.path.exists(photo_path):
            await call.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb.back_kb())
        else:
            await call.message.answer(text, reply_markup=kb.back_kb())
    await call.answer()
