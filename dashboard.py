import streamlit as st
import psycopg2
import pandas as pd
import os

# --- Page Config ---
st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 CoreIdentity VisualOps Dashboard")

# --- Environment Setup ---
NEON_HOST = os.getenv("NEON_HOST")
NEON_DB = os.getenv("NEON_DB")
NEON_USER = os.getenv("NEON_USER")
NEON_PASSWORD = os.getenv("NEON_PASSWORD")

# --- Validate Secrets ---
if not all([NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD]):
    st.error("❌ One or more required Neon environment variables are missing.")
    st.stop()

# --- Connect to Neon ---
def get_connection():
    try:
        conn = psycopg2.connect(
            host=NEON_HOST,
            dbname=NEON_DB,
            user=NEON_USER,
            password=NEON_PASSWORD,
            sslmode="require"
        )
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to Neon: {e}")
        return None

# --- Fetch and Display Logs ---
def show_event_logs():
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, location, event_type, details, date FROM public.event_logs ORDER BY date DESC LIMIT 100")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)
            st.subheader("🧠 Most Recent Event Logs")
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error querying Neon DB: {e}")
    finally:
        conn.close()

# --- Main Render ---
show_event_logs()

st.caption("Powered by Neon & Streamlit | CoreIdentity 2025")
