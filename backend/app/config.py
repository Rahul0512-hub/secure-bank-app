import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    MONGODB_AUDIT_URI: str = os.getenv("MONGODB_AUDIT_URI", "")


settings = Settings()
