import os
import pandas as pd

# Set the directory where the CSV files are stored
input_dir = "./"  # Change this to your directory path if needed

# Collect all CSV files with names like 1.csv, 2.csv, ...
csv_files = []
for file_name in os.listdir(input_dir):
    if file_name.endswith(".csv") and file_name[:-4].isdigit():
        csv_files.append(file_name)

# Sort by numeric filename
csv_files = sorted(csv_files, key=lambda x: int(x[:-4]))

# Combine all CSVs
combined_df = pd.concat([pd.read_csv(os.path.join(input_dir, f)) for f in csv_files], ignore_index=True)

# Save to a new file
combined_df.to_csv("combined.csv", index=False)

print(f"Combined {len(csv_files)} files into 'combined.csv'")
