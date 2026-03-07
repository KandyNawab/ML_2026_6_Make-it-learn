import pandas as pd
import glob
import os

# folder containing 690 csv files
folder_path = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\SORTED_DATA"

# get all csv files
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

rows = []

for file in csv_files:
    df = pd.read_csv(file)

    # select rows where frame_no = 1
    filtered = df[df["Frame"] == 1]

    rows.append(filtered)

# combine all rows
result = pd.concat(rows, ignore_index=True)

# save output
save_path = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\frame1_all.csv"
result.to_csv(save_path, index=False)

print("✅ CSV created:", save_path)