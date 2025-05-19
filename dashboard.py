import streamlit as st
import pandas as pd
import os
import json
import glob

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# User selections
location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date_path = f"toast_exports/{location}"
if not os.path.exists(date_path):
    st.error(f"No data found for location {location}.")
    st.stop()

available_dates = sorted([d for d in os.listdir(date_path) if os.path.isdir(f"{date_path}/{d}")])
date = st.selectbox("📅 Select Date", options=available_dates)

data_path = f"{date_path}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

# Show file list
try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"❌ Failed to list files in directory: {e}")
    st.stop()

# Loaders
def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        if df.empty or len(df.columns) == 0:
            raise ValueError("No columns to parse from file")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def load_excel(filepath):
    try:
        return pd.read_excel(filepath, engine="openpyxl")
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def verify_columns(df, required, name):
    if df is None:
        return False
    missing = [col for col in required if col not in df.columns]
    if missing:
        for m in missing:
            st.error(f"🔴 Missing critical column '{m}' in {name}")
        return False
    return True

# --- Dashboard Sections ---

# Top Menu Items (ItemSelectionDetails.csv)
item_path = os.path.join(data_path, "ItemSelectionDetails.csv")
item_df = load_csv(item_path)
if verify_columns(item_df, ["Menu Item", "Qty", "Net Price"], "ItemSelectionDetails.csv"):
    top_items = item_df.groupby("Menu Item").agg({
        "Qty": "sum",
        "Net Price": "sum"
    }).reset_index().rename(columns={"Qty": "Quantity Sold", "Net Price": "Total Sales"})
    top_items = top_items.sort_values(by="Quantity Sold", ascending=False)
    st.subheader("🍽️ Top Menu Items")
    st.dataframe(top_items)

# Sales Summary (CheckDetails.csv)
check_path = os.path.join(data_path, "CheckDetails.csv")
check_df = load_csv(check_path)
if check_df is not None and all(col in check_df.columns for col in ["Total", "Tax", "Discount"]):
    st.subheader("💵 Sales Summary (from CheckDetails)")
    st.metric("Total Sales", f"${check_df['Total'].sum():,.2f}")
    st.metric("Total Tax", f"${check_df['Tax'].sum():,.2f}")
    st.metric("Total Discount", f"${check_df['Discount'].sum():,.2f}")
elif check_df is not None:
    st.warning("⚠️ Some expected columns are missing in CheckDetails.csv")

# Order Details Summary
order_path = os.path.join(data_path, "OrderDetails.csv")
order_df = load_csv(order_path)
if order_df is not None:
    if "Tender" not in order_df.columns:
        st.error("🔴 Missing critical column 'Tender' in OrderDetails.csv")
    else:
        tender_summary = order_df["Tender"].value_counts().reset_index()
        tender_summary.columns = ["Tender Type", "Count"]
        st.subheader("📦 Order Tenders Summary")
        st.dataframe(tender_summary)

# Labor Summary (TimeEntries.csv)
labor_path = os.path.join(data_path, "TimeEntries.csv")
labor_df = load_csv(labor_path)
if labor_df is not None and all(col in labor_df.columns for col in ["Job Title", "Payable Hours", "Total Pay"]):
    st.subheader("👥 Labor Summary")
    labor_summary = labor_df.groupby("Job Title").agg({
        "Payable Hours": "sum",
        "Total Pay": "sum"
    }).reset_index()
    st.dataframe(labor_summary)

# Accounting (AccountingReport.xls)
account_path = os.path.join(data_path, "AccountingReport.xls")
account_df = load_excel(account_path)
if account_df is not None:
    st.subheader("📒 Accounting Summary")
    st.dataframe(account_df)
