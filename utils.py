# utils.py
import os
import pandas as pd
import json

def load_all_data(base_dir):
    data = {}

    if not os.path.isdir(base_dir):
        return data

    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
                key = os.path.splitext(filename)[0]  # Strip .csv
                data[key] = df
            elif filename.endswith(".json"):
                with open(file_path) as f:
                    key = os.path.splitext(filename)[0]
                    data[key] = json.load(f)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            continue

    return data
