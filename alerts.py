# alerts.py

import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = "7951699971:AAECBkqySq4WHdZ7uFfwYr-rvCsfgDqUjN0"
TELEGRAM_CHAT_ID = "8102731631"

def send_alert(source, event, result=None):
    timestamp = datetime.utcnow().isoformat() + "Z"
    message = f"""
🚨 <b>MAVEN ALERT</b>
🧠 <b>Source:</b> {source}
🛠️ <b>Event:</b> {event}
📅 <b>Time:</b> {timestamp}
✅ <b>Result:</b> {result or "Success"}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)
