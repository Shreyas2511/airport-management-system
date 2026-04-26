Database Schema

Tables

Passengers

- passenger_id (Primary Key)
- name
- age
- gender
- phone
- email
- passport_number

Airports

- airport_id (Primary Key)
- airport_name
- city
- country

Flights

- flight_id (Primary Key)
- airline
- source_airport (Foreign Key)
- destination_airport (Foreign Key)
- departure_time
- arrival_time

Bookings

- booking_id (Primary Key)
- passenger_id (Foreign Key)
- flight_id (Foreign Key)
- booking_date

Relationships

- One passenger → many bookings
- One flight → many bookings
- Airports → linked to flights