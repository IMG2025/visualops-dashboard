import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import pandas as pd

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard")

# === Diagnostic Check ===
st.info("✅ `dashboard.py` loaded and executing...")

# === 1. Check Secrets ===
required_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing = [var for var in required_vars if var not in os.environ or not os.environ[var]]

if missing:
    st.error(f"❌ Missing secrets: {', '.join(missing)}")
    st.stop()

# === 2. Debug output ===
with st.expander("🔐 Environment Variables"):
    for var in required_vars:
        masked = os.environ[var] if "PASS" not in var else "********"
        st.write(f"{var}: {masked}")

# === 3. Extract creds ===
host = os.environ["NEON_HOST"]
dbname = os.environ["NEON_DB"]
user = os.environ["NEON_USER"]
password = os.environ["NEON_PASSWORD"]

# === 4. Attempt DB Connection ===
conn = None
with st.spinner("🔌 Connecting to Neon..."):
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=5
        )
        st.success("✅ Connected to Neon.")
    except OperationalError as e:
        st.error(f"❌ Connection failed: {e}")
        st.stop()

# === 5. Verify Data Access ===
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

    if tables:
        st.subheader("📂 Tables in Database")
        st.write([t[0] for t in tables])
    else:
        st.warning("⚠️ No tables found.")

    cur.close()
except Exception as e:
    st.error(f"❌ Query failed: {e}")
finally:
    if conn:
        conn.close()
