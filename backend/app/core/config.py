from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str

    class Config:
        env_file = '.env'

settings = Settings()