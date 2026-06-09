"""FastAPI app that serves the dashboard and the computed crime/allocation data.

Run from the backend/ folder:

    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/ in a browser.

Data sources (all under backend/data):
  - shape/police_stations.csv .................. station metadata (all forces)
  - allocation/<force>budget_allocation.csv .... budget % + specialist % per station
  - processed/lsoa_crime_predictions_<force>.csv  per-LSOA monthly predictions

Note: results are cached in-memory per city. After re-running the prediction
pipeline, restart the server (or it auto-reloads when main.py changes) to pick
up fresh CSVs.
"""
import math
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIONS_CSV = DATA_DIR / "shape" / "police_stations.csv"
WEBSITE_DIR = BASE_DIR.parent / "website"

# Dashboard city name -> police force key used in the data files.
CITY_TO_FORCE = {
    "London": "metropolitan",
    "Birmingham": "west-midlands",
    "Leeds": "west-yorkshire",
    "Sheffield": "south-yorkshire",
    "Liverpool": "merseyside",
}

app = FastAPI(title="Police Resource Allocation API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


def _budget_csv(force: str) -> Path:
    return DATA_DIR / "allocation" / f"{force}budget_allocation.csv"


def _predictions_csv(force: str) -> Path:
    return DATA_DIR / "processed" / f"lsoa_crime_predictions_{force}.csv"


def _clean(value):
    """Convert pandas NaN to None so the JSON is valid."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


@lru_cache(maxsize=None)
def build_city(city: str) -> dict:
    """Assemble everything the dashboard needs for one city from the CSVs."""
    force = CITY_TO_FORCE[city]

    # 1. Station metadata for this force.
    stations = pd.read_csv(STATIONS_CSV)
    stations = stations[stations["police_force"] == force].copy()

    # 2. Merge budget % + specialist % (per station, yearly).
    budget_path = _budget_csv(force)
    if budget_path.exists():
        budget = pd.read_csv(budget_path)
        stations = stations.merge(budget, on="station", how="left")
        # Frontend reads `predicted_severity`; the budget file calls it this.
        if "total_predicted_crime_severity" in stations:
            stations["predicted_severity"] = stations["total_predicted_crime_severity"]

    station_records = [
        {k: _clean(v) for k, v in rec.items()}
        for rec in stations.to_dict(orient="records")
    ]

    # 3. Monthly + crime-type aggregates from the predictions file.
    monthly, crime_types, incident_estimate = [], [], 0
    pred_path = _predictions_csv(force)
    if pred_path.exists():
        preds = pd.read_csv(pred_path)
        incident_estimate = int(preds["predicted_crime_count"].sum())
        by_month = preds.groupby("month")["predicted_crime_count"].sum()
        monthly = [{"month": int(m), "count": int(c)} for m, c in by_month.items()]
        by_type = preds.groupby("Crime type")["predicted_crime_count"].sum()
        crime_types = [{"crime_type": t, "count": int(c)} for t, c in by_type.items()]

    return {
        "city": city,
        "force": force,
        "folder": city,
        "note": f"Live data for {force.replace('-', ' ').title()} "
                f"({len(station_records)} stations) built from the backend pipeline.",
        "incident_estimate": incident_estimate,
        "stations": station_records,
        "monthly": monthly,
        "crime_types": crime_types,
    }


@app.get("/api/cities")
def list_cities():
    """City list for the dropdown, with a station count + total estimate each."""
    out = []
    for city, force in CITY_TO_FORCE.items():
        data = build_city(city)
        out.append({
            "city": city,
            "force": force,
            "station_count": len(data["stations"]),
            "incident_estimate": data["incident_estimate"],
        })
    return out


@app.get("/api/city/{city}")
def get_city(city: str):
    """Full payload for one city: stations, budget, monthly + crime-type data."""
    if city not in CITY_TO_FORCE:
        raise HTTPException(status_code=404, detail=f"Unknown city: {city}")
    return build_city(city)


# Serve the static frontend. Mounted AFTER the API routes so /api/* still wins.
if WEBSITE_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEBSITE_DIR), html=True), name="website")
