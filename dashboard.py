import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# --- Utility Loaders ---
def load_csv(filepath):
    try:
        if os.path.getsize(filepath) == 0:
            raise ValueError("File is empty")
        df = pd.read_csv(filepath)
        if df.empty or len(df.columns) == 0:
            raise ValueError("Empty or malformed CSV")
        st.markdown(f"`{os.path.basename(filepath)}` Columns: {list(df.columns)}")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def load_json(filepath):
    try:
        if os.path.getsize(filepath) == 0:
            raise ValueError("File is empty")
        with open(filepath, "r") as f:
            data = json.load(f)
        st.markdown(f"`{os.path.basename(filepath)}` ✅ JSON loaded.")
        return data
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def load_excel(filepath):
    try:
        if os.path.getsize(filepath) == 0:
            raise ValueError("File is empty")
        df = pd.read_excel(filepath, engine="openpyxl")
        st.markdown(f"`{os.path.basename(filepath)}` Columns: {list(df.columns)}")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

# --- Select Location and Date ---
locations = ["57130", "57138"]
location_id = st.selectbox("📍 Select Location", options=locations)
base_path = f"toast_exports/{location_id}"

if not os.path.exists(base_path):
    st.error(f"❌ No data found for location {location_id}.")
    st.stop()

available_dates = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])
if not available_dates:
    st.error("❌ No dates found for selected location.")
    st.stop()

selected_date = st.selectbox("📅 Select Date", options=available_dates)
data_path = f"{base_path}/{selected_date}"
st.markdown(f"**Data Path:** `{data_path}`")

try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"❌ Failed to list files: {e}")
    st.stop()

# --- Top Menu Items ---
item_df = load_csv(os.path.join(data_path, "ItemSelectionDetails.csv"))
if item_df is not None and all(col in item_df.columns for col in ["Menu Item", "Qty", "Net Price"]):
    top_items = item_df.groupby("Menu Item").agg({
        "Qty": "sum",
        "Net Price": "sum"
    }).reset_index().rename(columns={"Qty": "Quantity Sold", "Net Price": "Total Sales"})
    top_items = top_items.sort_values("Quantity Sold", ascending=False)
    st.subheader("🍽️ Top Menu Items")
    st.dataframe(top_items)

# --- Sales Summary ---
check_df = load_csv(os.path.join(data_path, "CheckDetails.csv"))
if check_df is not None:
    st.subheader("💰 Sales Summary (from CheckDetails)")
    st.metric("Total Sales", f"${check_df['Total'].sum():,.2f}" if "Total" in check_df.columns else "N/A")
    st.metric("Total Tax", f"${check_df['Tax'].sum():,.2f}" if "Tax" in check_df.columns else "N/A")
    st.metric("Total Discount", f"${check_df['Discount'].sum():,.2f}" if "Discount" in check_df.columns else "N/A")

# --- Tender Breakdown ---
order_df = load_csv(os.path.join(data_path, "OrderDetails.csv"))
if order_df is not None:
    if "Tender" not in order_df.columns:
        st.error("🔴 Missing critical column 'Tender' in OrderDetails.csv")
    else:
        tender_summary = order_df["Tender"].value_counts().reset_index()
        tender_summary.columns = ["Tender Type", "Count"]
        st.subheader("📦 Order Tenders Summary")
        st.dataframe(tender_summary)

# --- Labor Summary ---
labor_df = load_csv(os.path.join(data_path, "TimeEntries.csv"))
if labor_df is not None and all(col in labor_df.columns for col in ["Job Title", "Payable Hours", "Total Pay"]):
    st.subheader("👥 Labor Summary")
    labor_summary = labor_df.groupby("Job Title").agg({
        "Payable Hours": "sum",
        "Total Pay": "sum"
    }).reset_index()
    st.dataframe(labor_summary)

# --- Accounting Summary ---
account_df = load_excel(os.path.join(data_path, "AccountingReport.xls"))
if account_df is not None:
    st.subheader("📒 Accounting Summary")
    st.dataframe(account_df)

# --- Modifiers Summary ---
mod_df = load_csv(os.path.join(data_path, "ModifiersSelectionDetails.csv"))
if mod_df is not None and "Modifier Name" in mod_df.columns:
    st.subheader("🧩 Top Modifiers")
    modifier_summary = mod_df["Modifier Name"].value_counts().reset_index()
    modifier_summary.columns = ["Modifier", "Count"]
    st.dataframe(modifier_summary)

# --- All Items Summary ---
all_items_df = load_csv(os.path.join(data_path, "AllItemsReport.csv"))
if all_items_df is not None:
    st.subheader("📦 All Items Report")
    st.dataframe(all_items_df)

# --- Kitchen Timings ---
kitchen_df = load_csv(os.path.join(data_path, "KitchenTimings.csv"))
if kitchen_df is not None:
    st.subheader("⏱️ Kitchen Timing Metrics")
    st.dataframe(kitchen_df)

# --- Menu Export JSON (v1) ---
menu_v1 = load_json(os.path.join(data_path, "MenuExport.json"))
if menu_v1 is not None:
    st.subheader("📋 Menu Export (v1)")
    if "menuGroups" in menu_v1:
        menu_items = []
        for group in menu_v1["menuGroups"]:
            for item in group.get("menuItems", []):
                menu_items.append({
                    "Group": group.get("name"),
                    "Item": item.get("name"),
                    "Price": item.get("basePrice")
                })
        if menu_items:
            st.dataframe(pd.DataFrame(menu_items))

# --- Menu Export JSON (v2) ---
menu_v2 = load_json(os.path.join(data_path, "MenuExportV2.json"))
if menu_v2 is not None:
    st.subheader("📋 Menu Export (v2)")
    if isinstance(menu_v2, dict):
        keys = list(menu_v2.keys())
        st.markdown(f"Top-level keys: `{keys}`")
        st.json(menu_v2)
