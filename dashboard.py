import streamlit as st
import psycopg2
import os
import pandas as pd

# --- Neon Connection ---
NEON_DB = os.getenv("NEON_DB")
NEON_USER = os.getenv("NEON_USER")
NEON_PASSWORD = os.getenv("NEON_PASSWORD")
NEON_HOST = os.getenv("NEON_HOST")

def get_connection():
    return psycopg2.connect(
        dbname=NEON_DB,
        user=NEON_USER,
        password=NEON_PASSWORD,
        host=NEON_HOST,
        port=5432
    )

# --- Streamlit Config ---
st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard (Neon Powered)")

# --- Query Event Logs ---
def load_event_logs():
    query = """
        SELECT id, location, event_type, details, date
        FROM public.event_logs
        ORDER BY date DESC
        LIMIT 50;
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    return df

# --- UI Section ---
try:
    st.subheader("🧠 Recent Event Logs")
    df_logs = load_event_logs()
    st.dataframe(df_logs, use_container_width=True)
except Exception as e:
    st.error(f"❌ Failed to load event logs: {e}")
