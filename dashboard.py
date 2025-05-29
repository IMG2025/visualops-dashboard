import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import pandas as pd

print("✅ dashboard.py: beginning execution")

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard")
st.info("✅ Streamlit is rendering this line.")  # Confirm UI is alive

# === 1. Check for required secrets ===
required_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing = [var for var in required_vars if var not in os.environ or not os.environ[var]]

if missing:
    st.error(f"❌ Missing required environment variables: {', '.join(missing)}")
    st.stop()

# === 2. Print all secrets for confirmation in the expander ===
with st.expander("🔧 Debug: Loaded Environment Variables"):
    for var in required_vars:
        st.write(f"{var}: {os.environ.get(var)}")

# === 3. Extract connection info ===
host = os.environ["NEON_HOST"]
dbname = os.environ["NEON_DB"]
user = os.environ["NEON_USER"]
password = os.environ["NEON_PASSWORD"]

# === 4. Connect to the database ===
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
        st.error(f"❌ Could not connect to Neon: {e}")
        st.stop()

# === 5. Run a test query ===
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    cur.close()

    if tables:
        st.subheader("📂 Tables in your Neon Database")
        st.write([t[0] for t in tables])
    else:
        st.warning("⚠️ No tables found in the public schema.")
except Exception as e:
    st.error(f"❌ Failed to run test query: {e}")
finally:
    if conn:
        conn.close()
        print("✅ Closed Neon connection.")
