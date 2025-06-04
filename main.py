from flask import Flask, request, jsonify
import psycopg2
import os
import json
from datetime import datetime

app = Flask(__name__)

# === Neon DB Setup ===
DB_HOST = os.getenv("NEON_HOST")
DB_NAME = os.getenv("NEON_DB")
DB_USER = os.getenv("NEON_USER")
DB_PASSWORD = os.getenv("NEON_PASSWORD")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# === Pulse Agent ===
@app.route("/ping")
def ping():
    return jsonify({"status": "✅ Pulse is active", "time": str(datetime.utcnow())})

@app.route("/logs/pulse")
def get_pulse_logs():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.event_logs ORDER BY date DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Deployr Agent ===
@app.route("/deployr/<service>")
def trigger_deploy(service):
    return jsonify({"status": f"🚀 Deployed service: {service}"})

# === Supplier Agent ===
@app.route("/supplier/<name>")
def sync_supplier(name):
    return jsonify({"status": f"🔄 Synced supplier: {name}"})

# === VIA Agent ===
@app.route("/via/<user_id>")
def track_via(user_id):
    return jsonify({"status": f"👤 Tracked VIA user: {user_id}"})

# === Echo Agent ===
@app.route("/echo/<action>")
def log_echo(action):
    return jsonify({"status": f"📢 Echo action logged: {action}"})

# === Signal Agent ===
@app.route("/signal/<violation>")
def trigger_signal(violation):
    return jsonify({"status": f"🚨 Violation triggered: {violation}"})

# === MCP Intercept ===
@app.route("/mcp/intercept", methods=["POST"])
def intercept():
    try:
        data = request.get_json()
        return jsonify({"status": "📡 Intercept received", "payload": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
