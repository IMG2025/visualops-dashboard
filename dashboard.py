import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Event Log Dashboard")

# Load Neon DB credentials from Streamlit secrets or env
DB_SETTINGS = {
    "host": os.getenv("NEON_HOST", st.secrets.get("NEON_HOST")),
    "dbname": os.getenv("NEON_DB", st.secrets.get("NEON_DB")),
    "user": os.getenv("NEON_USER", st.secrets.get("NEON_USER")),
    "password": os.getenv("NEON_PASSWORD", st.secrets.get("NEON_PASSWORD")),
    "port": 5432
}

# Connect to Neon
@st.cache_resource(show_spinner=False)
def get_conn():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to Neon: {e}")
        return None

# Load recent logs from event_logs
@st.cache_data(ttl=60)
def load_logs():
    conn = get_conn()
    if conn is None:
        return pd.DataFrame()
    try:
        return pd.read_sql("SELECT * FROM public.event_logs ORDER BY date DESC LIMIT 100", conn)
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        return pd.DataFrame()

# Display logs
df = load_logs()
if not df.empty:
    st.subheader("🧠 Recent Event Logs")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No logs found or failed to load from Neon.")

# Diagnostic block
with st.expander("🔍 Connection Debug Info"):
    st.json(DB_SETTINGS)
