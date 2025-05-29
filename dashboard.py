import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import pandas as pd
import traceback

# === Page setup ===
st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps Dashboard")

# === Required environment variables ===
required_env_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing_vars = [var for var in required_env_vars if var not in os.environ or not os.environ[var]]

if missing_vars:
    st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    st.stop()

# === Extract credentials ===
host = os.environ["NEON_HOST"]
dbname = os.environ["NEON_DB"]
user = os.environ["NEON_USER"]
password = os.environ["NEON_PASSWORD"]

# === Attempt connection ===
conn = None
try:
    st.info("🔌 Connecting to Neon database...")
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5
    )
    st.success("✅ Connected to Neon database.")
except OperationalError as e:
    st.error(f"❌ Connection to Neon failed: {e}")
    st.stop()

# === Table listing and preview ===
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

    if tables:
        table_names = [table[0] for table in tables]
        st.subheader("🗂 Available Tables")
        st.write(table_names)

        # Optional: Preview the first table
        selected_table = st.selectbox("Select a table to preview", table_names)
        cur.execute(f"SELECT * FROM {selected_table} LIMIT 10")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=colnames)
        st.subheader(f"📄 Preview of `{selected_table}`")
        st.dataframe(df)
    else:
        st.warning("⚠️ No tables found in the 'public' schema.")

    cur.close()

except Exception as e:
    st.error("❌ An error occurred during query execution.")
    st.exception(traceback.format_exc())

finally:
    if conn:
        conn.close()
