import os
import pandas as pd
from collections import defaultdict

def map_columns_to_files():
    # Store the column-to-file mapping
    column_file_mapping = defaultdict(list)

    # Find all CSV files
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                
                # Get column names
                df = pd.read_csv(file_path, nrows=0)

                # Map each column to the file it belongs to
                for column in df.columns:
                    column_file_mapping[column].append(file)

    return column_file_mapping

if __name__ == "__main__":
    column_file_mapping = map_columns_to_files()
    for column, files in column_file_mapping.items():
        print(f"Column '{column}' is in files: {files}")
