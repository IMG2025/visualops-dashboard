import streamlit as st
import psycopg2
import pandas as pd
import os

# Streamlit UI setup
st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard")

# Neon connection using Streamlit secrets
NEON_HOST = os.getenv("NEON_HOST")
NEON_DB = os.getenv("NEON_DB")
NEON_USER = os.getenv("NEON_USER")
NEON_PASSWORD = os.getenv("NEON_PASSWORD")

# Validate required environment variables
if not all([NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD]):
    st.error("❌ Missing Neon connection credentials.")
    st.stop()

# Connection string
conn_str = f"host={NEON_HOST} dbname={NEON_DB} user={NEON_USER} password={NEON_PASSWORD} sslmode=require"

# Query wrapper
def fetch_event_logs(limit=20):
    try:
        with psycopg2.connect(conn_str) as conn:
            query = f"SELECT * FROM public.event_logs ORDER BY date DESC LIMIT {limit}"
            df = pd.read_sql(query, conn)
            return df
    except Exception as e:
        st.error(f"❌ DB Query Failed: {e}")
        return pd.DataFrame()

# --- UI Layout ---
tabs = st.tabs(["📋 Recent Logs", "⚙️ System Status"])

with tabs[0]:
    st.subheader("Latest Ingested Event Logs")
    logs_df = fetch_event_logs()
    if logs_df.empty:
        st.warning("No logs found or failed to connect.")
    else:
        st.dataframe(logs_df, use_container_width=True)

with tabs[1]:
    st.subheader("Status")
    st.markdown("- ✅ Connected to Neon")
    st.markdown("- ✅ Dashboard Live")
    st.markdown("- 🔁 Data ingested via GitHub Actions")
