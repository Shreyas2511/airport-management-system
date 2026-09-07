-- Add delay and timing columns to Flights
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS shceduled_departure TIMESTAMP;
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS actual_departure TIMESTAMP;
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS scheduled_arrival TIMESTAMP;
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS actual_arrival TIMESTAMP;
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS status VARCHAR(20) DEFAULT 'scheduled';
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS  delay_minutes INT DEFAULT  0;
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS  aircraft_type VARCHAR(50);
ALTER TABLE Flights ADD COLUMN  IF NOT EXISTS  distance_km INT;

--Add location/capacity info to Airports
ALTER TABLE Airports ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE Airports ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE Airports ADD COLUMN IF NOT EXISTS traffic_capacity INT ;

-- New Weather table
CREATE TABLE IF NOT EXISTS Weather (
      weather_id SERIAL PRIMARY KEY,
	  airport_db INT REFERENCES Airports (airport_db),
	  date DATE NOT NULL,
	  condition VARCHAR(50),
	  wind_speed_kmph INT,
	  visibility_km DECIMAL(4,1),
	  temperature_c DECIMAL(4,1)
);


SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'airports';


ALTER TABLE Airports ADD COLUMN IF NOT EXISTS traffic_capacity INT ;

CREATE TABLE IF NOT EXISTS Weather (
       weather_id SERIAL PRIMARY KEY,
	   airport_id INT REFERENCES Airports(airport_id),
	   date DATE NOT NULL,
	   condition VARCHAR(50),
	   wind_speed_kmph INT,
	   visibility_km DECIMAL(4,1),
	   temperature_c DECIMAL(4,1)
);


SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
SELECT column_name FROM information_schema.columns WHERE table_name ='airports';

