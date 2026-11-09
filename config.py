import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PLAYEROK_URL = os.getenv(
    "PLAYEROK_URL", "https://playerok.com/profile/yunogasaiip/products"
)
DB_PATH = os.getenv("DB_PATH", "shop.db")
REVIEWS_PER_PAGE = 5
