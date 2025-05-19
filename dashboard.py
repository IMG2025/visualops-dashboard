import streamlit as st
import os
import pandas as pd
import json

st.set_page_config(layout="wide")

st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# Select location
location = st.selectbox("📍 Select Location", sorted(os.listdir("toast_exports")))

# Select date
date_path = f"toast_exports/{location}"
dates = sorted(os.listdir(date_path))
date = st.selectbox("📅 Select Date", dates)

# Construct full data path
data_path = os.path.join("toast_exports", location, date)
st.markdown(f"**Data Path:** `{data_path}`")

# List all available files
if os.path.exists(data_path):
    files = os.listdir(data_path)
    files = [f for f in files if not f.startswith('.') and not f.startswith('._')]
    st.markdown("📂 **Files Found:**")
    st.code(files)
else:
    st.error("❌ Selected path does not exist.")
    st.stop()

# Helper to safely load files
def load_csv(file_name):
    file_path = os.path.join(data_path, file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            st.warning(f"⚠️ Could not load {file_name}: {e}")
    else:
        st.warning(f"❌ Failed to load {file_name}: File not found.")
    return pd.DataFrame()

def load_json(file_name):
    file_path = os.path.join(data_path, file_name)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ Could not load {file_name}: {e}")
    else:
        st.warning(f"❌ Failed to load {file_name}: File not found.")
    return {}

# Load critical CSVs
all_items = load_csv("AllItemsReport.csv")
item_selections = load_csv("ItemSelectionDetails.csv")
payments = load_csv("PaymentDetails.csv")
orders = load_csv("OrderDetails.csv")
modifiers = load_csv("ModifiersSelectionDetails.csv")
time_entries = load_csv("TimeEntries.csv")
check_details = load_csv("CheckDetails.csv")
kitchen = load_csv("KitchenTimings.csv")
cash_entries = load_csv("CashEntries.csv")

# Load JSON exports
menu_export = load_json("MenuExport.json")
menu_export_v2 = load_json("MenuExportV2.json")

# Optional XLS file
xls_path = os.path.join(data_path, "AccountingReport.xls")
if os.path.exists(xls_path):
    try:
        accounting = pd.read_excel(xls_path)
    except Exception as e:
        st.warning(f"⚠️ Could not load AccountingReport.xls: {e}")
else:
    accounting = pd.DataFrame()
    st.warning("❌ Failed to load AccountingReport.xls: File not found.")

# Display top items if possible
st.subheader("🍽️ Top Menu Items")
if not all_items.empty and 'Item Name' in all_items.columns:
    item_summary = all_items['Item Name'].value_counts().reset_index()
    item_summary.columns = ['Item Name', 'Count']
    st.dataframe(item_summary)
else:
    st.warning("⚠️ 'Item Name' column missing or AllItemsReport.csv is empty.")

# Add more dashboard sections here as needed...
