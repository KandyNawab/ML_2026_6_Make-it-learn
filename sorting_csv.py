import os
import pandas as pd

# ====== SET YOUR FOLDERS HERE ======
input_folder = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\ORG_DATA"
output_folder = r"G:\F\AU Assignments\AU SEM 6\ML\PROJECT\SORTED_DATA"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        df = pd.read_csv(input_path)

        df_sorted = df.sort_values(by=df.columns[0])

        df_sorted.to_csv(output_path, index=False)

        print(f"Sorted: {filename}")

print("All files processed successfully.")
