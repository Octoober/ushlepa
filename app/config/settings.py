from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_token: str
    channel_name: str
    admin_ids: str
    database_url: str
    bot_name: str | None = None
    queue_interval_minutes: int = 30
    persistence_path: str = "data/user_data.pkl"

    @property
    def admin_ids_list(self) -> list[int]:
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


settings = Settings()
