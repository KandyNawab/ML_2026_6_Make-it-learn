import pandas as pd
import os
import glob

# folder containing all csv files
folder_path = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\SORTED_DATA"

# get all csv files
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

rows = []

for file in csv_files:
    df = pd.read_csv(file)
    
    if not df.empty:
        first_row = df.iloc[0]
        rows.append(first_row)

# combine all rows
result = pd.DataFrame(rows)

# save new csv
save_path = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\all_first.csv"
result.to_csv(save_path, index=False)

print("✅ CSV created at:", save_path)