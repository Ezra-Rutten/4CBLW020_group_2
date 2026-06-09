# scripts/generate_predictions.py 
# SKETCHY FILE - METROPOLITAN IS HARDCODED SO U CANNOT USE IT FOR NOW FOR DIFFERENT CITIES
import itertools
import pandas as pd
import sys
sys.path.append("../services")

from prediction import load_model_and_encoders
from budget_allocation import allocate_budget
from crime_weight import crime_weights


def generate_predictions(city: str):
    data_path: str = "../data/processed/"+city+"_all_data_uncleaned.csv"
    model_path: str = "../models/prediction_model.pkl"
    lsoa_station_path: str = "../data/shape/lsoa_station_map.csv"
    police_stations_path: str = "../data/shape/police_stations.csv"
    predictions_output: str = "../data/processed/lsoa_crime_predictions_"+city+".csv"
    budget_output: str = "../data/allocation/"+city+"budget_allocation.csv"

    model, le_crime, le_lsoa = load_model_and_encoders(data_path, model_path)

    lsoa_station = pd.read_csv(lsoa_station_path, usecols=["LSOA21CD", "station"])
    police_station = pd.read_csv(police_stations_path, usecols=["station", "police_force"])
    lsoa_station = (
        lsoa_station
        .merge(police_station, on="station", how="left")
        [["LSOA21CD", "station", "police_force"]]
    )

    all_lsoas = le_lsoa.classes_
    all_crime_types = le_crime.classes_
    months = list(range(1, 13))

    rows = list(itertools.product(all_lsoas, all_crime_types, months))
    pred_df = pd.DataFrame(rows, columns=["LSOA code", "Crime type", "month_num"])
    pred_df["year"] = 2025

    pred_df["lsoa_enc"] = le_lsoa.transform(pred_df["LSOA code"])
    pred_df["crime_type_enc"] = le_crime.transform(pred_df["Crime type"])

    pred_df["predicted_crime_count"] = model.predict(
        pred_df[["crime_type_enc", "month_num", "lsoa_enc"]]
    )
    pred_df["predicted_crime_count"] = (
        pred_df["predicted_crime_count"].clip(lower=0).round().astype(int)
    )

    pred_df["severity_score"] = pred_df["Crime type"].map(crime_weights)
    pred_df["predicted_crime_severity"] = (
        pred_df["predicted_crime_count"] * pred_df["severity_score"]
    )

    pred_df = pred_df.merge(
        lsoa_station, left_on="LSOA code", right_on="LSOA21CD", how="inner"
    ).drop(columns="LSOA21CD")

    out_df = pred_df[
        ["LSOA code", "station", "police_force", "Crime type", "year", "month_num",
         "predicted_crime_count", "predicted_crime_severity"]
    ].rename(columns={"month_num": "month"})

    out_df = out_df[out_df["police_force"] == city]
    out_df.to_csv(predictions_output, index=False)
    print(f"Saved {len(out_df):,} rows to {predictions_output}")

    budget_df = allocate_budget(
        predictions_path=predictions_output,
        output_path=budget_output,
    )
    print(f"Saved {len(budget_df):,} rows to {budget_output}")


if __name__ == "__main__":
    cities = ["metropolitan", "merseyside", "west-midlands", "west-yorkshire", "south-yorkshire"]
    for city in cities:
        generate_predictions(city)