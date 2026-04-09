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

    OPENAI_API_KEY: str
    LITELLM_MODEL: str

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: str | None = None
    POSTGRES_DB: str | None = None

    DATABASE_URL_OVERRIDE: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
