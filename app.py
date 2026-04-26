import streamlit as st
import psycopg2
import pandas as pd

# Database Connection
conn= psycopg2.connect(
    dbname="airport_db",
    user="postgres", 
    password="9vb4My@25",
    host="localhost",
    port="5432"
) 

# Title
st.title(" Airport Management System") 

# Fetch passengers
query = "SELECT * FROM Passengers"
df = pd.read_sql(query,conn)
st.subheader("Passenger List")
st.dataframe(df)

st.subheader("Flights Data")
query_flights = "SELECT * FROM Flights"
df_flights = pd.read_sql(query_flights,conn)
st.dataframe(df_flights)

# Top Travller
st.subheader("Top Traveller")

query_top_traveler = """
SELECT p.name, COUNT(b.booking_id) AS total_trips
FROM Bookings b 
JOIN Passengers p ON b.passenger_id = p.passenger_id
GROUP BY p.name
ORDER BY total_trips DESC
LIMIT 1;
"""
df_top = pd.read_sql(query_top_traveler,conn)
st.dataframe(df_top) 


# Busiest Routes 
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


# Peak Booking Hour 
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


