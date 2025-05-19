import os
import streamlit as st
import pandas as pd
import json
from datetime import datetime

EXPORT_PATH = "toast_exports"
LOCATIONS = sorted(os.listdir(EXPORT_PATH))

def get_available_dates(location):
    location_path = os.path.join(EXPORT_PATH, location)
    if not os.path.isdir(location_path):
        return []
    return sorted(os.listdir(location_path), reverse=True)

def load_csv_safe(filepath):
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise ValueError("Empty DataFrame")
        return df
    except Exception as e:
        st.warning(f"❌ Failed to load {os.path.basename(filepath)}: {e}")
        return pd.DataFrame()

def load_json_safe(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"❌ Failed to load {os.path.basename(filepath)}: {e}")
        return {}

st.title("📊 VisualOps: Multi-Location Toast Dashboard")

location = st.selectbox("📍 Select Location", LOCATIONS)
dates = get_available_dates(location)
selected_date = st.selectbox("📅 Select Date", dates)

data_path = os.path.join(EXPORT_PATH, location, selected_date)
st.markdown(f"**Data Path:** `{data_path}`")

# List all available files
available_files = os.listdir(data_path)
st.markdown(f"📂 **Files Found:** `{available_files}`")

# Load files safely
all_items = load_csv_safe(os.path.join(data_path, "AllItemsReport.csv"))
check_details = load_csv_safe(os.path.join(data_path, "CheckDetails.csv"))
time_entries = load_csv_safe(os.path.join(data_path, "TimeEntries.csv"))
kitchen_timings = load_csv_safe(os.path.join(data_path, "KitchenTimings.csv"))
payment_details = load_csv_safe(os.path.join(data_path, "PaymentDetails.csv"))
cash_entries = load_csv_safe(os.path.join(data_path, "CashEntries.csv"))
order_details = load_csv_safe(os.path.join(data_path, "OrderDetails.csv"))
item_selection = load_csv_safe(os.path.join(data_path, "ItemSelectionDetails.csv"))
modifiers = load_csv_safe(os.path.join(data_path, "ModifiersSelectionDetails.csv"))
accounting_report = load_csv_safe(os.path.join(data_path, "AccountingReport.xls"))

menu_export = load_json_safe(os.path.join(data_path, "MenuExport.json"))
menu_export_v2 = load_json_safe(os.path.join(data_path, "MenuExportV2.json"))

if all_items.empty and check_details.empty and item_selection.empty:
    st.error("❌ No valid data could be loaded for this location/date.")
else:
    if not all_items.empty:
        st.subheader("🍽️ Top Menu Items")
        item_summary = all_items['Item Name'].value_counts().reset_index()
        item_summary.columns = ['Item', 'Count']
        st.table(item_summary.head(10))

    if not kitchen_timings.empty:
        st.subheader("⏱️ Kitchen Fulfillment Times")
        avg_time = kitchen_timings['Fulfillment Time'].mean()
        st.write(f"**Average Fulfillment Time:** {round(avg_time, 2)} minutes")
        st.dataframe(kitchen_timings)

    if not time_entries.empty:
        st.subheader("👷 Labor Breakdown by Role")
        if 'Job Title' in time_entries.columns and 'Total Pay' in time_entries.columns:
            labor_summary = time_entries.groupby("Job Title")["Total Pay"].sum().reset_index()
            st.dataframe(labor_summary)
