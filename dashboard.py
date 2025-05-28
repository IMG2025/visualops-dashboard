import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# --- Database Connection ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://coreuser:changeme@34.27.201.81:5432/coredb")

@st.cache_resource

def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(query):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

# --- UI Filters ---
locations = ["57130", "57138"]
location_id = st.selectbox("📍 Select Location", options=locations)

# Get available dates dynamically
available_dates_query = f"""
    SELECT DISTINCT TO_CHAR(order_date, 'YYYYMMDD') AS date
    FROM visualops.order_details
    WHERE location_id = '{location_id}'
    ORDER BY date DESC
"""
available_dates_df = run_query(available_dates_query)
available_dates = available_dates_df['date'].tolist()

if not available_dates:
    st.error("No available dates for selected location.")
    st.stop()

selected_date = st.selectbox("🗓️ Select Date", options=available_dates)

# --- Data Queries ---
def load_table(table_name):
    query = f"""
        SELECT * FROM visualops.{table_name}
        WHERE location_id = '{location_id}'
          AND TO_CHAR(order_date, 'YYYYMMDD') = '{selected_date}'
    """
    return run_query(query)

# --- Top Menu Items ---
item_df = load_table("item_selection_details")
if not item_df.empty and all(col in item_df.columns for col in ["Menu Item", "Qty", "Net Price"]):
    top_items = item_df.groupby("Menu Item").agg({
        "Qty": "sum",
        "Net Price": "sum"
    }).reset_index().rename(columns={"Qty": "Quantity Sold", "Net Price": "Total Sales"})
    top_items = top_items.sort_values("Quantity Sold", ascending=False)
    st.subheader("🍽️ Top Menu Items")
    st.dataframe(top_items)

# --- Sales Summary ---
check_df = load_table("check_details")
if not check_df.empty:
    st.subheader("💰 Sales Summary")
    st.metric("Total Sales", f"${check_df['Total'].sum():,.2f}" if "Total" in check_df.columns else "N/A")
    st.metric("Total Tax", f"${check_df['Tax'].sum():,.2f}" if "Tax" in check_df.columns else "N/A")
    st.metric("Total Discount", f"${check_df['Discount'].sum():,.2f}" if "Discount" in check_df.columns else "N/A")

# --- Tenders ---
order_df = load_table("order_details")
if not order_df.empty and "Tender" in order_df.columns:
    tender_summary = order_df["Tender"].value_counts().reset_index()
    tender_summary.columns = ["Tender Type", "Count"]
    st.subheader("📦 Order Tenders Summary")
    st.dataframe(tender_summary)

# --- Labor Summary ---
labor_df = load_table("time_entries")
if not labor_df.empty and all(col in labor_df.columns for col in ["Job Title", "Payable Hours", "Total Pay"]):
    st.subheader("👥 Labor Summary")
    labor_summary = labor_df.groupby("Job Title").agg({
        "Payable Hours": "sum",
        "Total Pay": "sum"
    }).reset_index()
    st.dataframe(labor_summary)

# --- All Items ---
all_items_df = load_table("all_items_report")
if not all_items_df.empty:
    st.subheader("📦 All Items Report")
    st.dataframe(all_items_df)
