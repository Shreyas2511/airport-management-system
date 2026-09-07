"""
Improved flight delay prediction model using XGBoost + hyperparameter tuning.
Compares against the baseline RandomForest model from train_delay_model.py.

Run this AFTER generate_synthetic_data.py has populated the database.
"""

from dotenv import load_dotenv
import os
load_dotenv()

import pandas as pd
import numpy as np
import joblib
import os

from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_auc_score
from xgboost import XGBClassifier

# ---------- CONFIG ----------
DB_CONFIG = {
    "dbname": "airport_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),  # <-- put your postgres password here
    "host": "localhost",
    "port": "5432"
}

MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data():
    encoded_password = quote_plus(DB_CONFIG["password"])
    engine = create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{encoded_password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )

    query = """
        SELECT
            f.flight_id,
            f.airline,
            f.source_airport,
            f.destination_airport,
            f.departure_time,
            f.distance_km,
            f.aircraft_type,
            f.status,
            f.delay_minutes,
            w.condition AS weather_condition,
            w.wind_speed_kmph,
            w.visibility_km,
            w.temperature_c
        FROM Flights f
        JOIN Weather w
          ON w.airport_id = f.source_airport
         AND w.date = f.departure_time::date
        WHERE f.status != 'cancelled';
    """

    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def engineer_features(df):
    df["departure_time"] = pd.to_datetime(df["departure_time"])
    df["hour"] = df["departure_time"].dt.hour
    df["day_of_week"] = df["departure_time"].dt.dayofweek
    df["month"] = df["departure_time"].dt.month

    # Extra engineered features that might help XGBoost
    df["is_peak_hour"] = df["hour"].isin([7, 8, 17, 18, 19, 20]).astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_long_haul"] = (df["distance_km"] > 6000).astype(int)

    df["is_delayed"] = (df["delay_minutes"] > 15).astype(int)

    cat_cols = ["airline", "aircraft_type", "weather_condition"]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = [
        "hour", "day_of_week", "month", "distance_km",
        "wind_speed_kmph", "visibility_km", "temperature_c",
        "airline_enc", "aircraft_type_enc", "weather_condition_enc",
        "is_peak_hour", "is_weekend", "is_long_haul"
    ]

    return df, feature_cols, encoders


def train_xgboost(df, feature_cols):
    X = df[feature_cols]
    y = df["is_delayed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Handle class imbalance
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    base_model = XGBClassifier(
        random_state=42,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight
    )

    # Hyperparameter search space
    param_dist = {
        "n_estimators": [100, 200, 300, 400],
        "max_depth": [3, 4, 5, 6, 8],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "min_child_weight": [1, 3, 5]
    }

    print("Running hyperparameter search (this may take 1-3 minutes)...")
    search = RandomizedSearchCV(
        base_model,
        param_distributions=param_dist,
        n_iter=25,
        scoring="f1",
        cv=3,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    search.fit(X_train, y_train)

    print(f"\nBest params: {search.best_params_}")
    best_model = search.best_estimator_

    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    print("\n--- Tuned XGBoost Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["On-Time", "Delayed"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    importances = pd.Series(best_model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\nFeature Importances:")
    print(importances)

    return best_model


def main():
    print("Loading data from PostgreSQL...")
    df = load_data()
    print(f"Loaded {len(df)} flight records.")

    print("Engineering features...")
    df, feature_cols, encoders = engineer_features(df)

    print(f"Delayed flights: {df['is_delayed'].sum()} / {len(df)} ({df['is_delayed'].mean()*100:.1f}%)")

    model = train_xgboost(df, feature_cols)

    joblib.dump(model, f"{MODEL_DIR}/delay_model_xgb.pkl")
    joblib.dump(encoders, f"{MODEL_DIR}/encoders_xgb.pkl")
    joblib.dump(feature_cols, f"{MODEL_DIR}/feature_cols_xgb.pkl")

    print(f"\nModel saved to {MODEL_DIR}/delay_model_xgb.pkl")


if __name__ == "__main__":
    main()