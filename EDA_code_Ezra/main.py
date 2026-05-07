import pandas as pd
import json
import matplotlib.pyplot as plt
from crime_weight import crime_weights

# Cleaning dataset
df_london = pd.read_csv("EDA_code_Ezra/london_all_data_uncleaned.csv")

missing_attributes = (df_london.isna().sum().to_frame(name="missing_count")).copy()
missing_attributes["missing_percent"] = (missing_attributes["missing_count"] / len(df_london)) * 100
df_london = df_london.drop(columns=["Context"])
df_london["crime_weight"] = df_london["Crime type"].map(crime_weights)
df_london["has_missing"] = df_london.isna().any(axis=1)

# Analysis on df_london
crimes_per_month = (df_london.groupby("Month").size().reset_index(name="crime_count"))
type_of_crimes = (df_london.groupby("Crime type").size().reset_index(name="crime_count"))

missing_data_month = (df_london.groupby("Month")["has_missing"].sum().reset_index(name="missing_rows"))
missing_data_crime = (df_london.groupby("Crime type")["has_missing"].sum().reset_index(name="missing_rows"))

missing_data_month_procent = (missing_data_month.merge(crimes_per_month, on="Month"))
missing_data_month_procent["missing_percent"] = (missing_data_month_procent["missing_rows"] / missing_data_month_procent["crime_count"] * 100)

missing_data_crime_type_procent = (missing_data_crime.merge(type_of_crimes, on="Crime type"))
missing_data_crime_type_procent["missing_percent"] = (missing_data_crime_type_procent["missing_rows"] / missing_data_crime_type_procent["crime_count"] * 100)

duplicate_count = df_london.duplicated().sum()
duplicate_procent = duplicate_count/len(df_london)*100

# df_london = df_london.dropna(subset=["LSOA code"])
# df_crime_by_lsao = (df_london.groupby(["LSOA code", "LSOA name"]).agg(crime_score=("crime_weight", "sum"), total_crimes=("crime_weight", "count")).reset_index())

# Translate into JSON
info = {
    "crimes":{
        "crimes_per_month": crimes_per_month.to_dict(),
        "type_of_crimes": type_of_crimes.to_dict()#,
        # "lsoa_most_crimes_10": lsoa_most_crimes_10.to_dict(),
        # "lsoa_highest_crimescore_10": lsoa_highest_crimescore_10.to_dict(),
    },
    
    "missing_data": {
        "missing_data_month": missing_data_month.to_dict(),
        "missing_data_month_procent": missing_data_month_procent.to_dict(),
        "missing_data_crime": missing_data_crime.to_dict(),
        "missing_data_crime_type_procent": missing_data_crime_type_procent.to_dict(),
        "missing_attributes": missing_attributes.to_dict()
    },

    "duplicate_data": {
        "duplicate_rows": int(duplicate_count),
        "duplicate_rows_procent": float(round(duplicate_procent, 2))
    }
}

with open("EDA_code_Ezra/info.json", "w") as f:
    json.dump(info, f, indent=4)