id="db1"
import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "data/epds.db"


# -----------------------------
# اتصال به دیتابیس
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# ساخت جدول
# -----------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        region TEXT,
        name TEXT,
        lastname TEXT,
        phone TEXT,
        epi_score REAL,
        priority TEXT,

        affected_people INTEGER,
        injured INTEGER,

        critical INTEGER,
        unconscious INTEGER,
        bleeding INTEGER,
        trapped INTEGER,

        water INTEGER,
        food INTEGER,
        medicine INTEGER,

        blocked INTEGER,

        text TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# ذخیره گزارش
# -----------------------------
def save_report(report: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reports (
        timestamp, region, name, lastname, phone,
        epi_score, priority,
        affected_people, injured,
        critical, unconscious, bleeding, trapped,
        water, food, medicine,
        blocked, text
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        report.get("region"),
        report.get("name"),
        report.get("lastname"),
        report.get("phone"),
        report.get("epi_score"),
        report.get("priority"),
        report.get("affected_people"),
        report.get("injured"),
        int(report.get("critical", False)),
        int(report.get("unconscious", False)),
        int(report.get("bleeding", False)),
        int(report.get("trapped", False)),
        report.get("water"),
        report.get("food"),
        report.get("medicine"),
        int(report.get("blocked", False)),
        report.get("text")
    ))

    conn.commit()
    conn.close()


# -----------------------------
# گرفتن همه گزارش‌ها
# -----------------------------
def get_all_reports():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM reports ORDER BY epi_score DESC", conn)
    conn.close()
    return df


# -----------------------------
# فیلتر بر اساس سطح بحران
# -----------------------------
def get_reports_by_priority(priority):
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM reports WHERE priority = ? ORDER BY epi_score DESC",
        conn,
        params=(priority,)
    )

    conn.close()
    return df
