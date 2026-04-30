from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):

    #POSTGRES
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_ECHO: bool = False
    POSTGRES_CONNECT: str


    #JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_SECRET: str
    JWT_ALGORITHM: str


    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_CONNECT}/{self.POSTGRES_DB}"
        )
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
