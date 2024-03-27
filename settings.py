from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import SecretStr
import os

load_dotenv()


class SiteSettings(BaseSettings):
    TOKEN: SecretStr = os.getenv("TOKEN", None)
    local_path: SecretStr = os.getenv("LOCAL_PATH", None)
    virtual_path: SecretStr = os.getenv("VIRTUAL_PATH", None)
    period: SecretStr = os.getenv("SINCHRONIZATION_PERIOD", None)
    log_path: SecretStr = os.getenv("LOG_PATH", None)
