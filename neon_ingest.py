import os
import base64
import paramiko
import psycopg2
import csv
from io import StringIO
from alerts import send_alert

def main():
    try:
        # === Setup Neon DB connection ===
        conn = psycopg2.connect(
            host=os.getenv("NEON_HOST"),
            database=os.getenv("NEON_DB"),
            user=os.getenv("NEON_USER"),
            password=os.getenv("NEON_PASSWORD"),
            port=5432
        )
        cursor = conn.cursor()

        # === Decode private key for SFTP ===
        private_key_str = base64.b64decode(os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")).decode()
        private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_str))

        # === Connect to SFTP ===
        sftp_host = os.getenv("TOAST_SFTP_HOST")
        sftp_user = os.getenv("TOAST_SFTP_USERNAME")

        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_user, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # === List contents of SFTP root directory ===
        files = sorted(sftp.listdir_attr(), key=lambda f: f.st_mtime, reverse=True)
        print("📂 SFTP contents:", [f.filename for f in files])

        # === Identify latest CSV file ===
        latest_csv = next((f.filename for f in files if f.filename.endswith(".csv")), None)

        if not latest_csv:
            raise Exception("No CSV file found on SFTP server.")

        print(f"📥 Downloading: {latest_csv}")
        with sftp.open(latest_csv) as f:
            content = f.read().decode()

        reader = csv.reader(StringIO(content))
        header = next(reader)

        # === Insert into Neon ===
        print("🚀 Inserting into Neon...")
        cursor.execute("TRUNCATE TABLE toast_raw_data;")
        for row in reader:
            cursor.execute(
                f"INSERT INTO toast_raw_data ({', '.join(header)}) VALUES ({', '.join(['%s'] * len(row))})",
                row
            )

        conn.commit()
        print("✅ Ingestion complete.")
        send_alert("neon_ingest.py", f"{latest_csv}", "Success")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        send_alert("neon_ingest.py", "Ingestion Error", str(e))

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
