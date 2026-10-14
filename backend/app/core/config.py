from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "predicare"
    POSTGRES_PASSWORD: str = "predicare123"
    POSTGRES_DB: str = "predicare_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str = "change-me-in-production-very-secret-key-123456"
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()