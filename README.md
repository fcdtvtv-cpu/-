# 🛒 Sales Bot — бот продаж с заявками и отзывами

Telegram-бот для продажи услуг/товаров.

Клиент выбирает услугу → оставляет заявку → продавец получает её в личку → после оплаты просит отзыв → отзывы видят все.

---

## Как работает

1. **Каталог** — клиент выбирает услугу
2. **Заявка** — имя, контакт, описание задачи
3. Бот пишет продавцу в личку + кнопка **«Клиент оплатил товар»**
4. Клиенту: *«Заявка отправлена, ожидайте ответа. Оплата после связи с продавцом»*
5. После оплаты продавец жмёт кнопку → клиенту приходит запрос оценки **0–5** + текст
6. Отзывы сохраняются и показываются в меню **«⭐ Отзывы»**
7. **🔒 Безопасная сделка** — ссылка на профиль Playerok

---

## Структура

```
sales-bot/
├── bot/
│   ├── handlers/
│   │   ├── start.py      # меню, отзывы, безопасная сделка
│   │   └── order.py      # заявка, оплата, оценка
│   ├── keyboards/
│   ├── services/
│   │   ├── products.py   # каталог (заглушки — позже заменим)
│   │   └── storage.py    # заказы и отзывы (JSON)
│   ├── data/             # reviews.json, orders.json
│   ├── config.py
│   ├── states.py
│   └── main.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Установка

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Заполни `.env`:

```env
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
PLAYEROK_URL=https://playerok.com/profile/yunogasaiip/products
SHOP_NAME=Yuno Shop
```

Запуск:

```bash
python -m bot.main
```

---

## Что дальше

Когда скинешь список товаров/услуг — просто обновим `bot/services/products.py`.  
Можно добавить цены, описания, фото и т.д.