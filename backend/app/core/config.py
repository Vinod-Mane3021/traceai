from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"

    GITHUB_WEBHOOK_SECRET: str
    GITHUB_APP_ID: str
    GITHUB_CLIENT_ID: str
    GITHUB_APP_PRIVATE_KEY_PATH: str
    GITHUB_PUBLIC_LINK: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
