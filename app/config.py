from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    BASE_URL: str = os.getenv("BASE_URL")
    OPENAI_KEY: str = os.getenv("OPENAI_KEY")
    ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
