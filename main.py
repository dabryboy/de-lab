import psycopg2
import requests
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
from typing import Any

DATALAB_URL = "https://mon-amour-pfh9.onrender.com/datalab/"
LOGIN_URL = "https://mon-amour-pfh9.onrender.com/login/?next=/datalab/"
JSON_DATALAB_URL = "https://mon-amour-pfh9.onrender.com/datalab/export/json/"

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
    if "/login" in resp.url:
        raise RuntimeError("Не удалось войти: сервер вернул страницу логина (проверь логин/пароль)")

    return session


def fetch_datalab_page(session: requests.Session) -> requests.Response:
    response = session.get(DATALAB_URL, timeout=20)
    response.raise_for_status()
    return response


def fetch_datalab_json(session: requests.Session) -> Any:
    response = session.get(JSON_DATALAB_URL, timeout=20)
    response.raise_for_status()
    return response.json()


def extract_transactions(payload: dict) -> list[dict]:
  if not isinstance(payload, dict):
    raise ValueError("Expected payload to be a dict")

  transactions = payload.get("fact_kiss_transactions")
  if not isinstance(transactions, list):
    raise ValueError("Expected 'fact_kiss_transactions' to be a list")

  return transactions


def flatten_transaction(tx: dict) -> dict:
    sender = tx.get("sender") or {}
    receiver = tx.get("receiver") or {}
    service = tx.get("service") or {}

    return {
        "transaction_id": tx.get("transaction_id"),
        "sender_love_code": sender.get("love_code"),
        "sender_name": sender.get("name"),
        "receiver_love_code": receiver.get("love_code"),
        "receiver_name": receiver.get("name"),
        "service_id": service.get("id"),
        "service_title": service.get("title"),
        "service_category": service.get("category"),
        "is_free_reward": tx.get("is_free_reward"),
        "scheduled_date": tx.get("scheduled_date"),
        "kisses_amount": tx.get("kisses_amount"),
        "status": tx.get("status"),
        "love_note": tx.get("love_note"),
        "created_at": tx.get("created_at"),
        "completed_at": tx.get("completed_at"),
    }


def flatten_transactions(transactions: list[dict]) -> list[dict]:
    flat_transactions = []
    for i in transactions:
        flat_transactions.append(flatten_transaction(i))
    return flat_transactions


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


if __name__ == "__main__":
    email, password = get_credentials()
    session = create_logged_in_session(email, password)
    page_resp = fetch_datalab_page(session)

    data_json = fetch_datalab_json(session)
    extract_data_json = extract_transactions(data_json)


    # print("Итоговый URL:", page_resp.url)
    # print("Статус код:", page_resp.status_code)
    # print("Content-Type:", page_resp.headers.get("Content-Type"))
    # print("Фрагмент ответа:", page_resp.text[1500:3000])
    conn = get_db_connection()
    print("DB OK:", conn)
    conn.close()
    # print("json:\n", extract_data_json)
    # print(flatten_transactions(extract_data_json))