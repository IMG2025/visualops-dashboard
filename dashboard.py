import streamlit as st
import pandas as pd
import psycopg2
import os

# === Use Neon secret env vars ===
DB_CONFIG = {
    'host': os.getenv("NEON_HOST"),
    'dbname': os.getenv("NEON_DB"),
    'user': os.getenv("NEON_USER"),
    'password': os.getenv("NEON_PASSWORD"),
    'port': 5432
}

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("Cole Hospitality - VisualOps Dashboard")

def run_query(query, params=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=colnames)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

# Step 1: Location filter
st.sidebar.header("Filter Data")
location = st.sidebar.selectbox("Select a location", options=["New York", "Los Angeles", "Chicago"])

# Step 2: Fetch dates for selected location
available_dates_query = """
SELECT DISTINCT date
FROM event_logs
WHERE location = %s
ORDER BY date DESC
"""
available_dates_df = run_query(available_dates_query, (location,))

if 'date' not in available_dates_df.columns:
    st.error("The 'date' column was not found in the result. Please verify your database schema or query.")
    st.stop()

available_dates = available_dates_df['date'].tolist()

if not available_dates:
    st.error("No available dates for the selected location.")
    st.stop()

selected_date = st.sidebar.selectbox("Select a date", options=available_dates)

# Step 3: Fetch filtered logs
log_query = """
SELECT timestamp, agent_name, task, status
FROM event_logs
WHERE location = %s AND date = %s
ORDER BY timestamp DESC
"""
log_df = run_query(log_query, (location, selected_date))

st.subheader(f"Agent Activity for {location} on {selected_date}")
if log_df.empty:
    st.warning("No records found.")
else:
    st.dataframe(log_df)
