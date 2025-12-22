from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # API
    api_version: str = "v1"

    # Auth
    clerk_secret_key: str

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str

    # Email
    resend_api_key: str = ""

    # Business
    protocol_fee_percent: float = 7.0

    # Frontend
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Compute CORS origins once at initialization
        self.cors_origins = list(set([
            "http://localhost:3000",
            "http://localhost:3001",
            "https://proof-of-consideration.vercel.app",
            "https://disclosed.vercel.app",
            self.frontend_url
        ]))
        print(f"CORS Origins initialized: {self.cors_origins}")


@lru_cache()
def get_settings():
    return Settings()
