from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    version: str = "0.0.1"
    uvicorn_port: int = 8080
    uvicorn_host: str = "0.0.0.0"
    uvicorn_reload: bool = True
    uvicorn_proxy_headers: bool = False
    api_root_path: str = ""
    api_description: str = ""
    api_domain: str = "localhost"

    postgres_user: str = "dc_user"
    postgres_password: str = "dc_password"
    postgres_db: str = "datacatalog_db"
    postgres_host: str = "localhost"
    postgres_port: str = "5434"
    postgres_schema: str = "public"

    run_migrations: bool = True
    alembic_directory: str = "./alembic"
    alembic_file: str = "./alembic.ini"

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
