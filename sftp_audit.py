import os
import datetime
import requests

# === Configuration ===
locations = ["57130", "57138"]
base_dir = os.path.expanduser("~/visualops/toast_exports")
required_files = [
    "ItemSelectionDetails.csv",
    "CheckDetails.csv",
    "OrderDetails.csv",
    "TimeEntries.csv",
    "AccountingReport.xls"
]
log_path = os.path.expanduser("~/visualops/sftp_audit.log")

# Telegram setup
TELEGRAM_TOKEN = "7709042384:AAG8UjZ2hO2vjoSL8RYLjT23w703VS4UJJQ"
CHAT_ID = "8102731631"
alert_triggered = False
alert_messages = []

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# === Generate Date Range ===
today = datetime.date.today()
dates = [(today - datetime.timedelta(days=i)).strftime("%Y%m%d") for i in range(10)]

# === Run Audit ===
with open(log_path, "w") as log:
    log.write("SFTP Audit Report\n")
    log.write("========================================\n")

    for location in locations:
        log.write(f"📍 Location: {location}\n")
        for date in dates:
            folder = os.path.join(base_dir, location, date)
            if not os.path.exists(folder):
                msg = f"  ❌ {date} - Folder Missing"
                log.write(msg + "\n")
                alert_triggered = True
                alert_messages.append(f"{location} | {date} ❌ Missing Folder")
            else:
                missing_files = [f for f in required_files if not os.path.exists(os.path.join(folder, f))]
                if missing_files:
                    msg = f"  ⚠️ {date} - Missing files: {', '.join(missing_files)}"
                    log.write(msg + "\n")
                    alert_triggered = True
                    alert_messages.append(f"{location} | {date} ⚠️ Missing: {', '.join(missing_files)}")
                else:
                    log.write(f"  ✅ {date} - All required files found\n")
        log.write("----------------------------------------\n")

# === Send Telegram Alert if Needed ===
if alert_triggered:
    alert_text = "🚨 SFTP Audit Alert:\n\n" + "\n".join(alert_messages)
    send_telegram_alert(alert_text)
