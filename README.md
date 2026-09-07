
# ✈️ Smart Airport Management System with ML Analytics

An advanced airport management system combining PostgreSQL, Streamlit, and Machine Learning to predict flight delays, forecast passenger demand, and analyze airport congestion patterns.

## Features

- **Flight Delay Prediction** — XGBoost classifier (83.7% accuracy, 0.91 ROC-AUC) predicts delay risk using weather, time, and route features
- **Passenger Demand Forecasting** — Facebook Prophet model forecasts 30-day booking trends
- **Airport Congestion Clustering** — K-Means groups 30 global airports into traffic tiers, visualized on an interactive map
- **Interactive Dashboard** — Real-time passenger/flight data, top travelers, busiest routes, peak booking hours

## Tech Stack

- **Database:** PostgreSQL
- **Backend/ML:** Python, scikit-learn, XGBoost, Prophet
- **Frontend:** Streamlit, Plotly
- **Libraries:** pandas, numpy, psycopg2, SQLAlchemy, joblib, Faker

## Project Structure
airport-management-system/
├── sql/ # Database schema
│ ├── setup.sql
│ └── alter_schema.sql
├── scripts/
│ └── generate_synthetic_data.py # Synthetic dataset generator
├── ml/
│ ├── train_delay_model.py # Baseline Random Forest
│ ├── train_delay_model_v2.py # Tuned XGBoost (production model)
│ ├── forecast_demand.py # Prophet demand forecasting
│ ├── cluster_airports.py # K-Means congestion clustering
│ └── models/ # Saved trained models
├── app.py # Streamlit application
└── requirements.txt

## Setup Instructions

1. Clone the repo:

git clone https://github.com/shreyasbaravkar/airport-management-system.git
cd airport-management-system


2. Install dependencies:

pip install -r requirements.txt


3. Set up PostgreSQL database:

psql -U postgres -c "CREATE DATABASE airport_db;"
psql -U postgres -d airport_db -f sql/setup.sql
psql -U postgres -d airport_db -f sql/alter_schema.sql


4. Create a `.env` file in the root with your database password:

DB_PASSWORD=your_postgres_password

5. Generate synthetic data and train models:

python scripts/generate_synthetic_data.py
python ml/train_delay_model_v2.py
python ml/forecast_demand.py
python ml/cluster_airports.py


6. Run the app:

streamlit run app.py


## Model Performance

| Model | Metric | Score |
|---|---|---|
| Delay Prediction (XGBoost) | Accuracy | 83.7% |
| Delay Prediction (XGBoost) | ROC-AUC | 0.908 |
| Demand Forecast (Prophet) | Forecast Horizon | 30 days |
| Congestion Clustering | Clusters | 3 (Low/Medium/High) |