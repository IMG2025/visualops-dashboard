import os
import pandas as pd
import psycopg2
import requests
from io import StringIO
from datetime import datetime

NEON_DB_CONFIG = {
    "host": os.getenv("NEON_DB_HOST"),
    "port": os.getenv("NEON_DB_PORT", 5432),
    "dbname": os.getenv("NEON_DB_NAME"),
    "user": os.getenv("NEON_DB_USER"),
    "password": os.getenv("NEON_DB_PASSWORD"),
}

BASE_URL = "https://raw.githubusercontent.com/IMG2025/visualops-dashboard/main/toast_exports"

LOCATIONS = ["57130", "57138"]
DATE = datetime.now().strftime("%Y%m%d")

TABLES = [
    "ItemSelectionDetails",
    "ModifiersSelectionDetails",
    "CheckDetails",
    "OrderDetails",
    "PaymentDetails",
    "AllItemsReport",
    "KitchenTimings",
    "CashEntries",
    "TimeEntries",
]

SCHEMA = "visualops_schema"

def fetch_csv(location_id, date, table_name):
    url = f"{BASE_URL}/{location_id}/{date}/{table_name}.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        if df.empty:
            print(f"[WARN] Empty CSV: {table_name} for Location {location_id}")
            return None
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        print(f"[WARN] Could not load {url}: {e}")
        return None

def insert_into_neon(df, table_name, conn):
    cursor = conn.cursor()
    try:
        columns = list(df.columns)
        col_str = ', '.join(f'"{c}"' for c in columns)
        val_template = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO {SCHEMA}.{table_name.lower()} ({col_str}) VALUES ({val_template})'
        
        for _, row in df.iterrows():
            try:
                cursor.execute(insert_query, tuple(row))
            except Exception as e:
                conn.rollback()
                print(f"[ERR] Failed to insert row into {table_name}: {e}")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERR] Failed to insert into {table_name}: {e}")
    finally:
        cursor.close()

def main():
    print("✅ Connected to Neon\n")
    conn = psycopg2.connect(**NEON_DB_CONFIG)

    for loc in LOCATIONS:
        print(f"\n📂 Location {loc} | Date {DATE}")
        for table in TABLES:
            df = fetch_csv(loc, DATE, table)
            if df is not None:
                insert_into_neon(df, table, conn)

    conn.close()
    print("\n✅ Ingestion complete.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Neon connection failed: {e}")