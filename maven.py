import threading
import time
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dateutil import parser

# === MAVEN Governance ===
def start_maven():
    print("[MAVEN] MAVEN governance starting...")
    threading.Thread(target=monitor_pulse, daemon=True).start()
    threading.Thread(target=monitor_compliance, daemon=True).start()

# === Pulse Monitoring ===
def monitor_pulse():
    while True:
        try:
            with psycopg2.connect(os.environ['DATABASE_URL'], cursor_factory=psycopg2.extras.RealDictCursor) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT MAX(created_at) as created_at FROM edge_logs WHERE source = 'Pulse' AND action = 'ping';")
                    row = cur.fetchone()
                    if row and row['created_at']:
                        last_ping = row['created_at']
                        if isinstance(last_ping, str):
                            last_ping = parser.parse(last_ping)
                        last_ping = last_ping.replace(tzinfo=None)
                        if datetime.utcnow() - last_ping > timedelta(minutes=3):
                            print("[MAVEN] Pulse heartbeat missing for 3+ minutes.")
                        else:
                            print("[MAVEN] Pulse is healthy.")
                    else:
                        print("[MAVEN] No Pulse heartbeat found.")
        except Exception as e:
            print("[MAVEN] Pulse monitor error:", e)
        time.sleep(60)

# === Compliance Monitoring ===
def monitor_compliance():
    while True:
        try:
            with psycopg2.connect(os.environ['DATABASE_URL'], cursor_factory=psycopg2.extras.RealDictCursor) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT MAX(created_at) as created_at FROM signal_events;")
                    row = cur.fetchone()
                    if row and row['created_at']:
                        last_event = row['created_at']
                        if isinstance(last_event, str):
                            last_event = parser.parse(last_event)
                        last_event = last_event.replace(tzinfo=None)
                        if datetime.utcnow() - last_event > timedelta(minutes=5):
                            print("[MAVEN] Compliance alert: no signal events in 5+ minutes.")
                        else:
                            print("[MAVEN] Compliance signals active.")
                    else:
                        print("[MAVEN] No recent compliance issues.")
        except Exception as e:
            print("[MAVEN] Compliance monitor error:", e)
        time.sleep(60)
