from dotenv import load_dotenv
import os
load_dotenv()


import streamlit as st
import psycopg2
import pandas as pd
import joblib
import datetime
import plotly.express as px

# ---------- Database Connection ----------
conn = psycopg2.connect(
    dbname="airport_db",
    user="postgres",
    password= os.getenv("DB_PASSWORD"),
    host="localhost",
    port="5432"
)

st.set_page_config(page_title="Airport Management System", layout="wide")
st.title("✈️ Smart Airport Management System")

# ---------- Load ML models (cached so they don't reload on every interaction) ----------
@st.cache_resource
def load_delay_model():
    model = joblib.load("ml/models/delay_model_xgb.pkl")
    encoders = joblib.load("ml/models/encoders_xgb.pkl")
    feature_cols = joblib.load("ml/models/feature_cols_xgb.pkl")
    return model, encoders, feature_cols

@st.cache_data
def load_demand_forecast():
    return pd.read_csv("ml/models/demand_forecast.csv", parse_dates=["ds"])

@st.cache_data
def load_airport_clusters():
    return pd.read_csv("ml/models/airport_clusters.csv")

delay_model, encoders, feature_cols = load_delay_model()
forecast_df = load_demand_forecast()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", "🔮 Predict Delay", "📈 Demand Forecast", "🏆 Analytics", "🗺️ Congestion Map"
])

# ================= TAB 1: DASHBOARD =================
with tab1:
    st.subheader("Passenger List")
    df = pd.read_sql("SELECT * FROM Passengers", conn)
    st.dataframe(df)

    st.subheader("Flights Data")
    df_flights = pd.read_sql("SELECT * FROM Flights", conn)
    st.dataframe(df_flights)

# ================= TAB 2: PREDICT DELAY =================
with tab2:
    st.subheader("Predict Whether a Flight Will Be Delayed")
    st.caption("Enter flight details below — the model predicts delay risk using weather, timing, and route features.")

    col1, col2 = st.columns(2)

    with col1:
        airline = st.selectbox("Airline", encoders["airline"].classes_)
        aircraft_type = st.selectbox("Aircraft Type", encoders["aircraft_type"].classes_)
        weather_condition = st.selectbox("Weather Condition", encoders["weather_condition"].classes_)
        distance_km = st.number_input("Distance (km)", min_value=100, max_value=15000, value=2000)

    with col2:
        dep_date = st.date_input("Departure Date", datetime.date.today())
        dep_hour = st.slider("Departure Hour (0-23)", 0, 23, 10)
        wind_speed = st.slider("Wind Speed (km/h)", 0, 100, 15)
        visibility = st.slider("Visibility (km)", 0.0, 10.0, 8.0)
        temperature = st.slider("Temperature (°C)", -20, 45, 22)

    if st.button("Predict Delay Risk", type="primary"):
        day_of_week = dep_date.weekday()
        month = dep_date.month
        is_peak_hour = int(dep_hour in [7, 8, 17, 18, 19, 20])
        is_weekend = int(day_of_week in [5, 6])
        is_long_haul = int(distance_km > 6000)

        input_data = pd.DataFrame([{
            "hour": dep_hour,
            "day_of_week": day_of_week,
            "month": month,
            "distance_km": distance_km,
            "wind_speed_kmph": wind_speed,
            "visibility_km": visibility,
            "temperature_c": temperature,
            "airline_enc": encoders["airline"].transform([airline])[0],
            "aircraft_type_enc": encoders["aircraft_type"].transform([aircraft_type])[0],
            "weather_condition_enc": encoders["weather_condition"].transform([weather_condition])[0],
            "is_peak_hour": is_peak_hour,
            "is_weekend": is_weekend,
            "is_long_haul": is_long_haul
        }])[feature_cols]

        prediction = delay_model.predict(input_data)[0]
        probability = delay_model.predict_proba(input_data)[0][1]

        st.divider()
        if prediction == 1:
            st.error(f"⚠️ High Delay Risk — {probability*100:.1f}% probability of delay")
        else:
            st.success(f"✅ Likely On-Time — {probability*100:.1f}% probability of delay")

        st.progress(min(float(probability), 1.0))

# ================= TAB 3: DEMAND FORECAST =================
with tab3:
    st.subheader("30-Day Booking Demand Forecast")
    st.caption("Predicted daily bookings based on historical trends (Prophet time-series model).")

    future_only = forecast_df.tail(30)

    chart_data = future_only.set_index("ds")[["yhat", "yhat_lower", "yhat_upper"]]
    chart_data.columns = ["Predicted", "Lower Bound", "Upper Bound"]
    st.line_chart(chart_data)

    st.subheader("Forecast Table")
    display_df = future_only[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    display_df.columns = ["Date", "Predicted Bookings", "Lower Bound", "Upper Bound"]
    display_df["Predicted Bookings"] = display_df["Predicted Bookings"].round(1)
    st.dataframe(display_df, use_container_width=True)

# ================= TAB 4: ANALYTICS (original queries) =================
with tab4:
    st.subheader("Top Traveller")
    query_top_traveler = """
    SELECT p.name, COUNT(b.booking_id) AS total_trips
    FROM Bookings b 
    JOIN Passengers p ON b.passenger_id = p.passenger_id
    GROUP BY p.name
    ORDER BY total_trips DESC
    LIMIT 1;
    """
    df_top = pd.read_sql(query_top_traveler, conn)
    st.dataframe(df_top)

    st.subheader("Busiest Routes")
    query_routes = """
    SELECT 
        a1.city AS source,
        a2.city AS destination,
        COUNT(b.booking_id) AS total_bookings
    FROM Bookings b
    JOIN Flights f ON b.flight_id = f.flight_id
    JOIN Airports a1 ON f.source_airport = a1.airport_id
    JOIN Airports a2 ON f.destination_airport = a2.airport_id
    GROUP BY a1.city, a2.city
    ORDER BY total_bookings DESC
    LIMIT 5;
    """
    df_routes = pd.read_sql(query_routes, conn)
    st.dataframe(df_routes)

    st.subheader("Peak Booking Hour")
    query_peak = """
    SELECT 
        EXTRACT(HOUR FROM booking_date) AS booking_hour,
        COUNT(*) AS total_bookings
    FROM Bookings
    GROUP BY booking_hour
    ORDER BY total_bookings DESC
    LIMIT 1;
    """
    df_peak = pd.read_sql(query_peak, conn)
    st.dataframe(df_peak)

# ================= TAB 5: CONGESTION MAP =================
with tab5:
    st.subheader("Airport Congestion Clusters")
    st.caption("Airports grouped by traffic load using K-Means clustering — color indicates congestion tier.")

    clusters_df = load_airport_clusters()

    color_map = {
        "High Congestion": "#e74c3c",
        "Medium Congestion": "#f39c12",
        "Low Congestion": "#2ecc71"
    }

    fig = px.scatter_geo(
        clusters_df,
        lat="lat",
        lon="lon",
        color="congestion_level",
        color_discrete_map=color_map,
        hover_name="city",
        hover_data={"total_flights": True, "avg_delay": ":.1f", "traffic_capacity": True, "lat": False, "lon": False},
        size="total_flights",
        projection="natural earth",
        title="Global Airport Congestion Levels"
    )
    fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Cluster Summary")
    summary = clusters_df.groupby("congestion_level")[["total_flights", "avg_delay", "traffic_capacity"]].mean().round(1)
    st.dataframe(summary, use_container_width=True)