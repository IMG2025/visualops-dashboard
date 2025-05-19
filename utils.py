import os
import pandas as pd
import json

def load_all_data(base_dir):
    data = {}

    for location in os.listdir(base_dir):
        location_path = os.path.join(base_dir, location)
        if not os.path.isdir(location_path):
            continue

        data[location] = {}

        for date in os.listdir(location_path):
            date_path = os.path.join(location_path, date)
            if not os.path.isdir(date_path):
                continue

            data[location][date] = {}
            for filename in os.listdir(date_path):
                file_path = os.path.join(date_path, filename)
                try:
                    if filename.endswith(".csv"):
                        df = pd.read_csv(file_path)
                        data[location][date][filename] = df
                    elif filename.endswith(".json"):
                        with open(file_path) as f:
                            data[location][date][filename] = json.load(f)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue

    return data
