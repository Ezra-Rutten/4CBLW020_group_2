import pandas as pd

from crime_weight import (
    crime_weights_mental_health,
    crime_weights_social_services,
    crime_weights_negotiator,
    crime_weights_k9,
    crime_weights_swat,
)

# Specialist name -> per-crime weight lookup
SPECIALIST_WEIGHTS = {
    "mental_health": crime_weights_mental_health,
    "social_services": crime_weights_social_services,
    "negotiator": crime_weights_negotiator,
    "k9": crime_weights_k9,
    "swat": crime_weights_swat,
}


def allocate_budget(predictions_path: str, output_path: str) -> pd.DataFrame:
    """
    Aggregate predicted_crime_severity by station (yearly), compute each
    station's share of total severity as a budget percentage, and add a column
    per specialist.

    Each specialist value per row is:
        predicted_crime_count * crime_weight[crime] * specialist_weight[crime]
    which equals predicted_crime_severity * specialist_weight[crime], since
    predicted_crime_severity already includes the general crime weight.

    Returns the resulting DataFrame and saves it to output_path.
    """
    df = pd.read_csv(predictions_path)

    # Per-row specialist demand scores
    for name, weights in SPECIALIST_WEIGHTS.items():
        df[name] = df["predicted_crime_severity"] * df["Crime type"].map(weights)

    agg = {"predicted_crime_severity": "sum"}
    agg.update({name: "sum" for name in SPECIALIST_WEIGHTS})

    station_yearly = (
        df.groupby("station", as_index=False)
        .agg(agg)
        .rename(columns={"predicted_crime_severity": "total_predicted_crime_severity"})
    )

    yearly_total = station_yearly["total_predicted_crime_severity"].sum()
    station_yearly["budget_allocation_pct"] = (
        station_yearly["total_predicted_crime_severity"] / yearly_total * 100
    ).round(4)

    # Convert each specialist column to a percentage of its column total
    for name in SPECIALIST_WEIGHTS:
        col_total = station_yearly[name].sum()
        station_yearly[name] = (
            station_yearly[name] / col_total * 100 if col_total else 0
        ).round(4)

    station_yearly = station_yearly.sort_values("station").reset_index(drop=True)
    station_yearly.to_csv(output_path, index=False)
    return station_yearly


if __name__ == "__main__":
    result = allocate_budget(
        predictions_path="../data/processed/lsoa_crime_predictions.csv",
        output_path="../data/allocation/budget_allocation.csv",
    )
    print(result.head(20))
    print(f"Total budget_allocation_pct sums to: {result['budget_allocation_pct'].sum():.2f}%")
