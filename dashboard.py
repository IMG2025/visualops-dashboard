import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")

st.title("📊 VisualOps: Multi-Location Toast Dashboard")

location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date = st.selectbox("📅 Select Date", options=sorted([
    d for d in os.listdir(f"toast_exports/{location}") if os.path.isdir(f"toast_exports/{location}/{d}")
]))

data_path = f"toast_exports/{location}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

# List files
try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"Failed to read directory: {e}")
    st.stop()

# === Helper Functions ===

def load_csv(file):
    try:
        df = pd.read_csv(file)
        if df.empty or len(df.columns) == 0:
            st.warning(f"⚠️ Could not load {os.path.basename(file)}: No columns to parse from file")
            return None
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file)}: {e}")
        return None

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file)}: {e}")
        return None

def load_excel(file):
    try:
        return pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(file)}: {e}")
        return None

def find_column(df, candidates):
    for col in df.columns:
        if any(c.lower() in col.lower() for c in candidates):
            return col
    return None

# === Load Key Files ===

item_file = os.path.join(data_path, "ItemSelectionDetails.csv")
all_items = load_csv(item_file)

if all_items is not None:
    col_name = find_column(all_items, ["item name", "name", "item"])
    if col_name:
        item_summary = all_items[col_name].value_counts().reset_index()
        item_summary.columns = ["Item", "Count"]
        st.subheader("🍽️ Top Menu Items")
        st.dataframe(item_summary)
    else:
        st.error("🔴 'Item Name'-like column not found in ItemSelectionDetails.csv.")

# Load remaining files as needed...
# You can add more st.dataframe() or summaries here if needed
