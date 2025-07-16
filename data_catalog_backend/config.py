from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    version: str = "0.0.1"
    uvicorn_port: int = 8000
    uvicorn_host: str = "0.0.0.0"
    uvicorn_reload: bool = True
    uvicorn_proxy_headers: bool = False
    api_root_path: str = ""
    api_description: str = ""
    api_domain: str = "localhost"

    log_level: str = "INFO"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_schema: str = "public"

    run_migrations: bool = False
    alembic_directory: str = "./alembic"
    alembic_file: str = "./alembic.ini"

    include_admin_api: bool = False
    include_public_api: bool = False

    auth_url: str = ""
    token_url: str = ""

    auth_client_id: str = ""
    auth_jwks_url: str = ""

    auth_required_role: str = ""

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

    @property
    def logging_config(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "detailed",
                },
            },
            "loggers": {
                "data_catalog_backend": {
                    "level": self.log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }


settings = Settings()
