import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# --- CONFIGURATION ---
NEON_DB_CONFIG = {{
    "host": "YOUR_NEON_HOST",
    "port": 5432,
    "user": "YOUR_NEON_USER",
    "password": "YOUR_NEON_PASSWORD",
    "dbname": "YOUR_NEON_DBNAME",
}}

EXPORT_ROOT = "toast_exports"
TARGET_DATE = "20250516"
SCHEMA = "visualops_schema"

# --- DB CONNECTION ---
def get_conn():
    return psycopg2.connect(**NEON_DB_CONFIG)

# --- HELPERS ---
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Failed to load {{file_path}}: {{e}}")
        return None

def insert_dataframe(conn, df, table):
    if df is None or df.empty:
        print(f"[SKIP] No data for table: {{table}}")
        return

    columns = list(df.columns)
    values = df.values.tolist()
    placeholders = "(" + ",".join(["%s"] * len(columns)) + ")"
    query = f'INSERT INTO {{SCHEMA}}.{{table}} ({{",".join(columns)}}) VALUES %s'

    with conn.cursor() as cur:
        try:
            execute_values(cur, query, values)
            print(f"[OK] Inserted into {{table}} ({{len(values)}} rows)")
        except Exception as e:
            print(f"[ERR] Failed to insert into {{table}}: {{e}}")

# --- MAIN ---
def run_ingestion():
    conn = get_conn()
    locations = [loc for loc in os.listdir(EXPORT_ROOT) if os.path.isdir(os.path.join(EXPORT_ROOT, loc))]

    for location in locations:
        base_path = os.path.join(EXPORT_ROOT, location, TARGET_DATE)
        print(f"📂 Processing: {{base_path}}")

        files_to_tables = {{
            "ItemSelectionDetails.csv": "item_selection_details",
            "ModifiersSelectionDetails.csv": "modifiers_selection_details",
            "CheckDetails.csv": "check_details",
            "OrderDetails.csv": "order_details",
            "PaymentDetails.csv": "payment_details",
            "AllItemsReport.csv": "all_items_report",
            "KitchenTimings.csv": "kitchen_timings",
            "CashEntries.csv": "cash_entries",
            "TimeEntries.csv": "time_entries"
        }}

        for filename, table in files_to_tables.items():
            full_path = os.path.join(base_path, filename)
            if not os.path.isfile(full_path):
                print(f"[WARN] Missing: {{full_path}}")
                continue

            df = load_csv(full_path)
            df["location"] = location  # Add location tag
            df["export_date"] = TARGET_DATE  # Add export date tag
            insert_dataframe(conn, df, table)

    conn.commit()
    conn.close()
    print("✅ Ingestion complete.")

if __name__ == "__main__":
    run_ingestion()
