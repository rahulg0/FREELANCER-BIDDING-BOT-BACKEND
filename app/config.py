from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
    CLIENT_ID: str = os.getenv("CLIENT_ID")
    AUTHORIZATION_BASE_URL: str = os.getenv("AUTHORIZATION_BASE_URL")
    TOKEN_URL: str = os.getenv("TOKEN_URL")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI")
    BASE_URL: str = os.getenv("BASE_URL")
    GEMINI_KEY: str = os.getenv("GEMINI_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
