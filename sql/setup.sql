--
-- PostgreSQL database dump
--

\restrict R1ME4CZwheLDZFeGg3wX4qTnXXKPyQwtSBfcDZ5hGYdxHcJ51Ho3wo2I0yXXTHu

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-04-23 12:19:11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 16459)
-- Name: airports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.airports (
    airport_id integer NOT NULL,
    airport_name character varying(100),
    city character varying(50),
    country character varying(50)
);


ALTER TABLE public.airports OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16458)
-- Name: airports_airport_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.airports_airport_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.airports_airport_id_seq OWNER TO postgres;

--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 221
-- Name: airports_airport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.airports_airport_id_seq OWNED BY public.airports.airport_id;


--
-- TOC entry 226 (class 1259 OID 16493)
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    booking_id integer NOT NULL,
    passenger_id integer,
    flight_id integer,
    booking_date timestamp without time zone
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16492)
-- Name: bookings_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bookings_booking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bookings_booking_id_seq OWNER TO postgres;

--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 225
-- Name: bookings_booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bookings_booking_id_seq OWNED BY public.bookings.booking_id;


--
-- TOC entry 224 (class 1259 OID 16467)
-- Name: flights; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flights (
    flight_id integer NOT NULL,
    airline character varying(50),
    source_airport integer,
    destination_airport integer,
    departure_time timestamp without time zone,
    arrival_time timestamp without time zone
);


ALTER TABLE public.flights OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16466)
-- Name: flights_flight_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flights_flight_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flights_flight_id_seq OWNER TO postgres;

--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 223
-- Name: flights_flight_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flights_flight_id_seq OWNED BY public.flights.flight_id;


--
-- TOC entry 220 (class 1259 OID 16449)
-- Name: passengers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passengers (
    passenger_id integer NOT NULL,
    name character varying(100),
    age integer,
    gender character varying(10),
    phone character varying(12),
    email character varying(100),
    passport_number character varying(20)
);


ALTER TABLE public.passengers OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16448)
-- Name: passengers_passenger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.passengers_passenger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.passengers_passenger_id_seq OWNER TO postgres;

--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 219
-- Name: passengers_passenger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.passengers_passenger_id_seq OWNED BY public.passengers.passenger_id;


--
-- TOC entry 4872 (class 2604 OID 16462)
-- Name: airports airport_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.airports ALTER COLUMN airport_id SET DEFAULT nextval('public.airports_airport_id_seq'::regclass);


--
-- TOC entry 4874 (class 2604 OID 16496)
-- Name: bookings booking_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings ALTER COLUMN booking_id SET DEFAULT nextval('public.bookings_booking_id_seq'::regclass);


--
-- TOC entry 4873 (class 2604 OID 16470)
-- Name: flights flight_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights ALTER COLUMN flight_id SET DEFAULT nextval('public.flights_flight_id_seq'::regclass);


--
-- TOC entry 4871 (class 2604 OID 16452)
-- Name: passengers passenger_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passengers ALTER COLUMN passenger_id SET DEFAULT nextval('public.passengers_passenger_id_seq'::regclass);


--
-- TOC entry 5039 (class 0 OID 16459)
-- Dependencies: 222
-- Data for Name: airports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.airports (airport_id, airport_name, city, country) FROM stdin;
1	Chhatrapti Shivaji International Airport	Mumbai	India
2	Indira Gnadhi International Airport	Delhi	India
3	Kempegowda International Airport 	Banglore	India
4	Dubai International Airport	Dubai	UAE
5	Chhatrapti Shivaji International Airport	Mumbai	India
6	Indira Gnadhi International Airport	Delhi	India
7	Kempegowda International Airport 	Banglore	India
8	Dubai International Airport	Dubai	UAE
9	Heathrow Airport	London	Uk
10	John F Kennedy International Airport	New York	USA
11	Changi Airport	Singapore	Singapore
12	Frankfurt Airport	Frankfurt	Germany
13	Charles de Gaulle Airport	Paris	France
14	Sydney Airport	Sydeny	Australia
15	Toronto Pearson Airport	Toronto	Canada
16	Haneda Airport	Tokyo	Japan
17	Los Angeles International Airport	Los Angeles	USA
18	Doha Hamad International Airport	Doha	Qatar
\.


