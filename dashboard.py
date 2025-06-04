import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps - Toast Logs Dashboard")

# Load environment variables
NEON_HOST = os.getenv("NEON_HOST")
NEON_DB = os.getenv("NEON_DB")
NEON_USER = os.getenv("NEON_USER")
NEON_PASSWORD = os.getenv("NEON_PASSWORD")

# Debug output
with st.expander("🔍 Debug Info"):
    st.write("NEON_HOST:", NEON_HOST)
    st.write("NEON_DB:", NEON_DB)
    st.write("NEON_USER:", NEON_USER)
    st.write("NEON_PASSWORD:", "✅ Loaded" if NEON_PASSWORD else "❌ Missing")

# Database connection string
if NEON_HOST and NEON_DB and NEON_USER and NEON_PASSWORD:
    try:
        conn = psycopg2.connect(
            host=NEON_HOST,
            dbname=NEON_DB,
            user=NEON_USER,
            password=NEON_PASSWORD,
            sslmode="require",
        )
        st.success("✅ Connected to Neon Database")
    except Exception as e:
        st.error(f"❌ Failed to connect to database: {e}")
        st.stop()
else:
    st.error("❌ Missing one or more Neon environment variables")
    st.stop()

# Query recent logs
try:
    df = pd.read_sql("SELECT * FROM public.event_logs ORDER BY date DESC LIMIT 50", conn)
    st.dataframe(df)
except Exception as e:
    st.error(f"❌ Failed to load logs: {e}")

conn.close()
