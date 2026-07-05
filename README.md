# Police Resource Allocation — Setup & Run

## Install dependencies

pip install -r requirements.txt

## Required input data (must be in place before running)

- backend/data/raw/ → monthly crime CSVs
- backend/data/LB_shp/ → London Borough shapefiles
- backend/data/forc_kmls/ → police force KML boundaries

## Run the pipeline (from backend/scripts/)

# Step 1 — run both, order doesn't matter

python preprocess_data.py # combines raw CSVs → data/processed/
python fetch_stations.py # fetches station coordinates → data/shape/police_stations.csv

# Step 2 — run after step 1

python build_lsoa_map.py # maps LSOAs to stations → data/shape/lsoa_station_map.csv
python train_model.py # trains XGBoost model → models/prediction_model.pkl

# Step 3 — run after step 2

python generate_predictions.py # generates predictions + budget → data/processed/
