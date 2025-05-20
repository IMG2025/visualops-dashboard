import os
from datetime import datetime, timedelta

# === CONFIGURATION ===
locations = ["57130", "57138"]
days_back = 10
base_path = "toast_exports"

# === Generate Expected Date List ===
date_list = [(datetime.today() - timedelta(days=i)).strftime("%Y%m%d") for i in range(days_back)]

# === Scan Results ===
print("SFTP Audit Report\n" + "="*40)
for loc in locations:
    loc_path = os.path.join(base_path, loc)
    print(f"📍 Location: {loc}")
    if not os.path.exists(loc_path):
        print(f"  ❌ Location folder not found: {loc_path}")
        continue

    for date in date_list:
        date_path = os.path.join(loc_path, date)
        if os.path.exists(date_path) and os.path.isdir(date_path):
            print(f"  ✅ {date} - Found")
        else:
            print(f"  ❌ {date} - Missing")
    print("-" * 40)