--
-- TOC entry 5043 (class 0 OID 16493)
-- Dependencies: 226
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bookings (booking_id, passenger_id, flight_id, booking_date) FROM stdin;
1	1	1	2026-04-20 09:00:00
2	2	2	2026-04-21 10:30:00
3	3	3	2026-04-22 11:15:00
4	3	8	2026-04-20 00:38:01.967985
5	3	8	2026-04-17 23:24:17.109137
6	3	8	2026-04-15 10:20:58.502335
7	3	8	2026-04-17 05:13:49.096258
8	3	8	2026-04-20 10:23:50.252703
9	3	8	2026-04-20 16:17:32.054105
10	3	8	2026-04-22 13:15:38.56777
11	3	8	2026-04-20 01:02:32.016015
12	3	8	2026-04-19 21:10:00.481485
13	3	8	2026-04-14 01:56:54.95382
14	3	8	2026-04-16 09:43:55.246241
15	3	8	2026-04-13 13:46:23.781408
16	3	8	2026-04-20 15:33:45.144822
17	3	8	2026-04-14 23:24:17.979769
18	3	8	2026-04-13 15:30:39.508213
19	3	8	2026-04-18 21:22:15.803883
20	3	8	2026-04-15 02:15:13.862872
21	3	8	2026-04-14 02:45:32.18704
22	3	8	2026-04-16 19:08:30.639152
23	3	8	2026-04-20 15:34:01.77751
24	3	8	2026-04-16 06:18:11.10004
25	3	8	2026-04-21 03:33:50.590778
26	3	8	2026-04-19 22:51:00.019014
27	3	8	2026-04-21 11:15:31.843467
28	3	8	2026-04-20 20:05:36.68028
29	3	8	2026-04-13 07:52:07.349787
30	3	8	2026-04-13 08:46:39.630544
31	3	8	2026-04-20 13:54:17.184975
32	3	8	2026-04-15 20:27:17.807726
33	3	8	2026-04-13 21:58:25.289575
\.


--
-- TOC entry 5041 (class 0 OID 16467)
-- Dependencies: 224
-- Data for Name: flights; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flights (flight_id, airline, source_airport, destination_airport, departure_time, arrival_time) FROM stdin;
1	Indigo	1	2	2026-04-25 10:00:00	2026-04-25 12:00:00
2	Air India	2	4	2026-04-25 14:00:00	2026-04-25 18:00:00
3	Emirates	4	1	2026-04-26 09:00:00	2026-04-26 13:00:00
4	Qatar Airways	16	2	2026-04-29 05:05:10.150646	2026-04-26 14:06:16.656056
5	Emirates	16	2	2026-04-27 08:46:50.605469	2026-04-23 12:21:32.142196
6	Air India	16	2	2026-04-23 20:24:18.179937	2026-04-23 10:16:21.089098
7	Air India	16	2	2026-04-30 01:42:25.350826	2026-04-23 22:25:35.405627
8	Air India	16	2	2026-04-24 08:54:13.554303	2026-05-01 12:21:07.57924
9	Qatar Airways	16	2	2026-04-29 04:23:33.602508	2026-04-30 22:49:20.229055
10	Indigo	16	2	2026-04-29 01:00:39.012712	2026-04-24 16:13:13.467391
11	Air India	16	2	2026-05-02 12:55:16.088424	2026-05-02 00:28:53.79841
12	Air India	16	2	2026-04-24 00:14:29.913755	2026-05-03 02:21:02.706123
13	Indigo	16	2	2026-04-28 13:19:36.860273	2026-05-01 05:17:47.86435
14	Air India	16	2	2026-04-28 04:15:39.286348	2026-04-30 09:20:27.425137
15	Indigo	16	2	2026-04-23 19:31:04.042238	2026-04-29 02:31:03.462719
16	Indigo	16	2	2026-04-25 08:58:18.574641	2026-04-25 18:51:07.49953
17	Indigo	16	2	2026-04-25 02:47:13.739297	2026-04-23 23:32:56.210487
18	Emirates	16	2	2026-05-02 00:47:20.937752	2026-04-24 22:00:44.713943
19	Qatar Airways	16	2	2026-04-27 08:52:16.093989	2026-04-26 15:33:23.889023
20	Emirates	16	2	2026-04-25 03:50:28.526645	2026-04-24 07:32:57.243491
21	Qatar Airways	16	2	2026-05-01 00:34:23.884439	2026-04-30 14:49:44.815508
22	Indigo	16	2	2026-04-30 23:57:51.641886	2026-04-26 12:53:24.928002
23	Indigo	16	2	2026-04-26 22:26:09.857418	2026-05-01 07:17:01.85556
\.


