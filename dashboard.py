# dashboard.py
import streamlit as st
import pandas as pd
import os
from utils import load_all_data

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Toast Multi-Location Dashboard")

# --- Sidebar filters ---
locations = sorted(os.listdir("toast_exports"))
location = st.sidebar.selectbox("📍 Select Location", locations)

location_path = os.path.join("toast_exports", location)
available_dates = sorted(os.listdir(location_path), reverse=True)
date = st.sidebar.selectbox("📅 Select Date", available_dates)

DATA_DIR = os.path.join(location_path, date)
st.write(f"📂 Loading data from: `{DATA_DIR}`")

if not os.path.exists(DATA_DIR):
    st.error("❌ Selected directory does not exist.")
    st.stop()

files = os.listdir(DATA_DIR)
st.write(f"📄 Found {len(files)} files:", files)

# --- Load Data
data = load_all_data(DATA_DIR)
if not data:
    st.warning("⚠️ No valid data files found in selected directory.")
    st.stop()

# --- Summary Metrics
st.header("📊 Summary")
col1, col2, col3 = st.columns(3)
items = data.get("AllItemsReport")
checks = data.get("CheckDetails")
labor = data.get("TimeEntries")

col1.metric("💰 Revenue", f"${items['Net Amount'].sum():,.2f}" if items is not None else "N/A")
col2.metric("🧾 Checks", len(checks) if checks is not None else "N/A")
col3.metric("👥 Staff", labor["Employee"].nunique() if labor is not None else "N/A")

# --- Display Top Menu Items
if items is not None:
    st.subheader("🍽️ Top Menu Items")
    if all(col in items.columns for col in ["Menu Item", "Item Qty", "Net Amount"]):
        top_items = items.sort_values(by="Net Amount", ascending=False)
        st.dataframe(top_items[["Menu Item", "Item Qty", "Gross Amount", "Discount Amount", "Net Amount"]].head(20))
    else:
        st.warning("⚠️ Expected columns missing in AllItemsReport.csv")

# --- Kitchen Timings
kitchen = data.get("KitchenTimings")
if kitchen is not None and "Fulfillment Time" in kitchen:
    st.subheader("⏱️ Kitchen Timing")
    kitchen["Fulfillment Time"] = pd.to_numeric(kitchen["Fulfillment Time"], errors="coerce")
    st.write(f"Avg Fulfillment Time: {kitchen['Fulfillment Time'].mean():.2f} mins")
    st.dataframe(kitchen[["Check #", "Station", "Fulfillment Time"]].dropna().head(15))

# --- Labor Summary
if labor is not None:
    st.subheader("🧑‍🍳 Labor Cost by Role")
    summary = labor.groupby("Job Title")["Total Pay"].sum().reset_index()
    st.dataframe(summary.sort_values(by="Total Pay", ascending=False))

# --- Item Selections
selections = data.get("ItemSelectionDetails")
if selections is not None:
    st.subheader("📦 Item Selections")
    st.dataframe(selections.head(15))

# --- Modifiers
modifiers = data.get("ModifiersSelectionDetails")
if modifiers is not None:
    st.subheader("🛠️ Modifiers")
    st.dataframe(modifiers.head(15))

# --- Orders
orders = data.get("OrderDetails")
if orders is not None:
    st.subheader("📋 Orders")
    st.dataframe(orders.head(15))

# --- Payments
payments = data.get("PaymentDetails")
if payments is not None:
    st.subheader("💳 Payments")
    st.dataframe(payments.head(15))

# --- Cash Log
cash = data.get("CashEntries")
if cash is not None:
    st.subheader("💵 Cash Log")
    st.dataframe(cash.head(15))

# --- Menu
menu = data.get("MenuExport")
if menu is not None:
    st.subheader("📋 Raw Menu JSON")
    st.json(menu)

# --- Export Button
if items is not None:
    st.sidebar.download_button("⬇️ Export 'All Items' CSV", data=items.to_csv(index=False), file_name="AllItemsReport.csv")
