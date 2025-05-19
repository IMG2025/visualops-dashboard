import os
import pandas as pd
import json

def load_all_data(date_path):
    data = {}

    for filename in os.listdir(date_path):
        file_path = os.path.join(date_path, filename)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
                key = os.path.splitext(filename)[0]  # Strip .csv
                data[key] = df
            elif filename.endswith(".json"):
                with open(file_path, 'r') as f:
                    key = os.path.splitext(filename)[0]  # Strip .json
                    data[key] = json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {file_path}: {e}")
            continue

    return data
