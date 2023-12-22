from dataclasses import dataclass
from environs import Env


env = Env()
env.read_env()


@dataclass
class BotSettings:
    token: str
    admin_id: int


@dataclass
class DBSettings:
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    

def load_db_config():
    return DBSettings(
        DB_HOST=env.str('DB_HOST'),
        DB_PORT=env.str('DB_PORT'),
        DB_USER=env.str('DB_USER'),
        DB_PASS=env.str('DB_PASS'),
        DB_NAME=env.str('DB_NAME'),
    )


def load_bot_config():
    return BotSettings(
        token=env.str('TOKEN'),
        admin_id=env.int('STAFF_ID')
    )


settings_db = load_db_config()
settings_bot = load_bot_config()