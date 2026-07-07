import os
import pyodbc
from contextlib import contextmanager
from datetime import datetime

_CONN_STR = os.getenv("AZURE_SQL_CONNECTION_STRING")


@contextmanager
def _get_conn():
    conn = pyodbc.connect(_CONN_STR)
    try:
        yield conn
    finally:
        conn.close()


# --- Users ---

def get_user(user_id: str) -> dict | None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, email, created_at, tier, stripe_id FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        return _row_to_user(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, email, created_at, tier, stripe_id FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        return _row_to_user(row) if row else None


def get_user_by_stripe_id(stripe_id: str) -> dict | None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, email, created_at, tier, stripe_id FROM users WHERE stripe_id = ?",
            (stripe_id,),
        )
        row = cursor.fetchone()
        return _row_to_user(row) if row else None


def create_user(email: str, google_sub: str, tier: str = "free") -> dict:
    user_id = google_sub
    created_at = datetime.utcnow()

    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, email, created_at, tier, stripe_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, email, created_at, tier, None),
        )
        conn.commit()

    return {
        "user_id": user_id,
        "email": email,
        "created_at": created_at,
        "tier": tier,
        "stripe_id": None,
    }


def update_user_tier(user_id: str, tier: str):
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET tier = ? WHERE user_id = ?", (tier, user_id))
        conn.commit()


def set_stripe_id(user_id: str, stripe_id: str):
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET stripe_id = ? WHERE user_id = ?", (stripe_id, user_id))
        conn.commit()


def _row_to_user(row) -> dict:
    return {
        "user_id": row[0],
        "email": row[1],
        "created_at": row[2],
        "tier": row[3],
        "stripe_id": row[4],
    }


# --- Usage tracking ---

def log_usage(user_id: str, action: str):
    now = datetime.utcnow()
    month_year = now.strftime("%Y-%m")

    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usage (user_id, action, timestamp, month_year) VALUES (?, ?, ?, ?)",
            (user_id, action, now, month_year),
        )
        conn.commit()


def get_monthly_upload_count(user_id: str, month_year: str = None) -> int:
    month_year = month_year or datetime.utcnow().strftime("%Y-%m")

    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usage WHERE user_id = ? AND action = 'upload' AND month_year = ?",
            (user_id, month_year),
        )
        return cursor.fetchone()[0]
