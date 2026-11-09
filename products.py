# Список товаров/услуг. Позже сюда добавим реальные позиции.
# id — уникальный короткий ключ (латиница/цифры), он уходит в callback_data.

PRODUCTS = [
    {"id": "demo1", "title": "Товар 1 (пример)", "price": "000 ₽", "description": "Описание будет позже."},
    {"id": "demo2", "title": "Товар 2 (пример)", "price": "000 ₽", "description": "Описание будет позже."},
]


def get_product(product_id: str):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)
