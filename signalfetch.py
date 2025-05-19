import os
import base64
import paramiko
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SFTP credentials
SFTP_HOST = os.getenv("TOAST_SFTP_HOST")
SFTP_USER = os.getenv("TOAST_SFTP_USERNAME")
PRIVATE_KEY_B64 = os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")

# Constants
LOCATIONS = ["57130", "57138"]
EXPORT_PATH = "toast_exports"

TOAST_EXPORTS = [
    "AllItemsReport.csv",
    "CheckDetails.csv",
    "TimeEntries.csv",
    "KitchenTimings.csv",
    "ItemSelectionDetails.csv",
    "ModifiersSelectionDetails.csv",
    "OrderDetails.csv",
    "PaymentDetails.csv",
    "CashEntries.csv",
    "MenuExport.json",
    "MenuExportV2.json",
    "AccountingReport.xls"
]

# Decode private key for SFTP authentication
def load_private_key():
    try:
        decoded = base64.b64decode(PRIVATE_KEY_B64.encode())
        key_file = "/tmp/temp_rsa"
        with open(key_file, "wb") as f:
            f.write(decoded)
        return paramiko.RSAKey.from_private_key_file(key_file)
    except Exception as e:
        print(f"❌ Failed to decode private key: {e}")
        return None

# Main fetch logic
def fetch_exports():
    key = load_private_key()
    if key is None:
        return

    try:
        transport = paramiko.Transport((SFTP_HOST, 22))
        transport.connect(username=SFTP_USER, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        for location in LOCATIONS:
            print(f"\n📍 Scanning location: {location}")
            try:
                remote_dates = sftp.listdir(f"/{location}")
            except Exception as e:
                print(f"❌ Failed to list remote folder /{location}: {e}")
                continue

            for date in sorted(remote_dates, reverse=True):
                remote_base = f"/{location}/{date}"
                local_dir = os.path.join(EXPORT_PATH, location, date)
                os.makedirs(local_dir, exist_ok=True)

                try:
                    sftp.listdir(remote_base)  # Confirm folder exists
                    print(f"📦 Fetching files from: {remote_base}")
                except Exception:
                    print(f"⚠️  Skipping invalid or inaccessible folder: {remote_base}")
                    continue

                for filename in TOAST_EXPORTS:
                    remote_file = f"{remote_base}/{filename}"
                    local_file = os.path.join(local_dir, filename)

                    if os.path.exists(local_file):
                        print(f"↩️  Skipped (already exists): {filename}")
                        continue

                    try:
                        sftp.get(remote_file, local_file)
                        print(f"✅ Downloaded: {filename}")
                    except Exception as e:
                        print(f"⚠️  Missing or error: {filename} ({e})")

        sftp.close()
        transport.close()
        print("\n🚀 Fetch complete for all available folders.")

    except Exception as e:
        print(f"❌ SFTP connection failed: {e}")

if __name__ == "__main__":
    fetch_exports()
