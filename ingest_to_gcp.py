import psycopg2
import os
from datetime import datetime

# Database credentials
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "coreidentity"
DB_USER = "coreadmin"
DB_PASSWORD = "img2025"

def fetch_event_logs():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.event_logs ORDER BY timestamp DESC LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    logs = fetch_event_logs()
    for log in logs:
        print(log)