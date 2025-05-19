import streamlit as st
import pandas as pd
import os
from utils import load_all_data

st.set_page_config(page_title="📊 VisualOps: Toast Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# --- Sidebar filters ---
export_base = "./toast_exports"
locations = sorted([loc for loc in os.listdir(export_base) if os.path.isdir(os.path.join(export_base, loc))])

if not locations:
    st.error("❌ No locations found.")
    st.stop()

location = st.sidebar.selectbox("Select Location", locations)
location_path = os.path.join(export_base, location)

dates = sorted([d for d in os.listdir(location_path) if os.path.isdir(os.path.join(location_path, d))], reverse=True)
if not dates:
    st.error("❌ No dates found for this location.")
    st.stop()

date = st.sidebar.selectbox("Select Date", dates)
data_path = os.path.join(export_base, location, date)

st.write(f"📂 Data Path: `{data_path}`")

if not os.path.exists(data_path):
    st.error(f"❌ Directory does not exist: {data_path}")
    st.stop()

files = os.listdir(data_path)
st.write(f"📄 {len(files)} files found: {files}")

# --- Load data ---
data = load_all_data(data_path)
# Flatten nested structure if needed
if isinstance(data, dict) and list(data.values())[0] and isinstance(list(data.values())[0], dict):
    data = list(data.values())[0]

# --- Helper ---
def safe_df(name):
    return data.get(name.replace(".csv", "").replace(".json", ""), None)

# --- Load core datasets ---
items = safe_df("AllItemsReport")
checks = safe_df("CheckDetails")
labor = safe_df("TimeEntries")
kitchen = safe_df("KitchenTimings")
orders = safe_df("OrderDetails")
modifiers = safe_df("ModifiersSelectionDetails")
selections = safe_df("ItemSelectionDetails")
payments = safe_df("PaymentDetails")
cash = safe_df("CashEntries")
menu = safe_df("MenuExport")
menu_v2 = safe_df("MenuExportV2")
accounting = safe_df("AccountingReport")

# --- Metrics ---
st.subheader("📈 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("💰 Revenue", f"${items['Net Amount'].sum():,.2f}" if items is not None else "N/A")
col2.metric("🧾 Checks", len(checks) if checks is not None else "N/A")
col3.metric("👥 Employees", labor['Employee'].nunique() if labor is not None else "N/A")

# --- Top Menu Items ---
if items is not None:
    st.subheader("🍽️ Top Selling Items")
    required_cols = ["Menu Item", "Item Qty", "Gross Amount", "Discount Amount", "Net Amount"]
    if all(col in items.columns for col in required_cols):
        top_items = items[required_cols].sort_values(by="Net Amount", ascending=False).head(20)
        st.dataframe(top_items)
    else:
        st.warning("⚠️ Required columns missing in AllItemsReport")

# --- Kitchen Timings ---
if kitchen is not None and "Fulfillment Time" in kitchen:
    st.subheader("⏱️ Kitchen Fulfillment")
    kitchen["Fulfillment Time"] = pd.to_numeric(kitchen["Fulfillment Time"], errors="coerce")
    st.write(f"Average Fulfillment: {kitchen['Fulfillment Time'].mean():.2f} min")
    st.dataframe(kitchen[["Check #", "Station", "Fulfillment Time"]].head(10))

# --- Labor Breakdown ---
if labor is not None and "Job Title" in labor and "Total Pay" in labor:
    st.subheader("🧑‍🍳 Labor Summary")
    labor_summary = labor.groupby("Job Title")["Total Pay"].sum().reset_index()
    st.dataframe(labor_summary.sort_values(by="Total Pay", ascending=False))

# --- Payment Summary ---
if payments is not None:
    st.subheader("💳 Payment Summary")
    summary = payments.groupby("Type")["Amount"].sum().reset_index().sort_values(by="Amount", ascending=False)
    st.dataframe(summary)

# --- Cash Management ---
if cash is not None:
    st.subheader("💵 Cash Entries")
    st.dataframe(cash[["Created Date", "Amount", "Cash Drawer", "Employee", "Action"]].head(10))

# --- Order Summary ---
if orders is not None:
    st.subheader("🧾 Orders Overview")
    st.dataframe(orders[["Order #", "Server", "Dining Area", "Amount", "Tip", "Total"]].head(10))

# --- Export Option ---
if items is not None:
    st.sidebar.download_button("⬇️ Download 'All Items' CSV", data=items.to_csv(index=False), file_name="AllItems.csv")
