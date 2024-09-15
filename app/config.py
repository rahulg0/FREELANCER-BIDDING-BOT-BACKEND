from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    client_id: str = os.getenv("CLIENT_SECRET")
    client_secret: str = os.getenv("CLIENT_ID")
    authorization_base_url: str = os.getenv("AUTHORIZATION_BASE_URL")
    token_url: str = os.getenv("TOKEN_URL")
    redirect_uri: str = os.getenv("REDIRECT_URI")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
