import os
from dotenv import load_dotenv

load_dotenv()


# define config
class Config:
    # app config
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")
    APP_URL = os.getenv("APP_URL")
    CACHE_TYPE = "null"

    # mysql config
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
