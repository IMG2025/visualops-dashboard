from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import requests
from io import StringIO

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

SCHEMA = "visualops_schema"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/IMG2025/visualops-dashboard/main/toast_exports"
TARGET_DATES = ["20250516"]  # 👈 You can make this dynamic later
LOCATIONS = ["57130", "57138"]

# --- DB CONNECTION ---
def get_conn():
    return psycopg2.connect(**NEON_DB_CONFIG)

# --- LOAD FROM GITHUB ---
def load_csv_remote(location, date, filename):
    url = f"{GITHUB_RAW_BASE}/{location}/{date}/{filename}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"[GET] {url}")
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        print(f"[WARN] Could not load {url}: {e}")
        return None

# --- DB INSERT ---
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
            print(f"[ERR] Failed to insert into {table}: {e}")

# --- MAIN ---
def run_ingestion():
    conn = get_conn()

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

    for location in LOCATIONS:
        for date in TARGET_DATES:
            print(f"\n📂 Location {location} | Date {date}")
            for filename, table in files_to_tables.items():
                df = load_csv_remote(location, date, filename)
                if df is not None:
                    df["location"] = location
                    df["export_date"] = date
                    insert_dataframe(conn, df, table)

    conn.commit()
    conn.close()
    print("\n✅ Ingestion complete.")

# --- ENTRYPOINT ---
if __name__ == "__main__":
    try:
        with get_conn() as test_conn:
            with test_conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print("✅ Connected to Neon")
    except Exception as e:
        print(f"❌ Neon connection failed: {e}")
        exit(1)

    run_ingestion()
