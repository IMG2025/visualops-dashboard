import os
import pandas as pd
import json

def load_all_data(location, date, base_dir="toast_exports"):
    """
    Load all files for a given location and date.
    Returns: dict of filename => DataFrame or JSON
    """
    data = {}
    folder_path = os.path.join(base_dir, location, date)

    if not os.path.isdir(folder_path):
        return {}

    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        key = os.path.splitext(file)[0]
        try:
            if file.endswith(".csv"):
                df = pd.read_csv(path)
                data[key] = df
            elif file.endswith(".json"):
                with open(path, "r") as f:
                    data[key] = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")
            continue

    return data
