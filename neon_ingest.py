import os
import csv
import io
import paramiko
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

from alerts import send_alert  # Optional: triggers Telegram alert

# Load environment variables
load_dotenv()

# === SFTP Configuration ===
SFTP_HOST = os.getenv("TOAST_SFTP_HOST")
SFTP_USERNAME = os.getenv("TOAST_SFTP_USERNAME")
SFTP_PRIVATE_KEY_B64 = os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")

# === PostgreSQL Configuration ===
DB_HOST = os.getenv("NEON_HOST")
DB_NAME = os.getenv("NEON_DB")
DB_USER = os.getenv("NEON_USER")
DB_PASSWORD = os.getenv("NEON_PASSWORD")

# === SFTP Connection ===
def connect_sftp():
    import base64
    key_data = base64.b64decode(SFTP_PRIVATE_KEY_B64)
    pkey = paramiko.RSAKey.from_private_key(io.StringIO(key_data.decode()))
    transport = paramiko.Transport((SFTP_HOST, 22))
    transport.connect(username=SFTP_USERNAME, pkey=pkey)
    return paramiko.SFTPClient.from_transport(transport)

# === Database Connection ===
def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )

# === Process a CSV File ===
def process_csv(file_stream, cursor):
    reader = csv.reader(io.TextIOWrapper(file_stream, encoding='utf-8'))
    headers = next(reader, None)
    print("🧾 Header:", headers)

    for row in reader:
        try:
            if len(row) < 5:
                print("⚠️ Skipping malformed row:", row)
                continue
            item_id = row[1]
            menu_name = row[3]
            gross_amount = float(row[12]) if row[12] else 0.0
            cursor.execute(
                "INSERT INTO toast_data (item_id, menu_name, gross_amount) VALUES (%s, %s, %s)",
                (item_id, menu_name, gross_amount)
            )
        except Exception as e:
            print("🚨 Error inserting row:", row)
            print(e)
            continue

# === Main Ingestion Function ===
def main():
    try:
        sftp = connect_sftp()
        folders = sftp.listdir("57130")
        print("📁 Available date folders:", folders)

        if not folders:
            print("❌ No folders found.")
            return

        latest_folder = sorted(folders)[-1]
        filepath = f"/57130/{latest_folder}/AllItemsReport.csv"
        print("📥 Loading file:", filepath)

        file_stream = sftp.file(filepath, mode='r')
        conn = connect_db()
        cursor = conn.cursor()

        process_csv(file_stream, cursor)

        conn.commit()
        cursor.close()
        conn.close()
        sftp.close()

        print("✅ Ingestion complete")
        send_alert("✅ Toast ingestion complete.")
    except Exception as e:
        print("❌ Ingestion failed:", str(e))
        send_alert(f"❌ Ingestion failed: {str(e)}")

if __name__ == "__main__":
    main()
