import pandas as pd
from pathlib import Path

base_path = Path("../data/raw")

components = ["metropolitan", "merseyside", "west-midlands", "west-yorkshire", "south-yorkshire"]

Path("../data/processed").mkdir(parents=True, exist_ok=True)

component_dfs = {}

for component in components:
    all_dfs = []
    for month_dir in base_path.iterdir():
        if month_dir.is_dir():
            for csv_file in month_dir.glob(f"*{component}-street.csv"):
                df = pd.read_csv(csv_file)
                all_dfs.append(df)

    if all_dfs:
        df_component = pd.concat(all_dfs, ignore_index=True)
        component_dfs[component] = df_component
        df_component.to_csv(f"../data/processed/{component}_all_data_uncleaned.csv", index=False)
        print(f"Saved {component} with rows:", len(df_component))
    else:
        print(f"No files found for {component}")

if component_dfs:
    df_all = pd.concat(component_dfs.values(), ignore_index=True)
    df_all.to_csv("../data/processed/all_data_uncleaned.csv", index=False)
    print("Saved combined dataset with rows:", len(df_all))