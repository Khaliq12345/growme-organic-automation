import os
from dotenv import load_dotenv

load_dotenv()

LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "")
ENV = os.getenv("ENV", "dev")
