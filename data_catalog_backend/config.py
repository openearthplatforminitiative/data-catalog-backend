from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Get the root directory of the project
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

ENV_PATH = os.path.join(ROOT_DIR, ".env")


print(
    "Loaded .env:",
    os.path.exists(ENV_PATH),
)

load_dotenv(ENV_PATH)


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
    postgres_port: str
    postgres_schema: str

    run_migrations: bool = True
    alembic_directory: str = "../alembic"
    alembic_file: str = "../alembic.ini"

    model_config = SettingsConfigDict(env_file=ENV_PATH)

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
