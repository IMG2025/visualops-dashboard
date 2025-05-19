import os
import pandas as pd
import json

def load_all_data(date_path):
    """
    Loads all supported files from a given location/date path.
    Returns a flat dictionary like: {'AllItemsReport': DataFrame, 'MenuExport': dict}
    """
    data = {}
    if not os.path.exists(date_path):
        return data

    for file in os.listdir(date_path):
        file_path = os.path.join(date_path, file)
        key = os.path.splitext(file)[0]

        try:
            if file.endswith(".csv"):
                data[key] = pd.read_csv(file_path)
            elif file.endswith(".json"):
                with open(file_path) as f:
                    data[key] = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            continue

    return data
