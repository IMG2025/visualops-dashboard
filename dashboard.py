import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# === User Inputs ===
location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date = st.selectbox("📅 Select Date", options=sorted([
    d for d in os.listdir(f"toast_exports/{location}") if os.path.isdir(f"toast_exports/{location}/{d}")
]))

data_path = f"toast_exports/{location}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"Failed to list files: {e}")
    st.stop()

# === File Loaders ===
def load_csv(filename):
    try:
        df = pd.read_csv(os.path.join(data_path, filename))
        if df.empty or df.columns.size == 0:
            st.warning(f"⚠️ Empty or malformed: {filename}")
            return None
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {filename}: {e}")
        return None

# === Load Files ===
items_df = load_csv("ItemSelectionDetails.csv")
orders_df = load_csv("OrderDetails.csv")
checks_df = load_csv("CheckDetails.csv")

# === Top Items Summary ===
if items_df is not None:
    st.subheader("🍽️ Top Menu Items")

    if 'Menu Item' in items_df.columns:
        top_items = (
            items_df.groupby("Menu Item")
            .agg({"Qty": "sum", "Net Price": "sum"})
            .reset_index()
            .rename(columns={"Qty": "Quantity Sold", "Net Price": "Total Sales"})
            .sort_values("Total Sales", ascending=False)
        )
        st.dataframe(top_items)
    else:
        st.error("🛑 'Menu Item' column not found in ItemSelectionDetails.csv.")

# === Sales Summary ===
if checks_df is not None:
    st.subheader("💳 Sales Summary (from CheckDetails)")
    summary_cols = ['Amount', 'Tax', 'Tip', 'Gratuity', 'Total']
    if all(col in checks_df.columns for col in summary_cols):
        totals = checks_df[summary_cols].sum().to_frame("Total")
        st.dataframe(totals.T.style.format("${:,.2f}"))
    else:
        st.warning("Some expected columns are missing in CheckDetails.csv")

# === Order-Level Details ===
if orders_df is not None:
    st.subheader("📦 Order Details Summary")
    if 'Tender' in orders_df.columns:
        tenders = orders_df['Tender'].value_counts().reset_index()
        tenders.columns = ["Tender Type", "Count"]
        st.dataframe(tenders)
    else:
        st.warning("No 'Tender' column found in OrderDetails.csv")
