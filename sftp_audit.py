import os
import datetime
import requests
import logging

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
TELEGRAM_TOKEN = "7709042384:AAG8UjZ2vjoSL8RYLjT23w703VS4UJJQ"
CHAT_ID = "8102731631"

# === Setup Logging ===
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(message)s'
)

# === Generate Dates ===
today = datetime.date.today()
dates = [(today - datetime.timedelta(days=i)).strftime("%Y%m%d") for i in range(10)]

# === Main Audit Logic ===
alert_triggered = False
alert_messages = []
audit_log = []

logging.info("SFTP Audit Report\n========================================")
for location in locations:
    logging.info(f"📍 Location: {location}")
    audit_log.append(f"📍 Location: {location}")
    for date in dates:
        folder = os.path.join(base_dir, location, date)
        if not os.path.exists(folder):
            msg = f"  ❌ {date} - Folder Missing"
            logging.info(msg)
            audit_log.append(msg)
            alert_triggered = True
            alert_messages.append(f"{location} | {date} ❌ Missing Folder")
        else:
            missing = [f for f in required_files if not os.path.exists(os.path.join(folder, f))]
            if missing:
                msg = f"  ⚠️ {date} - Missing files: {', '.join(missing)}"
                logging.info(msg)
                audit_log.append(msg)
                alert_triggered = True
                alert_messages.append(f"{location} | {date} ⚠️ Missing: {', '.join(missing)}")
            else:
                msg = f"  ✅ {date} - All required files found"
                logging.info(msg)
                audit_log.append(msg)
    logging.info("----------------------------------------")
    audit_log.append("----------------------------------------")

# === Telegram Alert ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        logging.warning(f"Telegram notification failed: {e}")

if alert_triggered:
    alert_text = "🚨 *SFTP Audit Alert: Issues Detected* 🚨\n\n" + "\n".join(alert_messages)
    send_telegram_alert(alert_text)
