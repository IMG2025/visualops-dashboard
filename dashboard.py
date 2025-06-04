import streamlit as st
import requests
import os

st.set_page_config(page_title="CoreIdentity Dashboard", layout="wide")

API_BASE = os.getenv("API_BASE_URL", "http://localhost:5000")

st.title("🧠 CoreIdentity Agent Dashboard")

# --- PULSE ---
st.header("Pulse Agent")
if st.button("Ping Pulse Agent"):
    try:
        res = requests.get(f"{API_BASE}/ping")
        st.json(res.json())
    except Exception as e:
        st.error(f"Error pinging Pulse Agent: {e}")

if st.button("Get Pulse Logs"):
    try:
        res = requests.get(f"{API_BASE}/logs/pulse")
        st.json(res.json())
    except Exception as e:
        st.error(f"Error getting Pulse logs: {e}")

# --- DEPLOYR ---
st.header("Deployr Agent")
deploy_service = st.text_input("Enter service to deploy")
if st.button("Trigger Deploy") and deploy_service:
    try:
        res = requests.get(f"{API_BASE}/deployr/{deploy_service}")
        st.json(res.json())
    except Exception as e:
        st.error(f"Deployr Error: {e}")

# --- SUPPLIER ---
st.header("Supplier Agent")
supplier_name = st.text_input("Enter supplier to sync")
if st.button("Sync Supplier") and supplier_name:
    try:
        res = requests.get(f"{API_BASE}/supplier/{supplier_name}")
        st.json(res.json())
    except Exception as e:
        st.error(f"Supplier Error: {e}")

# --- VIA ---
st.header("VIA Agent")
user_id = st.text_input("Track VIA session for user:")
if st.button("Track VIA Session") and user_id:
    try:
        res = requests.get(f"{API_BASE}/via/{user_id}")
        st.json(res.json())
    except Exception as e:
        st.error(f"VIA Error: {e}")

# --- ECHO ---
st.header("Echo Agent")
action = st.text_input("Log user action:")
if st.button("Log Echo Action") and action:
    try:
        res = requests.get(f"{API_BASE}/echo/{action}")
        st.json(res.json())
    except Exception as e:
        st.error(f"Echo Error: {e}")

# --- SIGNAL ---
st.header("Signal Agent")
violation = st.text_input("Report violation detail:")
if st.button("Trigger Violation") and violation:
    try:
        res = requests.get(f"{API_BASE}/signal/{violation}")
        st.json(res.json())
    except Exception as e:
        st.error(f"Signal Error: {e}")

# --- MCP ---
st.header("MCP Intercept")
src = st.text_input("Source")
tgt = st.text_input("Target")
msg = st.text_area("Message Payload (JSON)")

if st.button("Send Intercept") and src and tgt and msg:
    try:
        payload = {
            "source": src,
            "target": tgt,
            "message": json.loads(msg)
        }
        res = requests.post(f"{API_BASE}/mcp/intercept", json=payload)
        st.json(res.json())
    except Exception as e:
        st.error(f"MCP Intercept Error: {e}")
