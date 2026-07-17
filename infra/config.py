from pydantic_settings import BaseSettings

class SystemConfig(BaseSettings):
    lumina_api_key: str = "default_unsafe_key"
    port: int = 8080

    class Config:
        env_file = ".env"
        extra = "ignore"

config = SystemConfig()