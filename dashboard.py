# dashboard.py
import streamlit as st
import pandas as pd
import os
from utils import load_all_data

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

EXPORT_BASE = "toast_exports"

# --- Sidebar Filters ---
locations = sorted([loc for loc in os.listdir(EXPORT_BASE) if os.path.isdir(os.path.join(EXPORT_BASE, loc))])
location = st.sidebar.selectbox("📍 Select Location", locations)

date_path = os.path.join(EXPORT_BASE, location)
dates = sorted([d for d in os.listdir(date_path) if os.path.isdir(os.path.join(date_path, d))], reverse=True)
date = st.sidebar.selectbox("📅 Select Date", dates)

DATA_PATH = os.path.join(EXPORT_BASE, location, date)
st.markdown(f"📁 **Data Path:** `{DATA_PATH}`")

files = os.listdir(DATA_PATH)
st.markdown(f"📄 **{len(files)} files found:** `{files}`")

# --- Load Data ---
data = load_all_data(location, date)

if not data or not isinstance(data, dict):
    st.error("❌ No valid data could be loaded for this location/date.")
    st.stop()

# --- Summary Metrics ---
st.subheader("📈 Summary Metrics")

items = data.get("AllItemsReport")
checks = data.get("CheckDetails")
labor = data.get("TimeEntries")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Revenue", f"${items['Net Amount'].sum():,.2f}" if items is not None and "Net Amount" in items else "N/A")
col2.metric("🧾 Checks", str(len(checks)) if checks is not None else "N/A")
col3.metric("👥 Employees", labor['Employee'].nunique() if labor is not None and "Employee" in labor else "N/A")

# --- Top Menu Items ---
st.subheader("🍽️ Top Menu Items")
required_columns = ["Menu Item", "Item Qty", "Gross Amount", "Discount Amount", "Net Amount"]

if items is not None and all(col in items.columns for col in required_columns):
    top_items = items[required_columns]
    st.dataframe(top_items.sort_values(by="Net Amount", ascending=False).head(15))
else:
    st.warning("⚠️ Expected columns missing in AllItemsReport.csv")

# --- Item Selection Details ---
selection = data.get("ItemSelectionDetails")
if selection is not None and "Menu Item" in selection.columns:
    st.subheader("📦 Item Selections")
    st.dataframe(selection[["Menu Item"]].value_counts().reset_index(name="Count").head(10))

# --- Kitchen Timings ---
kitchen = data.get("KitchenTimings")
if kitchen is not None and "Fulfillment Time" in kitchen.columns:
    st.subheader("⏱️ Kitchen Fulfillment Times")
    kitchen["Fulfillment Time"] = pd.to_numeric(kitchen["Fulfillment Time"], errors="coerce")
    kitchen_filtered = kitchen.dropna(subset=["Fulfillment Time"])
    avg_time = kitchen_filtered["Fulfillment Time"].mean()
    st.write(f"⏳ **Average Fulfillment Time:** `{avg_time:.2f} minutes`")
    st.dataframe(kitchen_filtered[["Check #", "Station", "Fulfillment Time"]].head(10))
else:
    st.info("ℹ️ No kitchen fulfillment time data available.")

# --- Labor Breakdown ---
if labor is not None and "Job Title" in labor.columns and "Total Pay" in labor.columns:
    st.subheader("👷 Labor Breakdown by Role")
    labor_summary = labor.groupby("Job Title")["Total Pay"].sum().reset_index().sort_values(by="Total Pay", ascending=False)
    st.dataframe(labor_summary)
else:
    st.info("ℹ️ Labor data is incomplete or missing expected columns.")

# --- Export Option ---
if items is not None:
    st.sidebar.download_button("⬇️ Export 'All Items' CSV", data=items.to_csv(index=False), file_name="AllItems.csv")
