import os
import paramiko
from io import StringIO
from datetime import datetime, timedelta

# Load credentials from environment
SFTP_HOST = os.getenv("TOAST_SFTP_HOST")
SFTP_USER = os.getenv("TOAST_SFTP_USERNAME")
SFTP_KEY_B64 = os.getenv("TOAST_SFTP_PRIVATE_KEY_B64")

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

def last_n_dates(n=7):  # Use 7 for GitHub job timeout safety
    today = datetime.utcnow()
    return [(today - timedelta(days=i)).strftime('%Y%m%d') for i in range(n)]

def fetch_exports():
    try:
        private_key_str = paramiko.RSAKey.from_private_key(StringIO(SFTP_KEY_B64))
        transport = paramiko.Transport((SFTP_HOST, 22))
        transport.connect(username=SFTP_USER, pkey=private_key_str)
        sftp = paramiko.SFTPClient.from_transport(transport)

        for location in LOCATIONS:
            print(f"\n📍 Scanning location: {location}")
            for date in last_n_dates():
                remote_base = f"/{location}/{date}"
                local_dir = os.path.join(EXPORT_PATH, location, date)
                os.makedirs(local_dir, exist_ok=True)

                try:
                    sftp.listdir(remote_base)
                    print(f"✅ Folder exists: {remote_base}")
                except FileNotFoundError:
                    print(f"❌ Folder not found: {remote_base}")
                    continue

                for filename in TOAST_EXPORTS:
                    remote_file = f"{remote_base}/{filename}"
                    local_file = os.path.join(local_dir, filename)

                    if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
                        print(f"↩️  Skipped (already exists): {filename}")
                        continue

                    try:
                        with sftp.open(remote_file, 'r') as rf:
                            contents = rf.read()
                            if contents:
                                with open(local_file, 'wb') as f:
                                    f.write(contents)
                                print(f"✅ Downloaded: {filename}")
                            else:
                                print(f"⚠️  Skipped empty: {filename}")
                    except Exception as e:
                        print(f"⚠️  Error reading {filename}: {e}")

        sftp.close()
        transport.close()
        print("\n🚀 Fetch complete.")

    except Exception as e:
        print(f"❌ SFTP fetch failed: {e}")

if __name__ == "__main__":
    fetch_exports()
