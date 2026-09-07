"""
Forecasts passenger booking demand using historical booking data.
Uses Facebook Prophet for time-series forecasting.

Run this AFTER generate_synthetic_data.py has populated the database.
"""
from dotenv import load_dotenv
import os
load_dotenv()

import pandas as pd
import joblib
import os

from urllib.parse import quote_plus
from sqlalchemy import create_engine
from prophet import Prophet

# ---------- CONFIG ----------
DB_CONFIG = {
    "dbname": "airport_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

FORECAST_DAYS = 30
TRIM_LAST_DAYS = 60   # drop the last N days — artifact of how bookings were generated (booking_date = flight_date - random(1,60))


def load_booking_data():
    encoded_password = quote_plus(DB_CONFIG["password"])
    engine = create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{encoded_password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )

    query = """
        SELECT booking_date::date AS ds, COUNT(*) AS y
        FROM Bookings
        GROUP BY booking_date::date
        ORDER BY ds;
    """

    df = pd.read_sql(query, engine)
    engine.dispose()

    # Drop the last N days — incomplete/artificially declining tail
    df = df.iloc[:-TRIM_LAST_DAYS].reset_index(drop=True)

    return df


def train_and_forecast(df):
    print(f"Training on {len(df)} days of booking history (after trimming incomplete tail)...")

    # Use logistic growth so forecast can never go below floor (0) or above a sensible cap
    df["floor"] = 0
    df["cap"] = df["y"].max() * 1.5   # allow some headroom above historical peak

    model = Prophet(
        growth="logistic",
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=FORECAST_DAYS)
    future["floor"] = 0
    future["cap"] = df["y"].max() * 1.5
    forecast = model.predict(future)

    return model, forecast


def main():
    print("Loading booking data from PostgreSQL...")
    df = load_booking_data()

    if len(df) < 30:
        print("WARNING: Less than 30 days of data — forecast may be unreliable.")

    model, forecast = train_and_forecast(df)

    print(f"\n--- Forecast for next {FORECAST_DAYS} days ---")
    future_forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(FORECAST_DAYS)
    future_forecast["yhat"] = future_forecast["yhat"].round(1)
    future_forecast["yhat_lower"] = future_forecast["yhat_lower"].clip(lower=0).round(1)
    future_forecast["yhat_upper"] = future_forecast["yhat_upper"].round(1)
    print(future_forecast.to_string(index=False))

    joblib.dump(model, f"{MODEL_DIR}/demand_model.pkl")
    forecast.to_csv(f"{MODEL_DIR}/demand_forecast.csv", index=False)

    print(f"\nModel saved to {MODEL_DIR}/demand_model.pkl")
    print(f"Forecast saved to {MODEL_DIR}/demand_forecast.csv")


if __name__ == "__main__":
    main()
    