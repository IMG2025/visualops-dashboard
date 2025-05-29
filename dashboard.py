import streamlit as st
import os
import psycopg2
from psycopg2 import OperationalError
import pandas as pd

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("✅ VisualOps Boot Check")

st.write("🔍 Stage 1: Environment Check")
required_vars = ["NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"]
missing = [var for var in required_vars if var not in os.environ or not os.environ[var]]
if missing:
    st.error(f"❌ Missing secrets: {', '.join(missing)}")
    st.stop()
else:
    st.success("✅ All environment secrets loaded.")

st.write("🔍 Stage 2: DB Connection Check")
try:
    conn = psycopg2.connect(
        host=os.environ["NEON_HOST"],
        dbname=os.environ["NEON_DB"],
        user=os.environ["NEON_USER"],
        password=os.environ["NEON_PASSWORD"],
        connect_timeout=5
    )
    st.success("✅ Connected to Neon DB.")
except OperationalError as e:
    st.error(f"❌ Could not connect: {e}")
    st.stop()

st.write("🔍 Stage 3: Verifying Tables...")
try:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    st.write("📦 Tables:", [t[0] for t in tables])
    cur.close()
except Exception as e:
    st.error(f"❌ Query error: {e}")
finally:
    conn.close()
