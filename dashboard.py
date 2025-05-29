import streamlit as st
import os
import psycopg2
import pandas as pd
from psycopg2 import OperationalError

st.set_page_config(page_title="CoreIdentity Dashboard", layout="wide")
st.title("🧪 VisualOps Diagnostic")

# === Stage 1: Sanity Check ===
st.info("✅ dashboard.py is loading...")
st.code("📂 Running file: dashboard.py")

# === Stage 2: Environment Variables ===
required_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    st.error(f"❌ Missing secrets: {', '.join(missing)}")
    st.stop()

st.success("✅ All secrets loaded.")

# === Stage 3: Connect to Neon ===
try:
    st.write("🔌 Connecting to Neon...")
    conn = psycopg2.connect(
        host=os.environ["NEON_HOST"],
        dbname=os.environ["NEON_DB"],
        user=os.environ["NEON_USER"],
        password=os.environ["NEON_PASSWORD"],
        connect_timeout=5
    )
    st.success("✅ Connection successful.")
except OperationalError as e:
    st.error(f"❌ Connection failed: {e}")
    st.stop()

# === Stage 4: Test Query ===
try:
    st.write("🔍 Running test query...")
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    now = cur.fetchone()[0]
    st.success(f"🕒 Database time: {now}")
    cur.close()
except Exception as e:
    st.error(f"❌ Query error: {e}")
finally:
    conn.close()
