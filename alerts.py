# alerts.py

import os
import requests
from datetime import datetime

# ✅ Ensure these are set in your environment securely
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "7951699971:AAECBkqySq4WHdZ7uFfwYr-rvCsfgDqUjN0"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8102731631"

def send_alert(source: str, event: str, result: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = (
        f"🚨 *MAVEN Alert Triggered!*\n"
        f"🧠 Source: *{source}*\n"
        f"🔧 Event: *{event}*\n"
        f"✅ Result: {result}\n"
        f"🕒 Time: `{timestamp}`"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.ok:
            print("✅ Alert sent successfully.")
        else:
            print(f"❌ Failed to send alert: {response.text}")
    except Exception as e:
        print(f"❌ Exception during alert send: {e}")
