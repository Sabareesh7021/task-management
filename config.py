import os
from dotenv import load_dotenv

load_dotenv()

TIMEZONE: str    = os.getenv('TIMEZONE')
DB_PASS : str    = os.getenv('DB_PASS')
DB_NAME : str    = os.getenv('DB_NAME')
DB_USER : str    = os.getenv('DB_USER')
DB_HOST : str    = os.getenv('DB_HOST')
DB_PORT : str    = os.getenv('DB_PORT')
SECRET_KEY : str     = os.getenv('SECRET_KEY')
ALLOWED_HOSTS: list  = [host.strip() for host in os.getenv('APP_URL', 'localhost').split(',')]
FRONTEND_URLS: list = os.getenv('FRONTEND_URLS', '').split(',')
DEBUG : bool         = os.getenv('DEBUG')
