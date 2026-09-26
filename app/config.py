import os

class Settings:
    APP_NAME: str = "Vera Message Engine"
    PORT: int = int(os.getenv("PORT", 8080))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

settings = Settings()
