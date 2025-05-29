import os
import csv
import io
import base64
import paramiko
import psycopg2
from datetime import datetime
from alerts import send_alert

# SFTP connection setup
host = os.getenv("TOAST_SFTP_HOST")
username = os.getenv("TOAST_SFTP_USERNAME")
private_key_b64 = os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")
private_key = paramiko.RSAKey.from_private_key(io.StringIO(base64.b64decode(private_key_b64).decode()))

transport = paramiko.Transport((host, 22))
transport.connect(username=username, pkey=private_key)
sftp = paramiko.SFTPClient.from_transport(transport)

# List folders
folders = sftp.listdir("57130")
print("📁 Available date folders:", folders)

# Use most recent folder
latest_folder = sorted(folders)[-1]
file_path = f"57130/{latest_folder}/AllItemsReport.csv"
print(f"📥 Loading file: /{file_path}")

# Read file
with sftp.open(file_path, "r") as f:
    reader = csv.reader(io.StringIO(f.read().decode("utf-8")))
    header = next(reader)
    print("🧾 Header:", header)

    data = []
    for row in reader:
        if len(row) < len(header):
            print(f"⚠️ Skipping malformed row: {row}")
            continue
        data.append(row)

sftp.close()
transport.close()

# DB connection
try:
    conn = psycopg2.connect(
        host=os.getenv("NEON_HOST"),
        database=os.getenv("NEON_DB"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        sslmode="require"
    )
    cursor = conn.cursor()

    # Simple insert or upsert example (adjust to actual schema)
    for row in data:
        try:
            cursor.execute(
                """
                INSERT INTO toast_items (master_id, item_id, parent_id, menu_name, menu_group, subgroup,
                    menu_item, tags, avg_price, item_qty_incl_voids, pct_qty_incl_voids,
                    gross_amt_incl_voids, pct_amt_incl_voids, item_qty, gross_amt,
                    void_qty, void_amt, discount_amt, net_amt, num_orders, pct_orders,
                    pct_qty_group, pct_qty_menu, pct_qty_all, pct_net_amt_group,
                    pct_net_amt_menu, pct_net_amt_all)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """,
                row[:27]  # Trim extra columns if needed
            )
        except Exception as e:
            print(f"⚠️ Skipping row due to DB error: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Ingestion complete.")

    send_alert("✅ Toast ingestion succeeded.")

except Exception as e:
    print("❌ Ingestion failed:", e)
    send_alert(f"❌ Ingestion failed: {e}")
