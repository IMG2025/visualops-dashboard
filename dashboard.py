import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# === Selection Controls ===
location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date = st.selectbox("📅 Select Date", options=sorted([
    d for d in os.listdir(f"toast_exports/{location}") if os.path.isdir(f"toast_exports/{location}/{d}")
]))

data_path = f"toast_exports/{location}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

# === File Discovery ===
try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"❌ Failed to read directory: {e}")
    st.stop()

# === File Loaders ===

def load_csv(file):
    try:
        df = pd.read_csv(file)
        if df.empty or df.columns.size == 0:
            st.warning(f"⚠️ {os.path.basename(file)}: No columns to parse.")
            return None
        return df
    except Exception as e:
        st.warning(f"⚠️ {os.path.basename(file)}: {e}")
        return None

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ {os.path.basename(file)}: {e}")
        return None

def load_excel(file):
    try:
        return pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        st.warning(f"⚠️ {os.path.basename(file)}: {e}")
        return None

def find_column(df, candidates):
    for col in df.columns:
        if any(candidate.lower() in col.lower() for candidate in candidates):
            return col
    return None

# === Load Key Dataset: ItemSelectionDetails ===

item_file = os.path.join(data_path, "ItemSelectionDetails.csv")
if not os.path.exists(item_file):
    st.warning("⚠️ File not found: ItemSelectionDetails.csv")
else:
    all_items = load_csv(item_file)
    if all_items is not None:
        name_col = find_column(all_items, ["item name", "name", "item"])
        if name_col:
            item_summary = all_items[name_col].value_counts().reset_index()
            item_summary.columns = ["Item", "Count"]
            st.subheader("🍽️ Top Menu Items")
            st.dataframe(item_summary)
        else:
            st.error("🔴 'Item Name' column not found in ItemSelectionDetails.csv.")

# === Optional: Display logic for other files (only if needed) ===
# You can uncomment or extend this section later

# order_file = os.path.join(data_path, "OrderDetails.csv")
# orders = load_csv(order_file)
# if orders is not None:
#     st.subheader("🧾 Order Details")
#     st.dataframe(orders)

# === END ===
