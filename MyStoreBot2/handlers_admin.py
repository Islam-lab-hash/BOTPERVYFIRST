"""Админ-хендлеры."""
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
import database as db
import keyboards as kb
from states import AdminAddProduct, AdminEditText
from config import ADMIN_IDS

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return
    await state.clear()
    await message.answer("<b>Админ-панель</b>", reply_markup=kb.admin_menu())


@router.callback_query(F.data == "adm:menu")
async def adm_menu(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await state.clear()
    await call.message.edit_text("<b>Админ-панель</b>", reply_markup=kb.admin_menu())
    await call.answer()


# === ТОВАРЫ ===
@router.callback_query(F.data == "adm:prods")
async def adm_prods(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    cats = await db.list_categories()
    await call.message.edit_text("Выберите категорию:", reply_markup=kb.admin_pick_cat_kb(cats))
    await call.answer()


@router.callback_query(F.data.startswith("adm:pickcat:"))
async def adm_pick_cat(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    cat_id = int(call.data.split(":")[2])
    prods = await db.list_products(cat_id)
    
    if not prods:
        await call.answer("Пусто", show_alert=True)
        return
    
    await call.message.edit_text("Товары:", reply_markup=kb.admin_prods_kb(prods))
    await call.answer()


@router.callback_query(F.data == "adm:add_prod")
async def adm_add_prod(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    cats = await db.list_categories()
    await call.message.edit_text("Куда добавить?", reply_markup=kb.admin_pick_cat_kb(cats))
    await call.answer()


@router.callback_query(F.data.startswith("adm:delprod:"))
async def adm_del_prod(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    prod_id = int(call.data.split(":")[2])
    await db.delete_product(prod_id)
    await call.answer("✅ Удалено")
    await adm_prods(call)


@router.callback_query(F.data.startswith("adm:delcat:"))
async def adm_del_cat(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    cat_id = int(call.data.split(":")[2])
    await db.delete_category(cat_id)
    await call.answer("✅ Удалено")
    await adm_cats(call)


@router.callback_query(F.data.startswith("adm:addcat"))
async def adm_add_cat_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminAddProduct.name)
    await state.update_data(action="addcat")
    await call.message.answer("Введите название категории:")
    await call.answer()


@router.message(AdminAddProduct.name)
async def adm_add_cat_save(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("action") == "addcat":
        await db.add_category(message.text)
        await message.answer("✅ Категория добавлена", reply_markup=kb.admin_menu())
    await state.clear()


# === КАТЕГОРИИ ===
@router.callback_query(F.data == "adm:cats")
async def adm_cats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    cats = await db.list_categories()
    await call.message.edit_text("Категории:", reply_markup=kb.admin_cats_kb(cats))
    await call.answer()


# === ЗАКАЗЫ ===
@router.callback_query(F.data == "adm:orders")
async def adm_orders(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    orders = await db.list_orders()
    await call.message.edit_text("Заказы:", reply_markup=kb.admin_orders_kb(orders))
    await call.answer()


@router.callback_query(F.data.startswith("adm:ord:"))
async def adm_order_detail(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    order_id = int(call.data.split(":")[2])
    order = await db.get_order(order_id)
    
    text = f"<b>Заказ #{order['id']}</b>\n\n"
    text += f"👤 {order['name']}\n📞 {order['phone']}\n💰 {int(order['total'])}₽\n\n{order['items']}"
    if order.get('comment'):
        text += f"\n\n💬 {order['comment']}"
    
    await call.message.edit_text(text, reply_markup=kb.admin_order_kb(order_id))
    await call.answer()


@router.callback_query(F.data.startswith("adm:ordok:"))
async def adm_order_ok(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    order_id = int(call.data.split(":")[2])
    await db.update_order_status(order_id, "done")
    order = await db.get_order(order_id)
    
    try:
        await bot.send_message(order['user_id'], f"✅ Заказ #{order_id} подтверждён!")
    except:
        pass
    
    await call.answer("✅ Подтверждено")
    await adm_orders(call)


@router.callback_query(F.data.startswith("adm:ordno:"))
async def adm_order_no(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    order_id = int(call.data.split(":")[2])
    await db.update_order_status(order_id, "cancelled")
    order = await db.get_order(order_id)
    
    try:
        await bot.send_message(order['user_id'], f"❌ Заказ #{order_id} отменён.")
    except:
        pass
    
    await call.answer("❌ Отменено")
    await adm_orders(call)


# === ТЕКСТЫ ===
@router.callback_query(F.data == "adm:texts")
async def adm_texts(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("📝 <b>Тексты</b>", reply_markup=kb.admin_texts_kb())
    await call.answer()


@router.callback_query(F.data.startswith("adm:edtxt:"))
async def adm_edtxt(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    key = call.data.split(":")[2]
    current = await db.get_text(key)
    
    await state.set_state(AdminEditText.value)
    await state.update_data(key=key)
    
    await call.message.answer(f"Текущее значение:\n<code>{current}</code>\n\nВведите новое:")
    await call.answer()


@router.message(AdminEditText.value)
async def adm_edtxt_save(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("key")
    await db.set_text(key, message.text)
    await message.answer("✅ Сохранено", reply_markup=kb.admin_menu())
    await state.clear()


# === МЕНЮ ===
@router.callback_query(F.data == "adm:menu")
async def adm_menu_edit(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("🔧 <b>Редактирование меню</b>", reply_markup=kb.admin_menu_edit_kb())
    await call.answer()


@router.callback_query(F.data.startswith("adm:edmenu:"))
async def adm_edmenu(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    key = call.data.split(":")[2]
    current = await db.get_text(f"menu_{key}")
    
    await state.set_state(AdminEditText.value)
    await state.update_data(key=f"menu_{key}")
    
    await call.message.answer(f"Текущее: <b>{current}</b>\n\nВведите новое название:")
    await call.answer()


# === РЕКВИЗИТЫ ===
@router.callback_query(F.data == "adm:pay")
async def adm_pay(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    pay = await db.get_payment_info()
    text = f"💳 <b>Реквизиты</b>\n\nКарта: {pay['card']}\nПолучатель: {pay['holder']}\nБанк: {pay['bank']}"
    await call.message.answer(text)
    await call.answer()


# === АДМИНЫ ===
@router.callback_query(F.data == "adm:admins")
async def adm_admins(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    admins = await db.list_admins()
    await call.message.edit_text("👥 <b>Админы</b>", reply_markup=kb.admin_admins_kb(admins))
    await call.answer()


@router.callback_query(F.data.startswith("adm:deladm:"))
async def adm_del_adm(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    user_id = int(call.data.split(":")[2])
    await db.remove_admin(user_id)
    await call.answer("✅ Удалён")
    await adm_admins(call)


@router.callback_query(F.data == "adm:addadm")
async def adm_add_adm_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminEditText.value)
    await state.update_data(action="addadm")
    await call.message.answer("Введите Telegram ID нового админа:")
    await call.answer()


# === СТАТИСТИКА ===
@router.callback_query(F.data == "adm:stats")
async def adm_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    stats = await db.get_stats()
    text = f"📊 <b>Статистика</b>\n\n👥 Пользователей: {stats['users']}\n🛒 Заказов: {stats['orders']}\n📦 Товаров: {stats['products']}"
    await call.message.answer(text)
    await call.answer()


# === РАССЫЛКА ===
@router.callback_query(F.data == "adm:broadcast")
async def adm_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminEditText.value)
    await state.update_data(action="broadcast")
    await call.message.answer("Введите текст рассылки:")
    await call.answer()
