from pydantic_settings import BaseSettings
from pydantic import computed_field
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

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        """Compute CORS origins from frontend_url and hardcoded values"""
        origins = list(set([
            "http://localhost:3000",
            "http://localhost:3001",
            "https://proof-of-consideration.vercel.app",
            "https://disclosed.vercel.app",
            self.frontend_url
        ]))
        print(f"CORS Origins: {origins}")
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
