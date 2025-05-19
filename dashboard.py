import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

base_path = "toast_exports"

# Select location
location_ids = sorted(os.listdir(base_path))
location = st.selectbox("📍 Select Location", location_ids)

# Select date
dates = sorted(os.listdir(os.path.join(base_path, location)))
date = st.selectbox("📅 Select Date", dates)

data_path = os.path.join(base_path, location, date)
st.markdown(f"**Data Path:** `{data_path}`")

files = os.listdir(data_path)
st.markdown("📁 **Files Found:**")
st.code(files)

# Helper: Load CSV safely
def safe_load_csv(file_path):
    try:
        if os.path.getsize(file_path) == 0:
            raise ValueError("File is empty")
        df = pd.read_csv(file_path)
        if df.empty or len(df.columns) == 0:
            raise ValueError("No columns to parse from file")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {e}")
        return pd.DataFrame()

# Helper: Load JSON safely
def safe_load_json(file_path):
    try:
        if os.path.getsize(file_path) == 0:
            raise ValueError("File is empty")
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {e}")
        return {}

# Load files
csv_files = [
    "TimeEntries.csv", "CheckDetails.csv", "KitchenTimings.csv", "AllItemsReport.csv",
    "PaymentDetails.csv", "CashEntries.csv", "OrderDetails.csv", "ItemSelectionDetails.csv",
    "ModifiersSelectionDetails.csv"
]

json_files = ["MenuExport.json", "MenuExportV2.json"]

xls_file = "AccountingReport.xls"

dfs = {file: safe_load_csv(os.path.join(data_path, file)) for file in csv_files}
jsons = {file: safe_load_json(os.path.join(data_path, file)) for file in json_files}

# Optional Excel loading
if os.path.exists(os.path.join(data_path, xls_file)):
    try:
        dfs["AccountingReport.xls"] = pd.read_excel(os.path.join(data_path, xls_file))
    except Exception as e:
        st.warning(f"⚠️ Could not load {xls_file}: {e}")

# Example visualization: Menu Item Summary
if not dfs["ItemSelectionDetails.csv"].empty:
    st.header("🍽️ Top Menu Items")
    item_summary = dfs["ItemSelectionDetails.csv"]['Item Name'].value_counts().reset_index()
    item_summary.columns = ['Item Name', 'Count']
    st.dataframe(item_summary)
else:
    st.info("ℹ️ No item-level data available for this location/date.")
