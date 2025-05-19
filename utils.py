import os
import pandas as pd
import json

def load_all_data(base_dir="toast_exports"):
    """
    Scans the toast_exports directory and loads all valid data files into a nested dict:
    data[location][date][filename] = DataFrame or dict
    """
    data = {}

    for location in os.listdir(base_dir):
        loc_path = os.path.join(base_dir, location)
        if not os.path.isdir(loc_path):
            continue

        data[location] = {}
        for date in os.listdir(loc_path):
            date_path = os.path.join(loc_path, date)
            if not os.path.isdir(date_path):
                continue

            data[location][date] = {}
            for file in os.listdir(date_path):
                path = os.path.join(date_path, file)
                try:
                    if file.endswith(".csv"):
                        df = pd.read_csv(path)
                        key = os.path.splitext(file)[0]
                        data[location][date][key] = df
                    elif file.endswith(".json"):
                        with open(path, "r") as f:
                            content = json.load(f)
                            key = os.path.splitext(file)[0]
                            data[location][date][key] = content
                except Exception as e:
                    print(f"❌ Failed to load {file} for {location}/{date}: {e}")
                    continue

    return data
