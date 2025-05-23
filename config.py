import os
from dotenv import load_dotenv

load_dotenv()

TIMEZONE: str    = os.getenv('TIMEZONE')

SECRET_KEY : str     = os.getenv('SECRET_KEY')
ALLOWED_HOSTS: list  = [host.strip() for host in os.getenv('APP_URL', 'localhost').split(',')]
DEBUG : bool         = os.getenv('DEBUG')
