"""База данных SQLite."""
import aiosqlite
from typing import Optional
from config import DB_PATH

DEFAULT_CATEGORIES = [
    "Халаты",
    "Пеньюары",
    "Сорочки",
    "Комплекты",
    "Наборы трусиков",
    "Свадебное белье",
    "Корсетные изделия",
    "Чулки и колготки",
    "Купальники",
    "Аксессуары",
    "Акции",
]

DEFAULT_SETTINGS = {
    "pay_card": "0000 0000 0000 0000",
    "pay_holder": "ИВАНОВА А. А.",
    "pay_bank": "Сбербанк",
    "start_text": "Натуральный шёлк Premium Turkey",
    "shop_name": "LINGERIE BOUTIQUE",
    "shop_addresses": "📍 Grozny Mall, г. Грозный",
    "shop_schedule": "Ежедневно 10:00-22:00",
    "delivery_info": "🚚 Доставка по всей России",
    "payment_info": "💳 Оплата при получении",
    "exchange_info": "🔁 Обмен в течение 14 дней",
    "instagram_url": "https://instagram.com/",
    "operator_username": "@manager",
    "menu_catalog": "Каталог",
    "menu_selector": "Подбор",
    "menu_cart": "Корзина",
    "menu_info": "Информация",
}


async def init_db():
    """Создаёт таблицы."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                sizes TEXT DEFAULT '',
                colors TEXT DEFAULT '',
                material TEXT DEFAULT '',
                country TEXT DEFAULT '',
                description TEXT DEFAULT '',
                photo_file_id TEXT DEFAULT '',
                in_stock INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, product_id)
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                phone TEXT,
                city TEXT,
                delivery TEXT,
                comment TEXT,
                items TEXT,
                total REAL,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Сидим категории
        cur = await db.execute("SELECT COUNT(*) FROM categories")
        if (await cur.fetchone())[0] == 0:
            for i, name in enumerate(DEFAULT_CATEGORIES):
                await db.execute("INSERT INTO categories (name, position) VALUES (?, ?)", (name, i))
        
        # Сидим настройки
        for k, v in DEFAULT_SETTINGS.items():
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
        await db.commit()


# === ПОЛЬЗОВАТЕЛИ ===
async def upsert_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=?, first_name=?
        """, (user_id, username, first_name, username, first_name))
        await db.commit()


# === КАТЕГОРИИ ===
async def list_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT id, name, position FROM categories ORDER BY position")
        return await cur.fetchall()


async def get_category(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT id, name FROM categories WHERE id=?", (cat_id,))
        return await cur.fetchone()


async def add_category(name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT MAX(position) FROM categories")
        pos = (await cur.fetchone())[0] or 0
        await db.execute("INSERT INTO categories (name, position) VALUES (?, ?)", (name, pos + 1))
        await db.commit()


async def update_category(cat_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET name=? WHERE id=?", (name, cat_id))
        await db.commit()


async def delete_category(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await db.commit()


# === ТОВАРЫ ===
async def list_products(cat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT id, category_id, name, price, sizes, colors, material, country, description, photo_file_id, in_stock
            FROM products WHERE category_id=? ORDER BY id DESC
        """, (cat_id,))
        return await cur.fetchall()


async def get_product(prod_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT id, category_id, name, price, sizes, colors, material, country, description, photo_file_id, in_stock
            FROM products WHERE id=?
        """, (prod_id,))
        return await cur.fetchone()


async def add_product(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO products (category_id, name, price, sizes, colors, material, country, description, photo_file_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["category_id"], data["name"], data["price"], data.get("sizes", ""),
            data.get("colors", ""), data.get("material", ""), data.get("country", ""),
            data.get("description", ""), data.get("photo_file_id", "")
        ))
        await db.commit()
        return cur.lastrowid


async def update_product(prod_id: int, **fields):
    async with aiosqlite.connect(DB_PATH) as db:
        sets = []
        vals = []
        for k, v in fields.items():
            sets.append(f"{k}=?")
            vals.append(v)
        vals.append(prod_id)
        await db.execute(f"UPDATE products SET {','.join(sets)} WHERE id=?", vals)
        await db.commit()


async def delete_product(prod_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id=?", (prod_id,))
        await db.commit()


# === КОРЗИНА ===
async def get_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT p.id, p.name, p.price, p.photo_file_id, c.qty
            FROM carts c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id=?
        """, (user_id,))
        return await cur.fetchall()


async def add_to_cart(user_id: int, prod_id: int, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO carts (user_id, product_id, qty) VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET qty=qty+?
        """, (user_id, prod_id, qty, qty))
        await db.commit()


async def remove_from_cart(user_id: int, prod_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM carts WHERE user_id=? AND product_id=?", (user_id, prod_id))
        await db.commit()


async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM carts WHERE user_id=?", (user_id,))
        await db.commit()


# === ЗАКАЗЫ ===
async def create_order(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO orders (user_id, name, phone, city, delivery, comment, items, total, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new')
        """, (
            data["user_id"], data.get("name"), data.get("phone"), data.get("city"),
            data.get("delivery"), data.get("comment", ""), data["items"], data["total"]
        ))
        await db.commit()
        return cur.lastrowid


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        return await cur.fetchone()


async def list_orders(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cur = await db.execute("SELECT * FROM orders WHERE status=? ORDER BY id DESC", (status,))
        else:
            cur = await db.execute("SELECT * FROM orders ORDER BY id DESC")
        return await cur.fetchall()


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()


# === НАСТРОЙКИ ===
async def get_text(key: str, default: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default


async def set_text(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()


get_setting = get_text
set_setting = set_text


# === АДМИНЫ ===
async def is_db_admin(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,))
        return await cur.fetchone() is not None


async def add_admin(user_id: int, username: str = None, added_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO admins (user_id, username, added_by) VALUES (?, ?, ?)
        """, (user_id, username, added_by))
        await db.commit()


async def remove_admin(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
        await db.commit()


async def list_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT user_id, username FROM admins")
        return await cur.fetchall()


# === СТАТИСТИКА ===
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        for table in ["users", "products", "categories", "orders"]:
            cur = await db.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = (await cur.fetchone())[0]
        return stats
