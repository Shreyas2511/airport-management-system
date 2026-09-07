"""
Trains a flight delay prediction model using historical flight + weather data
from the airport_db PostgreSQL database.

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
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ---------- CONFIG ----------
DB_CONFIG = {
    "dbname": "airport_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),# <-- put your postgres password here
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
    df["day_of_week"] = df["departure_time"].dt.dayofweek   # 0=Monday
    df["month"] = df["departure_time"].dt.month

    # Target: is_delayed (1 if delay > 15 minutes, matching how we generated the data)
    df["is_delayed"] = (df["delay_minutes"] > 15).astype(int)

    # Encode categorical columns
    cat_cols = ["airline", "aircraft_type", "weather_condition"]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = [
        "hour", "day_of_week", "month", "distance_km",
        "wind_speed_kmph", "visibility_km", "temperature_c",
        "airline_enc", "aircraft_type_enc", "weather_condition_enc"
    ]

    return df, feature_cols, encoders


def train_model(df, feature_cols):
    X = df[feature_cols]
    y = df["is_delayed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced"   # handles imbalance (fewer delayed flights than on-time)
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["On-Time", "Delayed"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\nFeature Importances:")
    print(importances)

    return model


def main():
    print("Loading data from PostgreSQL...")
    df = load_data()
    print(f"Loaded {len(df)} flight records.")

    print("Engineering features...")
    df, feature_cols, encoders = engineer_features(df)

    print(f"Delayed flights: {df['is_delayed'].sum()} / {len(df)} ({df['is_delayed'].mean()*100:.1f}%)")

    print("Training model...")
    model = train_model(df, feature_cols)

    # Save model + encoders for later use in the Streamlit app
    joblib.dump(model, f"{MODEL_DIR}/delay_model.pkl")
    joblib.dump(encoders, f"{MODEL_DIR}/encoders.pkl")
    joblib.dump(feature_cols, f"{MODEL_DIR}/feature_cols.pkl")

    print(f"\nModel saved to {MODEL_DIR}/delay_model.pkl")


if __name__ == "__main__":
    main()