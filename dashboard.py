import streamlit as st
import pandas as pd
import os
import json
import warnings

st.set_page_config(page_title="VisualOps Dashboard", layout="wide")
st.title("📊 VisualOps: Multi-Location Toast Dashboard")

# === UI Selections ===
location = st.selectbox("📍 Select Location", options=["57130", "57138"])
date = st.selectbox("📅 Select Date", options=sorted([
    d for d in os.listdir(f"toast_exports/{location}") if os.path.isdir(f"toast_exports/{location}/{d}")
]))

data_path = f"toast_exports/{location}/{date}"
st.markdown(f"**Data Path:** `{data_path}`")

# === File List ===
try:
    files_found = os.listdir(data_path)
    st.markdown("📁 **Files Found:**")
    st.code(files_found)
except Exception as e:
    st.error(f"Failed to read directory: {e}")
    st.stop()

# === Loaders ===
def load_csv(file, critical_cols=None):
    try:
        df = pd.read_csv(file)
        if df.empty or len(df.columns) == 0:
            st.warning(f"⚠️ Could not load {os.path.basename(file)}: No columns to parse from file")
            return None
        if critical_cols:
            for col in critical_cols:
                if not any(col.lower() == c.lower() for c in df.columns):
                    st.error(f"🔴 Missing critical column '{col}' in {os.path.basename(file)}")
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

def get_col(df, name):
    """Fuzzy column match"""
    for col in df.columns:
        if name.lower() in col.lower():
            return col
    return None

# === Top Menu Items ===
item_path = os.path.join(data_path, "ItemSelectionDetails.csv")
item_df = load_csv(item_path, ["Menu Item", "Qty", "Net Price"])
if item_df is not None:
    col_item = get_col(item_df, "Menu Item")
    col_qty = get_col(item_df, "Qty")
    col_net = get_col(item_df, "Net Price")
    if col_item and col_qty and col_net:
        menu_summary = (
            item_df.groupby(col_item)
            .agg(**{
                "Quantity Sold": (col_qty, "sum"),
                "Total Sales": (col_net, "sum")
            })
            .sort_values("Total Sales", ascending=False)
            .reset_index()
        )
        st.subheader("🍽️ Top Menu Items")
        st.dataframe(menu_summary)
    else:
        st.error("Missing one or more critical columns in ItemSelectionDetails.csv.")

# === Sales Summary (CheckDetails) ===
check_path = os.path.join(data_path, "CheckDetails.csv")
check_df = load_csv(check_path, ["Total", "Tax", "Discount"])
if check_df is not None:
    col_total = get_col(check_df, "Total")
    col_tax = get_col(check_df, "Tax")
    col_discount = get_col(check_df, "Discount")
    if col_total and col_tax and col_discount:
        st.subheader("🧾 Sales Summary (from CheckDetails)")
        st.metric("Total Sales", f"${check_df[col_total].sum():,.2f}")
        st.metric("Total Tax", f"${check_df[col_tax].sum():,.2f}")
        st.metric("Total Discount", f"${check_df[col_discount].sum():,.2f}")
    else:
        st.warning("Some expected columns are missing in CheckDetails.csv")

# === Order Details ===
order_path = os.path.join(data_path, "OrderDetails.csv")
order_df = load_csv(order_path, ["Tender"])
if order_df is not None:
    tender_col = get_col(order_df, "Tender")
    if tender_col:
        st.subheader("📦 Order Details Summary")
        tender_summary = order_df[tender_col].value_counts().reset_index()
        tender_summary.columns = ["Tender", "Count"]
        st.dataframe(tender_summary)
    else:
        st.warning("No 'Tender' column found in OrderDetails.csv")

# === Payments Breakdown ===
pay_path = os.path.join(data_path, "PaymentDetails.csv")
pay_df = load_csv(pay_path, ["Type", "Amount", "Tip", "Gratuity"])
if pay_df is not None:
    col_type = get_col(pay_df, "Type")
    col_amt = get_col(pay_df, "Amount")
    col_tip = get_col(pay_df, "Tip")
    col_grat = get_col(pay_df, "Gratuity")
    if col_type and col_amt:
        st.subheader("💳 Payment Breakdown")
        payment_summary = (
            pay_df.groupby(col_type)
            .agg({
                col_amt: "sum",
                col_tip: "sum" if col_tip else lambda x: 0,
                col_grat: "sum" if col_grat else lambda x: 0
            })
            .rename(columns={
                col_amt: "Amount",
                col_tip: "Tips",
                col_grat: "Gratuity"
            })
            .reset_index()
        )
        st.dataframe(payment_summary)

# === Cash Activity ===
cash_path = os.path.join(data_path, "CashEntries.csv")
cash_df = load_csv(cash_path, ["Action", "Amount"])
if cash_df is not None:
    action_col = get_col(cash_df, "Action")
    amt_col = get_col(cash_df, "Amount")
    if action_col and amt_col:
        st.subheader("💵 Cash Management Activity")
        cash_summary = cash_df.groupby(action_col)[amt_col].sum().reset_index()
        cash_summary.columns = ["Action", "Total Amount"]
        st.dataframe(cash_summary)

# === Labor Summary ===
labor_path = os.path.join(data_path, "TimeEntries.csv")
labor_df = load_csv(labor_path, ["Job Title", "Payable Hours", "Total Pay"])
if labor_df is not None:
    title_col = get_col(labor_df, "Job Title")
    hrs_col = get_col(labor_df, "Payable Hours")
    pay_col = get_col(labor_df, "Total Pay")
    if title_col and hrs_col and pay_col:
        st.subheader("👥 Labor Summary")
        labor_summary = (
            labor_df.groupby(title_col)
            .agg({
                hrs_col: "sum",
                pay_col: "sum"
            })
            .reset_index()
        )
        st.dataframe(labor_summary)

# === Accounting Summary ===
acct_path = os.path.join(data_path, "AccountingReport.xls")
acct_df = load_excel(acct_path)
if acct_df is not None:
    gl_col = get_col(acct_df, "GL Account")
    amt_col = get_col(acct_df, "Amount")
    if gl_col and amt_col:
        st.subheader("📘 Accounting Summary")
        accounting_summary = acct_df.groupby(gl_col)[amt_col].sum().reset_index()
        accounting_summary.columns = ["GL Code", "Amount"]
        st.dataframe(accounting_summary)
