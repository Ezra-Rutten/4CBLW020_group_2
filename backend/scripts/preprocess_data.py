import pandas as pd
from pathlib import Path


def preprocess_data(
    raw_path: str = "../data/raw",
    output_path: str = "../data/processed"
):
    base_path = Path(raw_path)
    components = ["metropolitan", "merseyside", "west-midlands", "west-yorkshire", "south-yorkshire"]

    Path(output_path).mkdir(parents=True, exist_ok=True)

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
            df_component["Borough"] = df_component["LSOA name"].str.replace(r'\s\d.*$', '', regex=True)
            component_dfs[component] = df_component
            df_component.to_csv(f"{output_path}/{component}_all_data_uncleaned.csv", index=False)
            print(f"Saved {component} with rows:", len(df_component))
        else:
            print(f"No files found for {component}")

    if component_dfs:
        df_all = pd.concat(component_dfs.values(), ignore_index=True)
        df_all.to_csv(f"{output_path}/all_data_uncleaned.csv", index=False)
        print("Saved combined dataset with rows:", len(df_all))


if __name__ == "__main__":
    preprocess_data()