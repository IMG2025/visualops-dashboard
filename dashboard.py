# dashboard.py
import streamlit as st
import pandas as pd
import os
from utils import load_all_data

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Toast Multi-Location Dashboard")

# --- Sidebar filters ---
location = st.sidebar.selectbox("Select Location", ["57130", "57138"])
export_base = "./toast_exports"
location_path = os.path.join(export_base, location)

if not os.path.exists(location_path):
    st.error("❌ No data folder found for selected location.")
    st.stop()

available_dates = sorted(os.listdir(location_path), reverse=True)
if not available_dates:
    st.error("❌ No date folders found in this location.")
    st.stop()

date = st.sidebar.selectbox("Select Date", available_dates)
DATA_DIR = os.path.join(export_base, location, date)

# --- Pre-load diagnostics ---
st.write("📂 Checking data path:", DATA_DIR)

if os.path.exists(DATA_DIR):
    files = os.listdir(DATA_DIR)
    st.write(f"📄 {len(files)} files found:", files)
else:
    st.error(f"❌ Directory does not exist: {DATA_DIR}")
    st.stop()

# --- Load data ---
data = load_all_data(DATA_DIR)

if not data:
    st.warning("⚠️ No data files could be loaded from this date/location.")
    st.stop()

# --- Load core data ---
items = data.get("AllItemsReport")
checks = data.get("CheckDetails")
labor = data.get("TimeEntries")
kitchen = data.get("KitchenTimings")
orders = data.get("OrderDetails")

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${items['Net Amount'].sum():,.2f}" if items is not None and "Net Amount" in items else "N/A")
col2.metric("🧾 Checks", len(checks) if checks is not None else "N/A")
col3.metric("👥 Employees", labor['Employee'].nunique() if labor is not None and "Employee" in labor else "N/A")

# --- Top Menu Items ---
required_cols = ["Menu Item", "Item Qty", "Gross Amount", "Discount Amount", "Net Amount"]
if items is not None:
    if all(col in items.columns for col in required_cols):
        st.subheader("🍽️ Top Selling Items")
        top_items = items[required_cols]
        st.dataframe(top_items.sort_values(by="Net Amount", ascending=False).head(20))
    else:
        st.warning(f"⚠️ Missing one or more expected columns in AllItemsReport: {required_cols}")

# --- Kitchen Timings ---
if kitchen is not None and "Fulfillment Time" in kitchen.columns:
    st.subheader("⏱️ Kitchen Fulfillment Times")
    kitchen_filtered = kitchen.dropna(subset=["Fulfillment Time"])
    kitchen_filtered["Fulfillment Time"] = pd.to_numeric(kitchen_filtered["Fulfillment Time"], errors="coerce")
    avg_time = kitchen_filtered["Fulfillment Time"].mean()
    st.write(f"Average Fulfillment Time: {avg_time:.2f} minutes")
    st.dataframe(kitchen_filtered[["Check #", "Station", "Fulfillment Time"]].head(15))
else:
    st.info("ℹ️ No kitchen fulfillment time data available.")

# --- Labor Summary ---
if labor is not None and "Job Title" in labor.columns and "Total Pay" in labor.columns:
    st.subheader("🧑‍🍳 Labor Summary by Role")
    summary = labor.groupby("Job Title")["Total Pay"].sum().reset_index().sort_values(by="Total Pay", ascending=False)
    st.dataframe(summary)
else:
    st.info("ℹ️ Labor data is incomplete or missing expected columns.")

# --- Export Option ---
if items is not None:
    st.sidebar.download_button("⬇️ Download 'All Items' CSV", data=items.to_csv(index=False), file_name="AllItems.csv")
