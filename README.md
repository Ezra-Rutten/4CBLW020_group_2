# Police Resource Allocation — Setup & Run

## Install dependencies

    cd backend
    pip install -r requirements.txt

The model now trains with **LightGBM** (`lightgbm` is in requirements.txt).
`xgboost` is only needed if you also run the exploratory
`notebooks/prediction.ipynb`, which still compares XGBoost vs LightGBM.

## Required input data (must be in place before running)

- backend/data/raw/ → monthly crime CSVs
- backend/data/LB_shp/ → London Borough shapefiles
- backend/data/forc_kmls/ → police force KML boundaries

## Run the full pipeline

### Step 1 — from `backend/scripts/` (run both, order doesn't matter)

    python preprocess_data.py   # combines raw CSVs → data/processed/
    python fetch_stations.py    # fetches station coordinates → data/shape/police_stations.csv

### Step 2 — from `backend/scripts/` (run after step 1)

    python build_lsoa_map.py    # maps LSOAs to stations → data/shape/lsoa_station_map.csv
    python train_model.py       # trains LightGBM model → models/prediction_model.pkl

### Step 3 — from `backend/services/` (run after step 2)

    python generate_predictions.py
    # predictions + budget for all 5 forces →
    #   data/processed/lsoa_crime_predictions_<force>.csv
    #   data/allocation/<force>budget_allocation.csv

## After the XGBoost → LightGBM switch

The model swap only affects the last two steps. To refresh everything with the
new model, re-run just these (the data-prep steps in Step 1 are unaffected and
don't need re-running unless the raw data changes):

    # from backend/scripts/
    python train_model.py
    # then from backend/services/
    python generate_predictions.py

This regenerates the per-force prediction and budget CSVs, so the dashboard's
allocation-need values, predicted severities and priority colours will shift
**slightly** — LightGBM fits the data a bit better (RMSE ~4.4 vs XGBoost ~5.3),
so the predicted counts (and everything derived from them) change.

## View the dashboard

    cd backend
    uvicorn main:app --reload --port 8000
    # then open http://localhost:8000/

The API caches each city in memory, so **restart uvicorn** after regenerating
the CSVs to pick up the new numbers.
