import os
import base64
import paramiko
import psycopg2
import csv
from io import StringIO

# === Setup Neon DB connection ===
db_conn = psycopg2.connect(
    host=os.getenv("NEON_HOST"),
    database=os.getenv("NEON_DB"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    port=5432
)
cursor = db_conn.cursor()

# === Load and decode private key ===
private_key_str = base64.b64decode(os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")).decode()
private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_str))

# === Connect to SFTP ===
sftp_host = os.getenv("TOAST_SFTP_HOST")
sftp_user = os.getenv("TOAST_SFTP_USERNAME")

transport = paramiko.Transport((sftp_host, 22))
transport.connect(username=sftp_user, pkey=private_key)
sftp = paramiko.SFTPClient.from_transport(transport)

# === Fetch latest CSV file ===
files = sorted(sftp.listdir_attr(), key=lambda f: f.st_mtime, reverse=True)
latest_csv = next((f.filename for f in files if f.filename.endswith(".csv")), None)

if not latest_csv:
    raise Exception("No CSV file found on SFTP server.")

with sftp.open(latest_csv) as f:
    content = f.read().decode()

reader = csv.reader(StringIO(content))
header = next(reader)

# === Insert into Neon DB ===
cursor.execute("TRUNCATE TABLE toast_raw_data;")
for row in reader:
    cursor.execute(
        f"INSERT INTO toast_raw_data ({', '.join(header)}) VALUES ({', '.join(['%s'] * len(row))})",
        row
    )

db_conn.commit()
cursor.close()
db_conn.close()
sftp.close()
transport.close()

print("✅ Ingestion complete.")
