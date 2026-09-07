"""
Clusters airports by congestion level using K-Means, based on:
- Total flights handled
- Average delay minutes
- Traffic capacity

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
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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

N_CLUSTERS = 3

AIRPORT_COORDS = {
    "JFK": (40.6413, -73.7781), "LAX": (33.9416, -118.4085), "ORD": (41.9742, -87.9073),
    "ATL": (33.6407, -84.4277), "LHR": (51.4700, -0.4543), "CDG": (49.0097, 2.5479),
    "FRA": (50.0379, 8.5622), "AMS": (52.3105, 4.7683), "DXB": (25.2532, 55.3657),
    "HND": (35.5494, 139.7798), "SIN": (1.3644, 103.9915), "SYD": (-33.9399, 151.1753),
    "DEL": (28.5562, 77.1000), "BOM": (19.0896, 72.8656), "PNQ": (18.5822, 73.9197),
    "BLR": (13.1986, 77.7066), "HKG": (22.3080, 113.9185), "ICN": (37.4602, 126.4407),
    "PEK": (40.0799, 116.6031), "GRU": (-23.4356, -46.4731), "MEX": (19.4363, -99.0721),
    "YYZ": (43.6777, -79.6248), "MAD": (40.4983, -3.5676), "FCO": (41.8003, 12.2389),
    "IST": (41.2753, 28.7519), "DOH": (25.2731, 51.6081), "JNB": (-26.1392, 28.2460),
    "CAI": (30.1219, 31.4056), "SVO": (55.9726, 37.4146), "ZRH": (47.4647, 8.5492),
}


def load_airport_stats():
    encoded_password = quote_plus(DB_CONFIG["password"])
    engine = create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{encoded_password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )

    query = """
        SELECT
            a.airport_id,
            a.airport_name,
            a.city,
            a.country,
            a.traffic_capacity,
            COUNT(f.flight_id) AS total_flights,
            COALESCE(AVG(f.delay_minutes), 0) AS avg_delay
        FROM Airports a
        LEFT JOIN Flights f ON f.source_airport = a.airport_id
        GROUP BY a.airport_id, a.airport_name, a.city, a.country, a.traffic_capacity
        ORDER BY total_flights DESC;
    """

    df = pd.read_sql(query, engine)
    engine.dispose()
    return df


def attach_coordinates(df):
    def extract_code(name):
        if "(" in name and ")" in name:
            return name.split("(")[-1].replace(")", "").strip()
        return None

    df["code"] = df["airport_name"].apply(extract_code)
    df["lat"] = df["code"].map(lambda c: AIRPORT_COORDS.get(c, (None, None))[0])
    df["lon"] = df["code"].map(lambda c: AIRPORT_COORDS.get(c, (None, None))[1])
    return df


def run_clustering(df):
    features = df[["total_flights", "avg_delay", "traffic_capacity"]].copy()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(scaled)

    cluster_order = df.groupby("cluster")["total_flights"].mean().sort_values().index
    label_map = {cluster_order[0]: "Low Congestion", cluster_order[1]: "Medium Congestion", cluster_order[2]: "High Congestion"}
    df["congestion_level"] = df["cluster"].map(label_map)

    return df, kmeans, scaler


def main():
    print("Loading airport stats from PostgreSQL...")
    df = load_airport_stats()
    print(f"Loaded {len(df)} airports.")

    print("Attaching coordinates...")
    df = attach_coordinates(df)

    print("Running K-Means clustering...")
    df, kmeans, scaler = run_clustering(df)

    print("\n--- Cluster Summary ---")
    summary = df.groupby("congestion_level")[["total_flights", "avg_delay", "traffic_capacity"]].mean().round(1)
    print(summary)

    print("\n--- Airports by Cluster ---")
    print(df[["city", "country", "total_flights", "avg_delay", "congestion_level"]].to_string(index=False))

    df.to_csv(f"{MODEL_DIR}/airport_clusters.csv", index=False)
    joblib.dump(kmeans, f"{MODEL_DIR}/kmeans_model.pkl")
    joblib.dump(scaler, f"{MODEL_DIR}/kmeans_scaler.pkl")

    print(f"\nSaved to {MODEL_DIR}/airport_clusters.csv")


if __name__ == "__main__":
    main()