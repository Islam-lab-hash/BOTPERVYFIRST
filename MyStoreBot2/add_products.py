"""Добавление товаров из папок в БД."""
import asyncio
import os
import database as db

async def main():
    await db.init_db()
    
    # Добавляем недостающие категории
    new_cats = ["Пижамы", "Бюстгальтеры"]
    for cat_name in new_cats:
        try:
            await db.add_category(cat_name)
            print(f"✅ Добавлена категория: {cat_name}")
        except Exception as e:
            print(f"⚠️ Категория {cat_name} уже существует")
    
    # Получаем все категории
    cats = await db.list_categories()
    cat_map = {c['name']: c['id'] for c in cats}
    
    # Товары для добавления
    products_dir = "assets/products"
    
    # Халаты
    halat_dir = os.path.join(products_dir, "Халат")
    if os.path.exists(halat_dir):
        halat_photos = [f for f in os.listdir(halat_dir) if f.endswith(('.jpg', '.png'))]
        for i, photo in enumerate(halat_photos[:6], 1):
            photo_path = os.path.join(halat_dir, photo)
            product_name = f"Шёлковый халат #{i}"
            await db.add_product({
                "category_id": cat_map["Халаты"],
                "name": product_name,
                "price": 4500 + i * 500,
                "sizes": "S,M,L,XL",
                "colors": "белый,чёрный,граит",
                "material": "Натуральный шёлк 100%",
                "country": "Турция",
                "description": "Элегантный шёлковый халат с кружевной отделкой.",
                "photo_file_id": photo_path
            })
            print(f"✅ Добавлен: {product_name}")
    
    # Пижамы
    pijama_dir = os.path.join(products_dir, "Пижама")
    if os.path.exists(pijama_dir):
        pijama_photos = [f for f in os.listdir(pijama_dir) if f.endswith(('.jpg', '.png'))]
        for i, photo in enumerate(pijama_photos[:6], 1):
            photo_path = os.path.join(pijama_dir, photo)
            product_name = f"Шёлковая пижама #{i}"
            await db.add_product({
                "category_id": cat_map.get("Пижамы", 3),  # Если нет категории Пижамы, используем Сорочки
                "name": product_name,
                "price": 3900 + i * 400,  # 3900-6300 ₽
                "sizes": "S,M,L,XL",
                "colors": "красный,синий,чёрный,белый",
                "material": "Натуральный шёлк 100%",
                "country": "Турция",
                "description": "Уютная шёлковая пижама. Мягкая, дышащая, идеальна для сна.",
                "photo_file_id": photo_path
            })
            print(f"✅ Добавлен: {product_name}")
    
    # Комплекты
    komplekt_dir = os.path.join(products_dir, "Комплекты")
    if os.path.exists(komplekt_dir):
        komplekt_photos = [f for f in os.listdir(komplekt_dir) if f.endswith(('.jpg', '.png'))]
        for i, photo in enumerate(komplekt_photos[:3], 1):
            photo_path = os.path.join(komplekt_dir, photo)
            product_name = f"Комплект белья #{i}"
            await db.add_product({
                "category_id": cat_map["Комплекты"],
                "name": product_name,
                "price": 3200 + i * 300,  # 3200-4100 ₽
                "sizes": "S,M,L,XL",
                "colors": "чёрный,синий,бордовый",
                "material": "Кружево, шёлк",
                "country": "Турция",
                "description": "Элегантный комплект: бюстгальтер + трусики. Идеальная посадка.",
                "photo_file_id": photo_path
            })
            print(f"✅ Добавлен: {product_name}")
    
    # Бюсты
    bust_dir = os.path.join(products_dir, "Бюсты")
    if os.path.exists(bust_dir):
        bust_photos = [f for f in os.listdir(bust_dir) if f.endswith(('.jpg', '.png'))]
        for i, photo in enumerate(bust_photos[:6], 1):
            photo_path = os.path.join(bust_dir, photo)
            product_name = f"Бюстгальтер #{i}"
            await db.add_product({
                "category_id": cat_map.get("Бюстгальтеры", 7),  # Если нет, используем Корсетные изделия
                "name": product_name,
                "price": 2500 + i * 200,  # 2500-3700 ₽
                "sizes": "75B,75C,80B,80C,85B",
                "colors": "чёрный,белый,бежевый",
                "material": "Кружево, микрофибра",
                "country": "Турция",
                "description": "Красивый бюстгальтер с кружевом. Удобная посадка, отличная поддержка.",
                "photo_file_id": photo_path
            })
            print(f"✅ Добавлен: {product_name}")
    
    # Пеньюары
    penuar_dir = os.path.join(products_dir, "Пеньюар")
    if os.path.exists(penuar_dir):
        penuar_photos = [f for f in os.listdir(penuar_dir) if f.endswith(('.jpg', '.png'))]
        for i, photo in enumerate(penuar_photos[:1], 1):
            photo_path = os.path.join(penuar_dir, photo)
            product_name = f"Пеньюар #{i}"
            await db.add_product({
                "category_id": cat_map["Пеньюары"],
                "name": product_name,
                "price": 5500,  # 5500 ₽
                "sizes": "S,M,L",
                "colors": "чёрный,белый",
                "material": "Атлас, кружево",
                "country": "Турция",
                "description": "Романтичный пеньюар с кружевной отделкой. Идеален для особых случаев.",
                "photo_file_id": photo_path
            })
            print(f"✅ Добавлен: {product_name}")
    
    print("\n✅ Все товары добавлены!")

if __name__ == "__main__":
    asyncio.run(main())
