import os
import paramiko
import base64
import logging
from dotenv import load_dotenv
from datetime import datetime

# === Load credentials ===
load_dotenv()

SFTP_HOST = os.getenv("TOAST_SFTP_HOST")
SFTP_USER = os.getenv("TOAST_SFTP_USERNAME")
PRIVATE_KEY_B64 = os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")

if not all([SFTP_HOST, SFTP_USER, PRIVATE_KEY_B64]):
    raise EnvironmentError("Missing one or more required SFTP environment variables.")

# === Decode private key ===
decoded_key = base64.b64decode(PRIVATE_KEY_B64).decode("utf-8")
key_path = "/tmp/sftp_key.pem"
with open(key_path, "w") as f:
    f.write(decoded_key)
os.chmod(key_path, 0o600)

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
EXPORT_DIR = "toast_exports"
TODAY = datetime.utcnow().strftime("%Y%m%d")

# === Files to fetch per location ===
LOCATIONS = ["57130", "57138"]
FILENAMES = [
    "AllItemsReport.csv",
    "CheckDetails.csv",
    "ItemSelectionDetails.csv",
    "KitchenTimings.csv",
    "MenuExport.json",
    "MenuExportV2.json",
    "ModifiersSelectionDetails.csv",
    "OrderDetails.csv",
    "TimeEntries.csv",
]

def fetch_exports():
    key = paramiko.RSAKey.from_private_key_file(key_path)
    transport = paramiko.Transport((SFTP_HOST, 22))
    transport.connect(username=SFTP_USER, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)

    for location_id in LOCATIONS:
        remote_base = f"/{location_id}/{TODAY}/"
        local_base = os.path.join(EXPORT_DIR, location_id, TODAY)
        os.makedirs(local_base, exist_ok=True)

        logging.info(f"📦 Fetching for location {location_id}")
        for filename in FILENAMES:
            remote_path = os.path.join(remote_base, filename)
            local_path = os.path.join(local_base, filename)
            try:
                sftp.get(remote_path, local_path)
                logging.info(f"✅ Downloaded {filename}")
            except FileNotFoundError:
                logging.warning(f"⚠️ File not found: {remote_path}")

    sftp.close()
    transport.close()
    logging.info("🎉 All exports completed.")

if __name__ == "__main__":
    fetch_exports()
