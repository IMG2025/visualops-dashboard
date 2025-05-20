import os

# Base SFTP mount or sync root directory
base_dir = "toast_exports"

# Replace with actual location and range of dates to verify
locations = ["57130", "57138"]
dates = ["20250517", "20250518", "20250519", "20250520"]

print("📋 SFTP Folder Presence Audit")
for location in locations:
    for date in dates:
        path = os.path.join(base_dir, location, date)
        exists = os.path.exists(path)
        status = "✅ FOUND" if exists else "❌ MISSING"
        print(f"{path:<40} {status}")
