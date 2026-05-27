import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import joblib


def train_model(
    data_path: str = "../data/processed/all_data_uncleaned.csv",
    output_path: str = "../models/prediction_model.pkl"
):
    df_crimes = pd.read_csv(data_path, low_memory=False)
    df_crimes = df_crimes.dropna(subset=["LSOA code"])
    df_crimes = df_crimes.dropna(subset=["Crime type"])
    df_crimes = df_crimes.dropna(subset=["Month"])
    df_crimes = df_crimes.drop(columns=["Context"])

    df_crimes["Month"] = pd.to_datetime(df_crimes["Month"])

    df_crimes = (
        df_crimes.groupby(["LSOA code", "Month", "Crime type"])
        .size()
        .reset_index(name="crime_count")
    )

    le_crime = LabelEncoder()
    le_lsoa = LabelEncoder()

    df_crimes["crime_type_enc"] = le_crime.fit_transform(df_crimes["Crime type"].fillna("Unknown"))
    df_crimes["lsoa_enc"] = le_lsoa.fit_transform(df_crimes["LSOA code"].fillna("Unknown"))
    df_crimes["month_num"] = pd.to_datetime(df_crimes["Month"]).dt.month

    train = df_crimes[df_crimes["Month"] < "2025-01-01"]
    test = df_crimes[df_crimes["Month"] >= "2025-01-01"]

    features = ["crime_type_enc", "month_num", "lsoa_enc"]
    target = "crime_count"

    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]

    model = xgb.XGBRegressor(
        objective="count:poisson",
        n_estimators=800,
        learning_rate=0.03,
        max_depth=4,
        min_child_weight=10,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.5,
        gamma=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"RMSE: {rmse:.2f}")

    joblib.dump(model, output_path)
    print(f"Model saved to {output_path}")


if __name__ == "__main__":
    train_model()