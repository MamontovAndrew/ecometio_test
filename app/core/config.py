import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "mydb")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "myuser")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    API_V1_STR = "/api/v1"

settings = Settings()
