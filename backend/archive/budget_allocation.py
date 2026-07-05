import pandas as pd


def allocate_budget(predictions_path: str, output_path: str) -> pd.DataFrame:
    """
    Aggregate predicted_crime_severity by station and month,
    then compute each station's share of total severity as a budget percentage.

    Returns the resulting DataFrame and saves it to output_path.
    """
    df = pd.read_csv(predictions_path)

    station_monthly = (
        df.groupby(["station", "month"], as_index=False)["predicted_crime_severity"]
        .sum()
        .rename(columns={"predicted_crime_severity": "total_predicted_crime_severity"})
    )

    monthly_totals = (
        station_monthly.groupby("month")["total_predicted_crime_severity"]
        .transform("sum")
    )
    station_monthly["budget_allocation_pct"] = (
        station_monthly["total_predicted_crime_severity"] / monthly_totals * 100
    ).round(4)

    station_monthly = station_monthly.sort_values(["month", "station"]).reset_index(drop=True)
    station_monthly.to_csv(output_path, index=False)
    return station_monthly


if __name__ == "__main__":
    result = allocate_budget(
        predictions_path="../data/processed/lsoa_crime_predictions.csv",
        output_path="../data/processed/budget_allocation.csv",
    )
    print(result.head(20))
