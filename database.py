import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        chat_id BIGINT PRIMARY KEY,
        rate REAL DEFAULT 90,
        markup REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        amount REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS removed_receipts (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        amount REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deductions (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        amount REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cleared (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        amount REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS session_receipts (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT NOT NULL,
        amount REAL NOT NULL
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ── Helpers ───────────────────────────────────────────────

def ensure_settings(cursor, chat_id):
    cursor.execute(
        "INSERT INTO settings (chat_id, rate, markup) VALUES (%s, 90, 0) ON CONFLICT (chat_id) DO NOTHING",
        (chat_id,)
    )


# ── Settings ──────────────────────────────────────────────

def set_rate(chat_id, rate):
    conn = get_connection()
    cursor = conn.cursor()
    ensure_settings(cursor, chat_id)
    cursor.execute(
        "UPDATE settings SET rate = %s WHERE chat_id = %s",
        (rate, chat_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_rate(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    ensure_settings(cursor, chat_id)
    conn.commit()
    cursor.execute(
        "SELECT rate FROM settings WHERE chat_id = %s",
        (chat_id,)
    )
    rate = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return rate


def set_markup(chat_id, markup):
    conn = get_connection()
    cursor = conn.cursor()
    ensure_settings(cursor, chat_id)
    cursor.execute(
        "UPDATE settings SET markup = %s WHERE chat_id = %s",
        (markup, chat_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_markup(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    ensure_settings(cursor, chat_id)
    conn.commit()
    cursor.execute(
        "SELECT markup FROM settings WHERE chat_id = %s",
        (chat_id,)
    )
    markup = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return markup


# ── Receipts (day total) ──────────────────────────────────

def add_receipt(chat_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO receipts (chat_id, amount) VALUES (%s, %s)",
        (chat_id, amount)
    )
    cursor.execute(
        "INSERT INTO session_receipts (chat_id, amount) VALUES (%s, %s)",
        (chat_id, amount)
    )
    conn.commit()
    cursor.close()
    conn.close()


def remove_receipt(chat_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO removed_receipts (chat_id, amount) VALUES (%s, %s)",
        (chat_id, amount)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_receipts_total(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM receipts WHERE chat_id = %s",
        (chat_id,)
    )
    receipts = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM removed_receipts WHERE chat_id = %s",
        (chat_id,)
    )
    removed = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return receipts - removed


# ── Session receipts (since last /clear) ──────────────────

def get_session_total(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM session_receipts WHERE chat_id = %s",
        (chat_id,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def get_session_count(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM session_receipts WHERE chat_id = %s",
        (chat_id,)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def reset_session(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM session_receipts WHERE chat_id = %s",
        (chat_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()


# ── Deductions ────────────────────────────────────────────

def add_deduction(chat_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deductions (chat_id, amount) VALUES (%s, %s)",
        (chat_id, amount)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_total_deductions(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM deductions WHERE chat_id = %s",
        (chat_id,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


# ── Cleared ───────────────────────────────────────────────

def add_cleared(chat_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cleared (chat_id, amount) VALUES (%s, %s)",
        (chat_id, amount)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_total_cleared(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM cleared WHERE chat_id = %s",
        (chat_id,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


# ── Reset day ─────────────────────────────────────────────

def reset_day(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receipts WHERE chat_id = %s", (chat_id,))
    cursor.execute("DELETE FROM removed_receipts WHERE chat_id = %s", (chat_id,))
    cursor.execute("DELETE FROM deductions WHERE chat_id = %s", (chat_id,))
    cursor.execute("DELETE FROM session_receipts WHERE chat_id = %s", (chat_id,))
    conn.commit()
    cursor.close()
    conn.close()