from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

# --- Load environment variables ---
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

NEON_DB_CONFIG = {
    "dbname": os.environ.get("NEON_DB_NAME"),
    "user": os.environ.get("NEON_DB_USER"),
    "password": os.environ.get("NEON_DB_PASSWORD"),
    "host": os.environ.get("NEON_DB_HOST"),
    "port": os.environ.get("NEON_DB_PORT", "5432")
}

EXPORT_ROOT = "toast_exports"
TARGET_DATE = "20250516"
SCHEMA = "visualops_schema"

# --- DB CONNECTION ---
def get_conn():
    print(f"🔌 Connecting to {NEON_DB_CONFIG['host']}:{NEON_DB_CONFIG['port']}...")
    return psycopg2.connect(**NEON_DB_CONFIG)

# --- HELPERS ---
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return None

def insert_dataframe(conn, df, table):
    if df is None or df.empty:
        print(f"[SKIP] No data for table: {table}")
        return

    columns = [f'"{col}"' for col in df.columns]
    values = df.values.tolist()
    query = f'INSERT INTO {SCHEMA}.{table} ({",".join(columns)}) VALUES %s'

    with conn.cursor() as cur:
        try:
            execute_values(cur, query, values)
            print(f"[OK] Inserted {len(values)} rows into {table}")
        except Exception as e:
            print(f"[FAIL] Insert into {table}: {e}")

# --- MAIN ---
def run_ingestion():
    conn = get_conn()
    locations = [loc for loc in os.listdir(EXPORT_ROOT) if os.path.isdir(os.path.join(EXPORT_ROOT, loc))]

    for location in locations:
        base_path = os.path.join(EXPORT_ROOT, location, TARGET_DATE)
        print(f"📂 Processing: {base_path}")

        files_to_tables = {
            "ItemSelectionDetails.csv": "item_selection_details",
            "ModifiersSelectionDetails.csv": "modifiers_selection_details",
            "CheckDetails.csv": "check_details",
            "OrderDetails.csv": "order_details",
            "PaymentDetails.csv": "payment_details",
            "AllItemsReport.csv": "all_items_report",
            "KitchenTimings.csv": "kitchen_timings",
            "CashEntries.csv": "cash_entries",
            "TimeEntries.csv": "time_entries"
        }

        for filename, table in files_to_tables.items():
            full_path = os.path.join(base_path, filename)
            if not os.path.isfile(full_path):
                print(f"[WARN] Missing: {full_path}")
                continue

            df = load_csv(full_path)
            if df is not None:
                df["location"] = location
                df["export_date"] = TARGET_DATE
                insert_dataframe(conn, df, table)

    conn.commit()
    conn.close()
    print("✅ Ingestion complete.")

# --- EXECUTE ---
if __name__ == "__main__":
    try:
        with get_conn() as test_conn:
            with test_conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print("✅ DB connection OK")
    except Exception as e:
        print(f"❌ DB connection failed: {e}")
        exit(1)

    run_ingestion()
