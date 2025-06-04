import streamlit as st
import psycopg2
import os
import pandas as pd

st.set_page_config(page_title="CoreIdentity Dashboard", layout="wide")

# Neon DB connection from environment
NEON_DB_URL = os.getenv("DATABASE_URL")
if not NEON_DB_URL:
    st.error("❌ DATABASE_URL not set.")
    st.stop()

def get_recent_events():
    try:
        conn = psycopg2.connect(NEON_DB_URL)
        query = "SELECT * FROM public.event_logs ORDER BY date DESC LIMIT 25;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Failed to connect to Neon DB: {e}")
        return pd.DataFrame()

st.title("🧠 CoreIdentity VisualOps Dashboard")
st.markdown("Displays most recent event logs directly from Neon PostgreSQL.")

with st.expander("🔍 View Latest Logs"):
    logs_df = get_recent_events()
    if not logs_df.empty:
        st.dataframe(logs_df)
    else:
        st.warning("No data found or failed to connect.")
