import aiosqlite

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    product_id TEXT NOT NULL,
    product_title TEXT NOT NULL,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',      -- new / paid / completed
    rating INTEGER,
    comment TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def create_order(user_id, username, product_id, product_title, name, contact, task) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, username, product_id, product_title, name, contact, task) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, product_id, product_title, name, contact, task),
        )
        await db.commit()
        return cur.lastrowid


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return await cur.fetchone()


async def mark_paid(order_id: int) -> bool:
    """Возвращает True, только если заказ был в статусе new (защита от двойного нажатия)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "UPDATE orders SET status = 'paid' WHERE id = ? AND status = 'new'", (order_id,)
        )
        await db.commit()
        return cur.rowcount > 0


async def set_rating(order_id: int, user_id: int, rating: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "UPDATE orders SET rating = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND user_id = ? AND status = 'paid'",
            (rating, order_id, user_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def set_comment(order_id: int, user_id: int, comment: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET comment = ? WHERE id = ? AND user_id = ? AND status = 'completed'",
            (comment, order_id, user_id),
        )
        await db.commit()


async def count_reviews() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
        return (await cur.fetchone())[0]


async def list_reviews(offset: int, limit: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM orders WHERE status = 'completed' "
            "ORDER BY completed_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return await cur.fetchall()


async def average_rating():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT AVG(rating) FROM orders WHERE status = 'completed' AND rating IS NOT NULL"
        )
        return (await cur.fetchone())[0]
