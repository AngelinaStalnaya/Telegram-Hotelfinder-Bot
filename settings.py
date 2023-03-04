import os

from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr, StrictStr

load_dotenv()  # loads .env with secret sensitive data


class SiteSettings(BaseSettings):  # class for sensitive site data defence
    api_key: SecretStr = os.getenv("SITE_API", None)  # loads secret site_api, None - in order of errors
    host_api: StrictStr = os.getenv("HOST_API", None)  # loads secret host_api


class TGBotSettings(BaseSettings):  # class for sensitive bot data defence
    bot_token: SecretStr = os.getenv('BOT_TOKEN', None)


start_bot = TGBotSettings()
start_site_settings = SiteSettings()
