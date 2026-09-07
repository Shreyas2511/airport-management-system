"""
Generates 1 year of synthetic airport data using FAST BATCH INSERTS:
- 30 airports with realistic hub-tier traffic bias (Major/Medium/Regional)
- Weather records per airport per day
- ~1 year of flights with realistic delay patterns (weather + hub congestion)
- Matching bookings (with realistic booking-hour distribution)

Run this AFTER setup.sql and alter_schema.sql have been applied.
"""

from dotenv import load_dotenv
import os
load_dotenv()


import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# ---------- CONFIG ----------
DB_CONFIG = {
    "dbname": "airport_db",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

START_DATE = datetime(2025, 9, 1)
END_DATE = datetime(2026, 9, 1)
FLIGHTS_PER_DAY = 15

WEATHER_CONDITIONS = ["Clear", "Cloudy", "Rain", "Storm", "Fog", "Snow"]

# (code, name, city, country, tier)  tier: "major", "medium", "regional"
AIRPORTS = [
    ("JFK", "John F. Kennedy Intl", "New York", "USA", "major"),
    ("LHR", "Heathrow", "London", "UK", "major"),
    ("DXB", "Dubai Intl", "Dubai", "UAE", "major"),
    ("HND", "Haneda", "Tokyo", "Japan", "major"),
    ("ATL", "Hartsfield-Jackson Intl", "Atlanta", "USA", "major"),
    ("ORD", "O'Hare Intl", "Chicago", "USA", "major"),

    ("LAX", "Los Angeles Intl", "Los Angeles", "USA", "medium"),
    ("CDG", "Charles de Gaulle", "Paris", "France", "medium"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany", "medium"),
    ("AMS", "Schiphol", "Amsterdam", "Netherlands", "medium"),
    ("SIN", "Changi", "Singapore", "Singapore", "medium"),
    ("ICN", "Incheon Intl", "Seoul", "South Korea", "medium"),
    ("PEK", "Beijing Capital", "Beijing", "China", "medium"),
    ("DEL", "Indira Gandhi Intl", "Delhi", "India", "medium"),
    ("BOM", "Chhatrapati Shivaji", "Mumbai", "India", "medium"),
    ("YYZ", "Toronto Pearson", "Toronto", "Canada", "medium"),
    ("MAD", "Barajas", "Madrid", "Spain", "medium"),
    ("FCO", "Leonardo da Vinci", "Rome", "Italy", "medium"),

    ("SYD", "Kingsford Smith", "Sydney", "Australia", "regional"),
    ("PNQ", "Pune Airport", "Pune", "India", "regional"),
    ("BLR", "Kempegowda Intl", "Bangalore", "India", "regional"),
    ("HKG", "Hong Kong Intl", "Hong Kong", "China", "regional"),
    ("GRU", "Guarulhos Intl", "Sao Paulo", "Brazil", "regional"),
    ("MEX", "Benito Juarez Intl", "Mexico City", "Mexico", "regional"),
    ("IST", "Istanbul Airport", "Istanbul", "Turkey", "regional"),
    ("DOH", "Hamad Intl", "Doha", "Qatar", "regional"),
    ("JNB", "O.R. Tambo Intl", "Johannesburg", "South Africa", "regional"),
    ("CAI", "Cairo Intl", "Cairo", "Egypt", "regional"),
    ("SVO", "Sheremetyevo", "Moscow", "Russia", "regional"),
    ("ZRH", "Zurich Airport", "Zurich", "Switzerland", "regional"),
]

AIRCRAFT_TYPES = ["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A350", "Boeing 787"]
AIRLINES = ["Delta", "United", "American", "Emirates", "Qatar Airways", "Lufthansa", "Air India", "Singapore Airlines"]

BOOKING_HOUR_WEIGHTS = [1,1,1,1,1,2,3,5,6,6,5,5,5,5,5,6,7,8,7,6,5,4,3,2]

TIER_SELECTION_WEIGHT = {"major": 6, "medium": 3, "regional": 1}
TIER_CAPACITY_RANGE = {"major": (900, 1400), "medium": (500, 900), "regional": (150, 500)}
TIER_CONGESTION_DELAY = {"major": (5, 15), "medium": (0, 8), "regional": (0, 3)}


def connect():
    return psycopg2.connect(**DB_CONFIG)


def clear_old_data(cur):
    cur.execute("TRUNCATE Weather, Bookings, Flights, Passengers, Airports RESTART IDENTITY CASCADE;")


def insert_airports(cur):
    rows = []
    for code, name, city, country, tier in AIRPORTS:
        cap_min, cap_max = TIER_CAPACITY_RANGE[tier]
        rows.append((f"{name} ({code})", city, country, random.randint(cap_min, cap_max)))

    result = execute_values(
        cur,
        "INSERT INTO Airports (airport_name, city, country, traffic_capacity) VALUES %s RETURNING airport_id",
        rows,
        fetch=True
    )
    airport_ids = {AIRPORTS[i][0]: result[i][0] for i in range(len(AIRPORTS))}
    airport_tiers = {AIRPORTS[i][0]: AIRPORTS[i][4] for i in range(len(AIRPORTS))}
    return airport_ids, airport_tiers


def insert_passengers(cur, n=500):
    rows = []
    for _ in range(n):
        phone = "9" + "".join([str(random.randint(0, 9)) for _ in range(9)])
        passport = "P" + "".join([str(random.randint(0, 9)) for _ in range(8)])
        rows.append((
            fake.name()[:100],
            random.randint(18, 80),
            random.choice(["Male", "Female", "Other"]),
            phone,
            fake.email()[:100],
            passport
        ))
    result = execute_values(
        cur,
        "INSERT INTO Passengers (name, age, gender, phone, email, passport_number) VALUES %s RETURNING passenger_id",
        rows,
        fetch=True
    )
    return [r[0] for r in result]


def generate_weather_data(airport_ids, start_date, end_date):
    rows = []
    lookup = {}
    current = start_date
    while current <= end_date:
        for code, aid in airport_ids.items():
            condition = random.choices(WEATHER_CONDITIONS, weights=[45, 20, 15, 5, 10, 5], k=1)[0]
            wind = random.randint(5, 80)
            visibility = round(random.uniform(0.5, 10.0), 1)
            temp = round(random.uniform(-10, 40), 1)
            rows.append((aid, current.date(), condition, wind, visibility, temp))
            lookup[(aid, current.date())] = condition
        current += timedelta(days=1)
    return rows, lookup


def compute_delay(condition, hour, distance_km, origin_tier):
    base_delay = 0
    weather_delay = {"Clear": 0, "Cloudy": 2, "Rain": 10, "Fog": 20, "Storm": 45, "Snow": 35}
    base_delay += weather_delay.get(condition, 0)
    if hour in [7, 8, 17, 18, 19, 20]:
        base_delay += random.randint(5, 20)
    if distance_km > 6000:
        base_delay += random.randint(0, 15)

    # Hub congestion effect — busier airports have extra structural delay
    cmin, cmax = TIER_CONGESTION_DELAY[origin_tier]
    base_delay += random.randint(cmin, cmax)

    base_delay += random.randint(-5, 10)
    return max(0, base_delay)


def weighted_distinct_pair(codes, tiers):
    """Pick 2 distinct airport codes, weighted by hub tier (major airports picked far more often)."""
    weights = [TIER_SELECTION_WEIGHT[tiers[c]] for c in codes]
    origin = random.choices(codes, weights=weights, k=1)[0]
    while True:
        dest = random.choices(codes, weights=weights, k=1)[0]
        if dest != origin:
            return origin, dest


def generate_flight_rows(airport_ids, airport_tiers, weather_lookup, start_date, end_date, flights_per_day):
    codes = list(airport_ids.keys())
    rows = []
    current = start_date

    while current <= end_date:
        for _ in range(flights_per_day):
            origin_code, dest_code = weighted_distinct_pair(codes, airport_tiers)
            origin_id = airport_ids[origin_code]
            dest_id = airport_ids[dest_code]
            origin_tier = airport_tiers[origin_code]

            distance_km = random.randint(500, 14000)
            aircraft = random.choice(AIRCRAFT_TYPES)
            airline = random.choice(AIRLINES)

            dep_hour = random.randint(0, 23)
            scheduled_departure = current.replace(hour=dep_hour, minute=random.choice([0, 15, 30, 45]))
            flight_duration_hours = max(1, distance_km / 800)
            scheduled_arrival = scheduled_departure + timedelta(hours=flight_duration_hours)

            condition = weather_lookup.get((origin_id, current.date()), "Clear")
            delay = compute_delay(condition, dep_hour, distance_km, origin_tier)

            status = "cancelled" if random.random() < 0.01 else ("delayed" if delay > 15 else "on_time")

            actual_departure = scheduled_departure + timedelta(minutes=delay if status != "cancelled" else 0)
            actual_arrival = scheduled_arrival + timedelta(minutes=delay if status != "cancelled" else 0)

            rows.append((
                airline, origin_id, dest_id, scheduled_departure, scheduled_arrival,
                scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
                status, delay, aircraft, distance_km
            ))

        current += timedelta(days=1)

    return rows


def insert_flights_batch(cur, flight_rows, batch_size=1000):
    flight_ids = []
    query = """
        INSERT INTO Flights
        (airline, source_airport, destination_airport, departure_time, arrival_time,
         scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
         status, delay_minutes, aircraft_type, distance_km)
        VALUES %s RETURNING flight_id
    """
    for i in range(0, len(flight_rows), batch_size):
        chunk = flight_rows[i:i + batch_size]
        result = execute_values(cur, query, chunk, fetch=True)
        flight_ids.extend([r[0] for r in result])
        print(f"  Inserted flights {i + len(chunk)}/{len(flight_rows)}")
    return flight_ids


def generate_and_insert_bookings(cur, flight_ids, flight_rows, passenger_ids, batch_size=5000):
    rows = []
    for idx, flight_id in enumerate(flight_ids):
        flight_departure = flight_rows[idx][3]
        num_bookings = random.randint(0, 8)
        for _ in range(num_bookings):
            passenger_id = random.choice(passenger_ids)
            booking_hour = random.choices(range(24), weights=BOOKING_HOUR_WEIGHTS, k=1)[0]
            booking_day_offset = random.randint(1, 60)
            booking_datetime = (flight_departure - timedelta(days=booking_day_offset)).replace(
                hour=booking_hour, minute=random.randint(0, 59)
            )
            rows.append((passenger_id, flight_id, booking_datetime))

    query = "INSERT INTO Bookings (passenger_id, flight_id, booking_date) VALUES %s"
    for i in range(0, len(rows), batch_size):
        chunk = rows[i:i + batch_size]
        execute_values(cur, query, chunk)
        print(f"  Inserted bookings {i + len(chunk)}/{len(rows)}")

    return len(rows)


def main():
    conn = connect()
    cur = conn.cursor()

    print("Clearing old data...")
    clear_old_data(cur)
    conn.commit()

    print("Inserting airports (with hub-tier bias)...")
    airport_ids, airport_tiers = insert_airports(cur)
    conn.commit()

    print("Inserting passengers...")
    passenger_ids = insert_passengers(cur, n=500)
    conn.commit()

    print("Generating weather data in memory...")
    weather_rows, weather_lookup = generate_weather_data(airport_ids, START_DATE, END_DATE)
    print(f"Inserting {len(weather_rows)} weather records...")
    execute_values(
        cur,
        "INSERT INTO Weather (airport_id, date, condition, wind_speed_kmph, visibility_km, temperature_c) VALUES %s",
        weather_rows
    )
    conn.commit()

    print("Generating flight data in memory (hub-weighted)...")
    flight_rows = generate_flight_rows(airport_ids, airport_tiers, weather_lookup, START_DATE, END_DATE, FLIGHTS_PER_DAY)
    print(f"Inserting {len(flight_rows)} flights (batched)...")
    flight_ids = insert_flights_batch(cur, flight_rows)
    conn.commit()

    print("Generating and inserting bookings (batched)...")
    total_bookings = generate_and_insert_bookings(cur, flight_ids, flight_rows, passenger_ids)
    conn.commit()

    cur.close()
    conn.close()
    print(f"\nDone! Synthetic data generated successfully.")
    print(f"  Airports: {len(airport_ids)}")
    print(f"  Passengers: {len(passenger_ids)}")
    print(f"  Weather records: {len(weather_rows)}")
    print(f"  Flights: {len(flight_ids)}")
    print(f"  Bookings: {total_bookings}")


if __name__ == "__main__":
    main()