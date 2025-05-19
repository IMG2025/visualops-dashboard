import streamlit as st
import os
import pandas as pd
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")

# Helper functions
def load_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        if df.empty or df.columns.size == 0:
            st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: No columns to parse from file")
            return None
        return df
    except pd.errors.EmptyDataError:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: File is empty.")
    except pd.errors.ParserError as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {str(e)}")
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {str(e)}")
    return None

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty file")
            return json.loads(content)
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {str(e)}")
        return None

def load_excel_file(file_path):
    try:
        return pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file_path)}: {str(e)}")
        return None

# UI
st.title("📊 VisualOps: Multi-Location Toast Dashboard")
location = st.selectbox("📍 Select Location", sorted([d for d in os.listdir("toast_exports") if os.path.isdir(os.path.join("toast_exports", d))]))
dates = sorted(os.listdir(os.path.join("toast_exports", location)))
date = st.selectbox("📅 Select Date", dates)

data_path = os.path.join("toast_exports", location, date)
st.markdown(f"**Data Path:** `{data_path}`")

# Display available files
try:
    files = os.listdir(data_path)
    st.markdown(f"📁 **Files Found:** `{files}`")
except FileNotFoundError:
    st.error("❌ Selected location/date combination not found.")
    st.stop()

# Load each file
csv_files = [
    "TimeEntries.csv", "CheckDetails.csv", "KitchenTimings.csv", "AllItemsReport.csv",
    "PaymentDetails.csv", "CashEntries.csv", "OrderDetails.csv", "ItemSelectionDetails.csv",
    "ModifiersSelectionDetails.csv"
]
json_files = ["MenuExport.json", "MenuExportV2.json"]
xls_file = "AccountingReport.xls"

data_frames = {}

for file in csv_files:
    fp = os.path.join(data_path, file)
    if os.path.exists(fp):
        df = load_csv_file(fp)
        if df is not None:
            data_frames[file] = df
    else:
        st.warning(f"⚠️ File not found: {file}")

for file in json_files:
    fp = os.path.join(data_path, file)
    if os.path.exists(fp):
        data = load_json_file(fp)
        if data is not None:
            data_frames[file] = data
    else:
        st.warning(f"⚠️ File not found: {file}")

xls_fp = os.path.join(data_path, xls_file)
if os.path.exists(xls_fp):
    df = load_excel_file(xls_fp)
    if df is not None:
        data_frames[xls_file] = df
else:
    st.warning(f"⚠️ File not found: {xls_file}")

# Example Visualization
if "ItemSelectionDetails.csv" in data_frames:
    try:
        all_items = data_frames["ItemSelectionDetails.csv"]
        if "Item Name" in all_items.columns:
            item_summary = all_items["Item Name"].value_counts().reset_index()
            item_summary.columns = ["Item", "Count"]
            st.subheader("🍽️ Top Menu Items")
            st.dataframe(item_summary)
        else:
            st.warning("🛑 'Item Name' column not found in ItemSelectionDetails.csv.")
    except Exception as e:
        st.error(f"❌ Error while processing item summary: {str(e)}")
else:
    st.info("ℹ️ No ItemSelectionDetails data available for summary.")
