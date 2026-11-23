import psycopg2
import requests
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

DATALAB_URL = "https://mon-amour-pfh9.onrender.com/datalab/"
LOGIN_URL = "https://mon-amour-pfh9.onrender.com/login/?next=/datalab/"


load_dotenv()

def get_credentials() -> tuple[str, str]:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        raise ValueError("Please set ADMIN_EMAIL and ADMIN_PASSWORD")

    return email, password


def fetch_csrf_token(session: requests.Session, login_url: str) -> str:
    resp = session.get(login_url, timeout=20)
    resp.raise_for_status()
    token = session.cookies.get("csrftoken")

    if not token:
        raise RuntimeError(
            "Не удалось найти csrftoken в cookies после GET-запроса на логин."
        )

    return token

def create_logged_in_session(email: str, password: str) -> requests.Session:
    session = requests.Session()
    csrf_token = fetch_csrf_token(session, LOGIN_URL)

    payload = {
        "email": email,
        "password": password,
        "csrfmiddlewaretoken": csrf_token,
    }

    resp = session.post(
        LOGIN_URL,
        data=payload,
        headers={"Referer": LOGIN_URL},
        timeout=20,
    )
    resp.raise_for_status()

    return session


def fetch_datalab_page(session: requests.Session) -> requests.Response:
    response = session.get(DATALAB_URL, timeout=20)
    response.raise_for_status()
    return response


if __name__ == "__main__":
    email, password = get_credentials()
    session = create_logged_in_session(email, password)
    page_resp = fetch_datalab_page(session)

    print("Итоговый URL:", page_resp.url)
    print("Статус код:", page_resp.status_code)
    print("Content-Type:", page_resp.headers.get("Content-Type"))
    print("Фрагмент ответа:", page_resp.text[:500])