from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional
from pydantic import SecretStr, BaseModel, RedisDsn, model_validator, PostgresDsn, Field
from yaml import load as yaml_load

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import Loader


class BotSettings(BaseModel):
    token: str

class PostgresSettings(BaseModel):
    dsn: PostgresDsn


class Settings(BaseModel):
    bot: BotSettings  # Must be the last one, since it checks for fsm_mode
    postgres: PostgresSettings

def parse_settings(local_file_name: str = ".config.yaml") -> Settings:
    parent_dir = Path(__file__).parent.parent.parent
    settings_file = Path(Path.joinpath(parent_dir, local_file_name))
    if not Path(settings_file).is_file():
        raise ValueError("Path %s is not a file or doesn't exist", settings_file)
    file_path = settings_file.absolute()

    with open(file_path, "rt") as file:
        config_data = yaml_load(file, Loader)
    return Settings.model_validate(config_data)

