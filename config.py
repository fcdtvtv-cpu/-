from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_id: int
    playerok_url: str = "https://playerok.com/profile/yunogasaiip/products"
    shop_name: str = "Yuno Shop"


settings = Settings()