import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import time

import streamlit as st
st.info("🟢 Forced redeploy - Streamlit is running dashboard.py")

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard")

print("✅ Streamlit UI initialized")

# === 1. Check secrets ===
required_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing = [var for var in required_vars if not os.environ.get(var)]

if missing:
    st.error(f"❌ Missing required secrets: {', '.join(missing)}")
    print("❌ Missing secrets:", missing)
    st.stop()

st.success("✅ All required environment variables present.")
print("✅ Environment variables loaded")

# === 2. Log variables for debug ===
with st.expander("🔧 Debug: Secrets"):
    for var in required_vars:
        st.write(f"{var}: {os.environ.get(var)}")
print("✅ Secrets rendered in expander")

# === 3. Try DB connection ===
host = os.environ["NEON_HOST"]
dbname = os.environ["NEON_DB"]
user = os.environ["NEON_USER"]
password = os.environ["NEON_PASSWORD"]

st.info("🔌 Attempting to connect to Neon...")
print("🔌 Connecting to Neon with:", host, dbname, user)

conn = None
try:
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5
    )
    st.success("✅ Connected to Neon.")
    print("✅ Neon DB connection successful.")
except OperationalError as e:
    st.error(f"❌ DB connection failed: {e}")
    print("❌ DB connection failed:", str(e))
    st.stop()

# === 4. Run a basic query ===
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    cur.close()
    conn.close()

    if tables:
        st.subheader("📂 Tables in Neon Database")
        st.write([t[0] for t in tables])
        print("✅ Tables retrieved:", [t[0] for t in tables])
    else:
        st.warning("⚠️ No tables found.")
        print("⚠️ No tables found in public schema.")
except Exception as e:
    st.error(f"❌ Query failed: {e}")
    print("❌ Query failed:", str(e))
