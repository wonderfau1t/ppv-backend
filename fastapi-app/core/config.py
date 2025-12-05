from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class JWTConfig(BaseModel):
    secret: str
    algorithm: str
    ttl_minutes: int 

class HTTPServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str

    echo: bool
    echo_pool: bool

    def __str__(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )
    httpserver_config: HTTPServerConfig = HTTPServerConfig()
    api_prefix: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    jwt: JWTConfig


settings = Settings()  # type: ignore
