from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv("../.env.local")

print("Loaded POSTGRES_USER:", os.getenv("POSTGRES_USER"))
print("Loaded POSTGRES_PASSWORD:", os.getenv("POSTGRES_PASSWORD"))
print("Loaded POSTGRES_DB:", os.getenv("POSTGRES_DB"))


class Settings(BaseSettings):
    version: str = "0.0.1"
    uvicorn_port: int = 8000
    uvicorn_host: str = "0.0.0.0"
    uvicorn_reload: bool = True
    uvicorn_proxy_headers: bool = False
    api_root_path: str = ""
    api_description: str = ""
    api_domain: str = "localhost"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str = "5432"
    postgres_schema: str = "public"

    run_migrations: bool = True
    alembic_directory: str = "./alembic"
    alembic_file: str = "./alembic.ini"

    class Config:
        env_file = "../.env.local"

    @property
    def api_url(self):
        if self.api_domain == "localhost":
            return f"http://{self.api_domain}:{self.uvicorn_port}"
        else:
            return f"https://{self.api_domain}{self.api_root_path}"

    @property
    def database_connection(self):
        return (
            f"postgresql://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}?"
            f"options=-csearch_path={self.postgres_schema}"
        )


settings = Settings()

print(
    "values: ", settings.postgres_user, settings.postgres_password, settings.postgres_db
)
