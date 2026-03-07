import pandas as pd
import matplotlib.pyplot as plt
import os

data_folder = r"Add the path name here"      # folder with csv files
output_folder = "plots"   # Output folder

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(data_folder):
    if file.endswith(".csv"):

        filepath = os.path.join(data_folder, file)
        df = pd.read_csv(filepath)

        frame = df["Frame"]                           # This will be our x-axis 
        smoothed_vel = df["Smoothed_vel(kmph)"]       
        org_vel = df["Org_vel(kmph)"]                 # These  will the y axis

        org_class = df["Org_cls"].iloc[0]

        base_name = file.replace(".csv", "")

        # Smoothed velocity plot
        plt.figure(figsize=(18,6))
        plt.plot(frame, smoothed_vel, label=f"Smoothed_vel | Class: {org_class}")
        plt.xlabel("Frame")
        plt.ylabel("Velocity (kmph)")
        plt.title(f"{base_name} - Smoothed Velocity")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_folder, base_name + "_smoothed.png"))
        plt.close()

        # Original velocity plot
        plt.figure(figsize=(18,6))
        plt.plot(frame, org_vel, label=f"Org_vel | Class: {org_class}")
        plt.xlabel("Frame")
        plt.ylabel("Velocity (kmph)")
        plt.title(f"{base_name} - Original Velocity")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_folder, base_name + "_original.png"))
        plt.close()

        # Combined plot
        plt.figure(figsize=(18,6))
        plt.plot(frame, org_vel, label="Original Velocity")
        plt.plot(frame, smoothed_vel, label="Smoothed Velocity")
        plt.xlabel("Frame")
        plt.ylabel("Velocity (kmph)")
        plt.title(f"{base_name} | Class: {org_class}")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_folder, base_name + "_combined.png"))
        plt.close()

print("All plots generated successfully!")