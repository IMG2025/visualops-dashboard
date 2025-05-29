import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import pandas as pd

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")

st.title("📊 VisualOps Dashboard")

# === Validate Secrets ===
required_env_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing_vars = [var for var in required_env_vars if var not in os.environ or not os.environ[var]]

if missing_vars:
    st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    st.stop()

# === Extract credentials ===
host = os.environ["NEON_HOST"]
dbname = os.environ["NEON_DB"]
user = os.environ["NEON_USER"]
password = os.environ["NEON_PASSWORD"]

# === Attempt database connection ===
conn = None
try:
    st.info("🔌 Connecting to Neon database...")
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5
    )
    st.success("✅ Connected to Neon database.")
except OperationalError as e:
    st.error(f"❌ Could not connect to Neon: {e}")
    st.stop()

# === Example Query with Safeguard ===
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

    if tables:
        st.subheader("🗂 Available Tables")
        st.write([table[0] for table in tables])
    else:
        st.warning("⚠️ No tables found in your Neon database.")

    cur.close()
except Exception as e:
    st.error(f"❌ Query failed: {e}")
finally:
    if conn:
        conn.close()
