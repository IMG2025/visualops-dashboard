import os
import base64
import paramiko
import psycopg2
import csv
from io import StringIO
from datetime import datetime
from alerts import send_alert

def main():
    try:
        # === Neon DB Connection ===
        conn = psycopg2.connect(
            host=os.getenv("NEON_HOST"),
            database=os.getenv("NEON_DB"),
            user=os.getenv("NEON_USER"),
            password=os.getenv("NEON_PASSWORD"),
            port=5432
        )
        cursor = conn.cursor()

        # === Decode SFTP Key ===
        private_key_str = base64.b64decode(os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")).decode()
        private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_str))

        # === SFTP Setup ===
        sftp_host = os.getenv("TOAST_SFTP_HOST")
        sftp_user = os.getenv("TOAST_SFTP_USERNAME")
        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_user, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # === Choose location (e.g., 57130)
        location_id = "57130"
        sftp.chdir(f"/{location_id}")
        folders = sorted(sftp.listdir(), reverse=True)
        print("📁 Available date folders:", folders)

        latest_date_folder = folders[0]
        sftp.chdir(f"/{location_id}/{latest_date_folder}")

        # === Choose CSV file to ingest
        csv_file = "AllItemsReport.csv"
        print(f"📥 Loading file: /{location_id}/{latest_date_folder}/{csv_file}")

        with sftp.open(csv_file) as f:
            raw = f.read().decode().strip()

        if not raw:
            raise Exception("CSV file is empty.")

        reader = csv.reader(StringIO(raw))
        header = next(reader, None)
        if not header:
            raise Exception("CSV header not found.")

        print(f"🧾 Header ({len(header)} columns): {header}")

        # === Ingest into Neon
        cursor.execute("TRUNCATE TABLE toast_raw_data;")

        inserted = 0
        for idx, row in enumerate(reader, start=2):  # Start at 2 to account for header
            if len(row) != len(header):
                print(f"⚠️ Row {idx} skipped - column mismatch ({len(row)} vs {len(header)}): {row}")
                continue
            try:
                cursor.execute(
                    f"INSERT INTO toast_raw_data ({', '.join(header)}) VALUES ({', '.join(['%s'] * len(row))})",
                    row
                )
                inserted += 1
            except Exception as e:
                print(f"❌ Failed to insert row {idx}: {row}\nReason: {e}")

        conn.commit()
        print(f"✅ Ingested {inserted} rows.")
        send_alert("neon_ingest.py", csv_file, "Success")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        send_alert("neon_ingest.py", "Failure", str(e))

    finally:
        try:
            cursor.close()
            conn.close()
            sftp.close()
            transport.close()
        except:
            pass

if __name__ == "__main__":
    main()
