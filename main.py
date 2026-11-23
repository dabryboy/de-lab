import psycopg2
import requests
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

URL = "https://mon-amour-pfh9.onrender.com/datalab/"

resp = requests.get(URL, timeout = 20)

load_dotenv()

def get_credentials() -> tuple[str, str]:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        raise ValueError("Please set ADMIN_EMAIL and ADMIN_PASSWORD")

    return email, password

