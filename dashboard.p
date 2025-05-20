
import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# === Selection ===
location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date = st.selectbox("📅 Select Date", options=sorted([
    d for d in os.listdir(f"toast_exports/{location}") if os.path.isdir(f"toast_exports/{location}/{d}")
]))

data_path = f"toast_exports/{location}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

# === File Loader ===
def load_csv_safe(path):
    try:
        df = pd.read_csv(path)
        if df.empty or df.columns.str.contains("Unnamed").all():
            st.warning(f"⚠️ {os.path.basename(path)} is malformed or empty.")
            return None
        return df
    except Exception as e:
        st.warning(f"⚠️ Failed to load {os.path.basename(path)}: {e}")
        return None

def load_excel_safe(path):
    try:
        df = pd.read_excel(path, engine="openpyxl")
        if df.empty:
            st.warning(f"⚠️ {os.path.basename(path)} is empty.")
            return None
        return df
    except Exception as e:
        st.warning(f"⚠️ Failed to load {os.path.basename(path)}: {e}")
        return None

def load_json_safe(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Failed to load {os.path.basename(path)}: {e}")
        return None

# === Dashboard Sections ===

st.subheader("🍽️ Item Selection Summary")
item_df = load_csv_safe(os.path.join(data_path, "ItemSelectionDetails.csv"))
if item_df is not None:
    if "Menu Item" in item_df.columns:
        top_items = item_df["Menu Item"].value_counts().reset_index()
        top_items.columns = ["Item", "Count"]
        st.dataframe(top_items)
    else:
        st.error("❌ 'Menu Item' column not found in ItemSelectionDetails.csv")

st.subheader("💵 Payments Summary")
payment_df = load_csv_safe(os.path.join(data_path, "PaymentDetails.csv"))
if payment_df is not None:
    if {"Amount", "Tip", "Dining Option"}.issubset(payment_df.columns):
        summary = payment_df.groupby("Dining Option")[["Amount", "Tip"]].sum().reset_index()
        st.dataframe(summary)
    else:
        st.error("❌ One or more required columns missing in PaymentDetails.csv")

st.subheader("🧾 Check Details")
check_df = load_csv_safe(os.path.join(data_path, "CheckDetails.csv"))
if check_df is not None:
    if {"Item Description", "Tender", "Total"}.issubset(check_df.columns):
        st.dataframe(check_df[["Item Description", "Tender", "Total"]].head(10))
    else:
        st.error("❌ Critical columns missing in CheckDetails.csv")

st.subheader("📦 Menu Overview")
menu_data = load_json_safe(os.path.join(data_path, "MenuExport.json"))
if menu_data:
    menu_names = [entry["name"] for entry in menu_data if entry.get("entityType") == "Menu"]
    st.markdown(f"**Menus Found:** {', '.join(menu_names)}")

st.subheader("🕒 Labor Hours Summary")
labor_df = load_csv_safe(os.path.join(data_path, "TimeEntries.csv"))
if labor_df is not None:
    if "Employee" in labor_df.columns and "Total Hours" in labor_df.columns:
        hours_summary = labor_df.groupby("Employee")["Total Hours"].sum().reset_index()
        st.dataframe(hours_summary)
    else:
        st.error("❌ 'Employee' or 'Total Hours' column missing in TimeEntries.csv")

st.markdown("---")
st.markdown("🌐 Live at: [cole-visualops-dashboard.streamlit.app](https://cole-visualops-dashboard.streamlit.app)")
