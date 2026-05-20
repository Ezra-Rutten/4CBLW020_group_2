# 4CBLW020 Group 2

## Setup

Install dependencies:

```
pip install -r backend/requirements.txt
```

## Data

Place the Metropolitan Police crime CSV files inside `backend/data/raw/`, organized by month:

The `backend/data/processed/` folder will be created automatically when you run the pipeline.

## Running the pipeline

From the `backend/services/` directory:

```
python data.py
```

This reads all CSVs from `data/raw/`, combines them, and saves the result to `data/processed/london_all_data_uncleaned.csv`.

## Running the notebooks

Open the notebooks from `backend/notebooks/` in Jupyter. Run `data.py` first to generate the processed data before running any notebook.
