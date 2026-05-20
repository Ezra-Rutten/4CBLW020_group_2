import pandas as pd
from pathlib import Path
import geopandas as gpd
import glob
import os

base_path = Path("../data/raw")
all_dfs= []

for month_dir in base_path.iterdir():
    if month_dir.is_dir():
        for csv_file in month_dir.glob("*.csv"):
            df = pd.read_csv(csv_file)
            all_dfs.append(df)

df_london = pd.concat(all_dfs, ignore_index=True)
df_london.to_csv("../data/processed/london_all_data_uncleaned.csv", index=False)

print("Saved dataset with rows:", len(df_london))