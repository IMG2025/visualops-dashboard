# signalfetch.py

import os
import paramiko
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USERNAME = os.getenv("TOAST_SFTP_USERNAME")
HOST = os.getenv("TOAST_SFTP_HOST")
KEY_PATH = os.path.expanduser(os.getenv("TOAST_SFTP_KEY_PATH"))
LOCAL_BASE = "toast_exports"

def fetch_exports(location_id, date_str, remote_dir=None):
    if not remote_dir:
        remote_dir = f"/{location_id}/{date_str}"

    local_dir = os.path.join(LOCAL_BASE, location_id, date_str)
    os.makedirs(local_dir, exist_ok=True)

    key = paramiko.RSAKey.from_private_key_file(KEY_PATH)
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USERNAME, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)

    print(f"📦 Fetching data from {remote_dir} to {local_dir}")
    for file in sftp.listdir(remote_dir):
        remote_path = f"{remote_dir}/{file}"
        local_path = os.path.join(local_dir, file)
        sftp.get(remote_path, local_path)
        print(f"✅ Downloaded: {file}")

    sftp.close()
    transport.close()
    print("🚀 Sync complete.")

if __name__ == "__main__":
    fetch_exports("57130", "20250516")
