--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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
-- Name: event_logs; Type: TABLE; Schema: public; Owner: coreuser
--

CREATE TABLE public.event_logs (
    id integer NOT NULL,
    location character varying(100),
    event_type character varying(100),
    details text,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.event_logs OWNER TO coreuser;

--
-- Name: event_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: coreuser
--

CREATE SEQUENCE public.event_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_logs_id_seq OWNER TO coreuser;

--
-- Name: event_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: coreuser
--

ALTER SEQUENCE public.event_logs_id_seq OWNED BY public.event_logs.id;


--
-- Name: event_logs id; Type: DEFAULT; Schema: public; Owner: coreuser
--

ALTER TABLE ONLY public.event_logs ALTER COLUMN id SET DEFAULT nextval('public.event_logs_id_seq'::regclass);


--
-- Data for Name: event_logs; Type: TABLE DATA; Schema: public; Owner: coreuser
--

COPY public.event_logs (id, location, event_type, details, date) FROM stdin;
\.


--
-- Name: event_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: coreuser
--

SELECT pg_catalog.setval('public.event_logs_id_seq', 1, false);


--
-- Name: event_logs event_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: coreuser
--

ALTER TABLE ONLY public.event_logs
    ADD CONSTRAINT event_logs_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

