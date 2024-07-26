import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    log_level: str
    db_name: str

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        numeric_level = getattr(logging, self.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")
        logging.basicConfig(level=numeric_level)


def get_settings() -> Settings:
    return Settings()
