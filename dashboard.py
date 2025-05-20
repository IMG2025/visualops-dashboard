import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# --- SFTP Audit Log ---
audit_log_path = os.path.expanduser("~/visualops/sftp_audit.log")
if os.path.exists(audit_log_path):
    with open(audit_log_path, "r") as f:
        audit_lines = f.readlines()
    st.subheader("📋 SFTP Audit Summary")
    current_section = ""
    for line in audit_lines:
        line = line.strip()
        if "Location" in line:
            current_section = line
            st.markdown(f"### {line}")
        elif line.startswith("✅"):
            st.success(line)
        elif line.startswith("❌"):
            st.error(line)
        elif line.startswith("⚠️"):
            st.warning(line)

# --- User Selection ---
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

# --- File List ---
try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"❌ Failed to list files: {e}")
    st.stop()

# --- Utility Loaders ---
def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        if df.empty or len(df.columns) == 0:
            raise ValueError("Empty or malformed CSV")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

def load_excel(filepath):
    try:
        return pd.read_excel(filepath, engine="openpyxl")
    except Exception as e:
        st.warning(f"⚠️ Could not load {os.path.basename(filepath)}: {e}")
        return None

# --- Top Menu Items ---
item_df = load_csv(os.path.join(data_path, "ItemSelectionDetails.csv"))
if item_df is not None and all(col in item_df.columns for col in ["Menu Item", "Qty", "Net Price"]):
    top_items = item_df.groupby("Menu Item").agg({
        "Qty": "sum", "Net Price": "sum"
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
        "Payable Hours": "sum", "Total Pay": "sum"
    }).reset_index()
    st.dataframe(labor_summary)

# --- Accounting Summary ---
account_df = load_excel(os.path.join(data_path, "AccountingReport.xls"))
if account_df is not None:
    st.subheader("📒 Accounting Summary")
    st.dataframe(account_df)

# --- Payment Summary ---
payment_df = load_csv(os.path.join(data_path, "PaymentDetails.csv"))
if payment_df is not None and "Amount" in payment_df.columns:
    st.subheader("💳 Payment Summary")
    if "Payment Type" in payment_df.columns:
        pay_summary = payment_df.groupby("Payment Type")["Amount"].sum().reset_index()
        st.dataframe(pay_summary)
    else:
        st.dataframe(payment_df)

# --- Modifier Usage ---
mod_df = load_csv(os.path.join(data_path, "ModifiersSelectionDetails.csv"))
if mod_df is not None and "Modifier Name" in mod_df.columns:
    st.subheader("🧂 Modifier Usage")
    mod_summary = mod_df["Modifier Name"].value_counts().reset_index()
    mod_summary.columns = ["Modifier", "Count"]
    st.dataframe(mod_summary)

# --- Cash Log ---
cash_df = load_csv(os.path.join(data_path, "CashEntries.csv"))
if cash_df is not None and "Amount" in cash_df.columns:
    st.subheader("💵 Cash Entries")
    st.dataframe(cash_df)

# --- Kitchen Ticket Times ---
kitchen_df = load_csv(os.path.join(data_path, "KitchenTimings.csv"))
if kitchen_df is not None:
    st.subheader("⏱️ Kitchen Ticket Timings")
    st.dataframe(kitchen_df)

# --- All Items Report ---
items_report_df = load_csv(os.path.join(data_path, "AllItemsReport.csv"))
if items_report_df is not None:
    st.subheader("📦 All Items Report")
    st.dataframe(items_report_df)

# --- Menu Export Viewer ---
for menu_file in ["MenuExportV2.json", "MenuExport.json"]:
    menu_path = os.path.join(data_path, menu_file)
    if os.path.exists(menu_path):
        try:
            with open(menu_path, "r") as f:
                menu_data = json.load(f)
            st.subheader(f"📋 {menu_file} Viewer")
            st.json(menu_data)
        except Exception as e:
            st.warning(f"⚠️ Failed to load {menu_file}: {e}")
