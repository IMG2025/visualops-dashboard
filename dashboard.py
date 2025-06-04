import os
import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")

# --- Load secrets ---
NEON_HOST = os.getenv("NEON_HOST")
NEON_DB = os.getenv("NEON_DB")
NEON_USER = os.getenv("NEON_USER")
NEON_PASSWORD = os.getenv("NEON_PASSWORD")

# --- Debug secrets ---
with st.expander("🔐 Environment Debug"):
    st.write("NEON_HOST:", NEON_HOST or "❌ Missing")
    st.write("NEON_DB:", NEON_DB or "❌ Missing")
    st.write("NEON_USER:", NEON_USER or "❌ Missing")
    st.write("NEON_PASSWORD:", "✅ Loaded" if NEON_PASSWORD else "❌ Missing")

# --- DB Connection ---
if NEON_HOST and NEON_DB and NEON_USER and NEON_PASSWORD:
    try:
        conn = psycopg2.connect(
            host=NEON_HOST,
            dbname=NEON_DB,
            user=NEON_USER,
            password=NEON_PASSWORD,
            sslmode="require"
        )
        st.success("✅ Connected to Neon Database")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        st.stop()
else:
    st.error("❌ One or more Neon secrets missing.")
    st.stop()

# --- Fetch Logs ---
try:
    df = pd.read_sql("SELECT * FROM public.event_logs ORDER BY date DESC LIMIT 50", conn)
    if df.empty:
        st.warning("📭 No logs available in `event_logs` table.")
    else:
        st.subheader("📊 Latest Event Logs")
        st.dataframe(df)
except Exception as e:
    st.error(f"❌ Failed to load logs: {e}")

conn.close()
