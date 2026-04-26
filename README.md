# ✈️ Smart Airport Management System

## 📌 Overview

The Smart Airport Management System is a database-driven project built using PostgreSQL and Python. It manages airport operations such as passengers, flights, airports, and bookings.

The project also includes analytical features to extract insights like frequent travelers, busiest routes, and peak booking hours.

---

## 🎯 Objectives

* Design a structured relational database
* Implement real-world relationships using foreign keys
* Perform data analysis using SQL
* Build a simple dashboard using Streamlit

---

## 🧱 Database Design

The system consists of the following tables:

* **Passengers** → Stores passenger details
* **Airports** → Stores airport information
* **Flights** → Stores flight details
* **Bookings** → Stores booking records

---

## 🔗 Relationships

* One passenger → many bookings
* One flight → many bookings
* Flights connect airports (source & destination)

---

## ⚙️ Features

### 🗄️ Database Features

* Normalized relational schema
* Primary key & foreign key constraints
* Data integrity

### 📊 Analytics Features

* Frequent travelers analysis
* Busiest routes detection
* Peak booking time analysis

### 💻 Application Features

* View passengers, flights, bookings
* Display analytics using Streamlit
* Simple dashboard interface

---

## 🛠️ Tech Stack

* PostgreSQL
* Python
* Streamlit
* Pandas
* Psycopg2

---

## 📸 Screenshots

(Add screenshots here)

Example:
![Dashboard](screenshots/dashboard.png)

---

## 🚀 How to Run

### 1️⃣ Setup Database

* Install PostgreSQL
* Create database: `airport_db`
* Run SQL file:

```bash
psql -U postgres -d airport_db -f sql/setup.sql
```

---

### 2️⃣ Install Dependencies

```bash
pip install streamlit psycopg2 pandas
```

---

### 3️⃣ Run Application

```bash
streamlit run app.py
```

---

## 📈 Sample Queries

### Frequent Travelers

```sql
SELECT p.name, COUNT(b.booking_id) AS total_trips
FROM Bookings b
JOIN Passengers p ON b.passenger_id = p.passenger_id
GROUP BY p.name
ORDER BY total_trips DESC;
```

---

## 🧠 Learning Outcomes

* Database design using SQL
* Writing complex queries using JOIN & GROUP BY
* Building a Python-based dashboard
* Integrating backend with frontend

---

## 🔮 Future Improvements

* Add filters and search functionality
* Improve UI design
* Deploy application online

---

## 👤 Author

Shreyas Baravkar
