import os
from datetime import datetime, timedelta

locations = ["57130", "57138"]
base_path = "/Users/toddmorgan/visualops/toast_exports"
required_files = [
    "ItemSelectionDetails.csv",
    "CheckDetails.csv",
    "OrderDetails.csv",
    "TimeEntries.csv"
]

# Generate last 10 days
today = datetime.today()
dates = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(10)]

print("SFTP Audit Report")
print("=" * 40)

for loc in locations:
    print(f"📍 Location: {loc}")
    loc_path = os.path.join(base_path, loc)

    for date in dates:
        date_path = os.path.join(loc_path, date)
        if not os.path.exists(date_path):
            print(f"  ❌ {date} - Folder Missing")
        else:
            # Check if required files exist
            missing = []
            for req in required_files:
                if not os.path.exists(os.path.join(date_path, req)):
                    missing.append(req)
            if missing:
                print(f"  ⚠️ {date} - Missing files: {', '.join(missing)}")
            else:
                print(f"  ✅ {date} - All required files found")
    print("-" * 40)
