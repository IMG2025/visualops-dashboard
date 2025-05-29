import streamlit as st
import psycopg2
import pandas as pd
import os

st.title("📊 VisualOps Dashboard")

conn = psycopg2.connect(
    host=os.getenv("NEON_HOST"),
    database=os.getenv("NEON_DB"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    port=5432
)

df = pd.read_sql("SELECT * FROM toast_raw_data ORDER BY timestamp DESC LIMIT 100", conn)
st.dataframe(df)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
summary = df.groupby('date').agg(total_orders=('order_id', 'count'),
                                 total_revenue=('price', 'sum')).reset_index()

st.line_chart(summary.set_index('date'))
conn.close()
