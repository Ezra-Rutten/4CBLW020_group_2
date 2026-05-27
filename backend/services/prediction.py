import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib


def load_model_and_encoders(data_path: str, model_path: str):
    df = pd.read_csv(data_path, low_memory=False)
    df = df.dropna(subset=["LSOA code", "Crime type", "Month"])
    df = df.drop(columns=["Context"], errors="ignore")

    df["Month"] = pd.to_datetime(df["Month"])
    df = (
        df.groupby(["LSOA code", "Month", "Crime type"])
        .size()
        .reset_index(name="crime_count")
    )

    le_crime = LabelEncoder()
    le_lsoa = LabelEncoder()
    le_crime.fit(df["Crime type"].fillna("Unknown"))
    le_lsoa.fit(df["LSOA code"].fillna("Unknown"))

    model = joblib.load(model_path)
    return model, le_crime, le_lsoa


def predict(df: pd.DataFrame, model, le_crime: LabelEncoder, le_lsoa: LabelEncoder) -> pd.DataFrame:
    df = df[["LSOA code", "Month", "Crime type"]].drop_duplicates().copy()
    df["month_num"] = pd.to_datetime(df["Month"]).dt.month
    df["crime_type_enc"] = le_crime.transform(df["Crime type"].fillna("Unknown"))
    df["lsoa_enc"] = le_lsoa.transform(df["LSOA code"].fillna("Unknown"))

    features = ["crime_type_enc", "month_num", "lsoa_enc"]
    df["predicted_crime_count"] = model.predict(df[features])
