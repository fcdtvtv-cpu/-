"""
Каталог услуг / товаров.
Пока заглушки — позже заменим на реальные товары.
"""

from typing import TypedDict


class Product(TypedDict):
    id: str
    title: str
    description: str
    price: str


# Временные заглушки. Когда скинешь товары — просто обновим этот список.
PRODUCTS: list[Product] = [
    {
        "id": "service_1",
        "title": "Услуга #1",
        "description": "Описание услуги появится позже",
        "price": "—",
    },
    {
        "id": "service_2",
        "title": "Услуга #2",
        "description": "Описание услуги появится позже",
        "price": "—",
    },
    {
        "id": "service_3",
        "title": "Услуга #3",
        "description": "Описание услуги появится позже",
        "price": "—",
    },
]


def get_all_products() -> list[Product]:
    return PRODUCTS


def get_product(product_id: str) -> Product | None:
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None