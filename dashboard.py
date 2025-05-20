import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# --- Utility Loaders ---
def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        st.caption(f"{os.path.basename(filepath)} Columns: {df.columns.tolist()}")
        return df if not df.empty else None
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
        df = pd.read_excel(filepath, engine="openpyxl")
        st.caption(f"{os.path.basename(filepath)} Columns: {df.columns.tolist()}")
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
if item_df is not None and {"Menu Item", "Qty", "Net Price"}.issubset(item_df.columns):
    st.subheader("🍽️ Top Menu Items")
    top_items = item_df.groupby("Menu Item").agg({
        "Qty": "sum", "Net Price": "sum"
    }).reset_index().rename(columns={"Qty": "Quantity Sold", "Net Price": "Total Sales"})
    st.dataframe(top_items.sort_values("Quantity Sold", ascending=False))
else:
    st.info("No valid ItemSelectionDetails.csv found or missing required columns.")

# --- Sales Summary ---
check_df = load_csv(os.path.join(data_path, "CheckDetails.csv"))
if check_df is not None:
    st.subheader("💰 Sales Summary (from CheckDetails)")
    st.metric("Total Sales", f"${check_df.get('Total', pd.Series()).sum():,.2f}")
    st.metric("Total Tax", f"${check_df.get('Tax', pd.Series()).sum():,.2f}")
    st.metric("Total Discount", f"${check_df.get('Discount', pd.Series()).sum():,.2f}")

# --- Tender Breakdown ---
order_df = load_csv(os.path.join(data_path, "OrderDetails.csv"))
if order_df is not None:
    if "Tender" in order_df.columns:
        st.subheader("📦 Order Tenders Summary")
        tender_summary = order_df["Tender"].value_counts().reset_index()
        tender_summary.columns = ["Tender Type", "Count"]
        st.dataframe(tender_summary)
    else:
        st.warning("⚠️ 'Tender' column missing from OrderDetails.csv")

# --- Labor Summary ---
labor_df = load_csv(os.path.join(data_path, "TimeEntries.csv"))
if labor_df is not None and {"Job Title", "Payable Hours", "Total Pay"}.issubset(labor_df.columns):
    st.subheader("👥 Labor Summary")
    labor_summary = labor_df.groupby("Job Title").agg({
        "Payable Hours": "sum", "Total Pay": "sum"
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
    menu_items = []
    for group in menu_v1.get("menuGroups", []):
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
    st.json(menu_v2)