--
-- TOC entry 5037 (class 0 OID 16449)
-- Dependencies: 220
-- Data for Name: passengers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passengers (passenger_id, name, age, gender, phone, email, passport_number) FROM stdin;
1	Rahul Sharma	28	Male	123456	rahulsharma@gmail.com	PSPID001
2	Priya Mehta	24	Female	346789	priyamehta@gmail.com	PSPID002
3	Amit Verma	35	Male	876543	amitverma@gmail.com	PSPID003
\.


--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 221
-- Name: airports_airport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.airports_airport_id_seq', 18, true);


--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 225
-- Name: bookings_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bookings_booking_id_seq', 33, true);


--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 223
-- Name: flights_flight_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flights_flight_id_seq', 23, true);


--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 219
-- Name: passengers_passenger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.passengers_passenger_id_seq', 3, true);


--
-- TOC entry 4880 (class 2606 OID 16465)
-- Name: airports airports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.airports
    ADD CONSTRAINT airports_pkey PRIMARY KEY (airport_id);


--
-- TOC entry 4884 (class 2606 OID 16499)
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (booking_id);


--
-- TOC entry 4882 (class 2606 OID 16473)
-- Name: flights flights_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights
    ADD CONSTRAINT flights_pkey PRIMARY KEY (flight_id);


--
-- TOC entry 4876 (class 2606 OID 16457)
-- Name: passengers passengers_passport_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passengers
    ADD CONSTRAINT passengers_passport_number_key UNIQUE (passport_number);


--
-- TOC entry 4878 (class 2606 OID 16455)
-- Name: passengers passengers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passengers
    ADD CONSTRAINT passengers_pkey PRIMARY KEY (passenger_id);


--
-- TOC entry 4887 (class 2606 OID 16505)
-- Name: bookings bookings_flight_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_flight_id_fkey FOREIGN KEY (flight_id) REFERENCES public.flights(flight_id);


--
-- TOC entry 4888 (class 2606 OID 16500)
-- Name: bookings bookings_passenger_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_passenger_id_fkey FOREIGN KEY (passenger_id) REFERENCES public.passengers(passenger_id);


--
-- TOC entry 4885 (class 2606 OID 16479)
-- Name: flights flights_destination_airport_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights
    ADD CONSTRAINT flights_destination_airport_fkey FOREIGN KEY (destination_airport) REFERENCES public.airports(airport_id);


--
-- TOC entry 4886 (class 2606 OID 16474)
-- Name: flights flights_source_airport_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights
    ADD CONSTRAINT flights_source_airport_fkey FOREIGN KEY (source_airport) REFERENCES public.airports(airport_id);


-- Completed on 2026-04-23 12:19:11

--
-- PostgreSQL database dump complete
--

\unrestrict R1ME4CZwheLDZFeGg3wX4qTnXXKPyQwtSBfcDZ5hGYdxHcJ51Ho3wo2I0yXXTHu

