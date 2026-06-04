import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import joblib
import lightgbm as lgb

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

    train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=["crime_type_enc", "lsoa_enc"])
    test_data  = lgb.Dataset(X_test, label=y_test, reference=train_data, categorical_feature=["crime_type_enc", "lsoa_enc"])

    params = {
        "objective": "poisson",
        "metric": "poisson",
        "learning_rate": 0.03,
        "max_depth": 4,
        "num_leaves": 15,
        "min_data_in_leaf": 10,
        "bagging_fraction": 0.7,
        "bagging_freq": 1,
        "feature_fraction": 0.7,
        "lambda_l1": 0.1,
        "lambda_l2": 1.5,
        "seed": 42,
        "verbose": -1
    }
    num_round = 800
    model = lgb.train(
        params,
        train_data,
        num_boost_round=num_round,
        valid_sets=[test_data]
    )

    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"RMSE: {rmse:.2f}")    

    joblib.dump(model, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_model()