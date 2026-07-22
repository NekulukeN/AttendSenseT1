--
-- PostgreSQL database dump
--

\restrict GeBFd4RhshupUgINtERdRy8F6COYH5nnAFAnweDuSSi8bKwsCPOJdH3ighWr7N2

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

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

--
-- Name: attendancestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.attendancestatus AS ENUM (
    'present',
    'late',
    'absent'
);


ALTER TYPE public.attendancestatus OWNER TO postgres;

--
-- Name: sessionstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sessionstatus AS ENUM (
    'active',
    'ended'
);


ALTER TYPE public.sessionstatus OWNER TO postgres;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'student',
    'lecturer',
    'admin'
);


ALTER TYPE public.userrole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anomaly_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anomaly_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer NOT NULL,
    reason character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.anomaly_logs OWNER TO postgres;

--
-- Name: anomaly_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.anomaly_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.anomaly_logs_id_seq OWNER TO postgres;

--
-- Name: anomaly_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.anomaly_logs_id_seq OWNED BY public.anomaly_logs.id;


--
-- Name: attendance_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer NOT NULL,
    check_in_time timestamp with time zone DEFAULT now(),
    check_out_time timestamp with time zone,
    status public.attendancestatus
);


ALTER TABLE public.attendance_logs OWNER TO postgres;

--
-- Name: attendance_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_logs_id_seq OWNER TO postgres;

--
-- Name: attendance_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_logs_id_seq OWNED BY public.attendance_logs.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    actor_id integer,
    action character varying NOT NULL,
    detail character varying,
    "timestamp" timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: face_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.face_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    embedding text NOT NULL,
    image_path character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.face_profiles OWNER TO postgres;

--
-- Name: face_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.face_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.face_profiles_id_seq OWNER TO postgres;

--
-- Name: face_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.face_profiles_id_seq OWNED BY public.face_profiles.id;


--
-- Name: probe_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.probe_results (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer NOT NULL,
    probe_type character varying NOT NULL,
    status character varying,
    sent_time timestamp with time zone DEFAULT now(),
    response_time timestamp with time zone,
    passed boolean
);


ALTER TABLE public.probe_results OWNER TO postgres;

--
-- Name: probe_results_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.probe_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.probe_results_id_seq OWNER TO postgres;

--
-- Name: probe_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.probe_results_id_seq OWNED BY public.probe_results.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    class_name character varying NOT NULL,
    lecturer_id integer,
    start_time timestamp with time zone DEFAULT now(),
    end_time timestamp with time zone,
    status public.sessionstatus
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sessions_id_seq OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    student_id character varying,
    full_name character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    role character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: anomaly_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_logs ALTER COLUMN id SET DEFAULT nextval('public.anomaly_logs_id_seq'::regclass);


--
-- Name: attendance_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_logs ALTER COLUMN id SET DEFAULT nextval('public.attendance_logs_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: face_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.face_profiles ALTER COLUMN id SET DEFAULT nextval('public.face_profiles_id_seq'::regclass);


--
-- Name: probe_results id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probe_results ALTER COLUMN id SET DEFAULT nextval('public.probe_results_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: anomaly_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anomaly_logs (id, user_id, session_id, reason, created_at) FROM stdin;
\.


--
-- Data for Name: attendance_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance_logs (id, user_id, session_id, check_in_time, check_out_time, status) FROM stdin;
1	1	1	2026-06-09 11:51:26.493094+08	\N	present
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, actor_id, action, detail, "timestamp") FROM stdin;
1	6	USER_REGISTERED	aden@attendsense.com registered.	2026-06-25 10:52:20.192876+08
2	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 10:58:02.118082+08
3	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 10:58:09.420591+08
4	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 10:58:20.415364+08
5	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 10:59:48.783403+08
6	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 11:04:38.083608+08
7	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 11:09:42.256906+08
8	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 11:10:31.222574+08
9	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 11:20:36.847871+08
10	6	USER_LOGIN	aden@attendsense.com logged in.	2026-06-25 11:27:26.762266+08
\.


--
-- Data for Name: face_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.face_profiles (id, user_id, embedding, image_path, created_at) FROM stdin;
1	1	[-0.14371229708194733, -0.3762493431568146, 0.01361161470413208, -0.8833783268928528, 0.5339681506156921, 0.08393722772598267, -0.32597753405570984, -0.11090342700481415, 0.08642113208770752, 0.06699183583259583, 0.35156241059303284, 0.0023624682798981667, -0.5655336380004883, -0.24076497554779053, 0.44964396953582764, -0.13985943794250488, -0.6293716430664062, 0.11778637766838074, 0.055516742169857025, -0.5724308490753174, -0.5141969919204712, 0.01246810331940651, 0.38620230555534363, 0.8461452722549438, 0.8018860220909119, 0.03308990225195885, 0.060649462044239044, 0.5627087354660034, -0.2551223635673523, -0.3416725695133209, -0.34103959798812866, 0.21179549396038055, -0.3412131667137146, -0.21471524238586426, 0.13052617013454437, 0.6016952395439148, -0.2837817072868347, 0.6557837724685669, 1.239607572555542, -0.5473377704620361, 0.14961083233356476, -0.1825098991394043, -0.3757762312889099, 0.08650639653205872, -0.09216424077749252, -0.18984824419021606, 0.033070724457502365, -1.1830902099609375, -0.3325551152229309, 0.50929194688797, -0.7879782915115356, 0.677202045917511, 0.7958836555480957, -0.9624679088592529, -0.05036896839737892, 0.7959972620010376, 0.21394644677639008, -0.18709172308444977, -0.13011732697486877, 0.24179917573928833, 0.7226194143295288, -0.1817324459552765, -0.569939374923706, -0.45478948950767517, 0.19903424382209778, 0.5755648612976074, 0.2608981430530548, 0.21943268179893494, 0.04614774137735367, 0.4478197395801544, -0.18319593369960785, 0.06287574768066406, -0.4980809688568115, -1.0637235641479492, 0.4745807349681854, -0.3218752145767212, -0.8685067892074585, -0.1875813752412796, -0.7618695497512817, 0.5074647068977356, 0.23757582902908325, -0.23344185948371887, 0.5652351975440979, 1.011362910270691, 0.288051575422287, 0.6705519556999207, 0.4336825907230377, 0.4605554938316345, 0.12101341784000397, -0.39274802803993225, 0.6302970051765442, -0.7559680342674255, -0.8129997849464417, -0.17883053421974182, 0.7014673352241516, 0.10649771243333817, -0.9962526559829712, -1.066659927368164, -0.5748809576034546, -0.013062860816717148, -0.4426118731498718, 0.3327324688434601, -0.2845611572265625, -1.2016805410385132, 0.021223261952400208, -0.41589272022247314, 0.23950204253196716, -0.3676912784576416, 0.7118587493896484, 0.1557401418685913, -0.02687811106443405, 0.28187495470046997, 0.1355457305908203, 0.26732850074768066, 0.37023720145225525, 0.09559591114521027, -0.23866526782512665, 0.6852778196334839, 0.09020660817623138, 0.3977516293525696, 0.31802862882614136, 0.19142954051494598, 0.96607506275177, -0.21001063287258148, 0.47267335653305054, -1.2109755277633667, 0.7219758033752441, 0.09357991814613342]	uploads/faces/user_1.jpg	2026-06-09 11:43:30.369095+08
2	6	[-0.09149874746799469, -0.3745187819004059, -0.11387749761343002, -0.495307058095932, 0.36941078305244446, 0.05108710378408432, 0.12452031672000885, -0.12683705985546112, -0.09355882555246353, -0.014546631835401058, 0.46466243267059326, -0.11562050879001617, 0.11334444582462311, -0.5959886312484741, 0.10944442451000214, 0.3249890208244324, 0.4886954426765442, -0.3633183240890503, 0.2658863663673401, -0.38521432876586914, -0.11857731640338898, 0.0742606669664383, -0.3935847580432892, -0.1324366331100464, -0.04901735112071037, -0.28268682956695557, 0.5072183609008789, 0.3507813513278961, -0.31988394260406494, -0.17202149331569672, -0.1442287117242813, 0.23897682130336761, 0.2112780213356018, -0.28191396594047546, 0.5577822327613831, -0.1752421259880066, 0.31188100576400757, -0.11682990938425064, 0.45075175166130066, -0.15137337148189545, 0.26976293325424194, 0.08722742646932602, -0.23837295174598694, -0.18455538153648376, -0.2680583894252777, -0.7409109473228455, 0.14444057643413544, -0.08197387307882309, 0.305339515209198, 0.2640897035598755, -0.4331148862838745, 0.2229211926460266, 0.16414101421833038, -0.313862681388855, 0.01435807067900896, 0.39273157715797424, 0.4503595530986786, 0.29672449827194214, -0.10890455543994904, -0.9147451519966125, -0.29252731800079346, -0.2532835006713867, 0.064734548330307, 0.9619240164756775, 0.07427795231342316, 0.5467121005058289, 0.37204065918922424, 0.042425546795129776, 0.17141500115394592, -0.3005414307117462, -0.19900654256343842, -0.6120847463607788, 0.08403008431196213, -0.4609086513519287, -0.1189212054014206, -0.14049509167671204, -0.17244543135166168, 0.28337562084198, -0.28529930114746094, -0.4220935106277466, -0.4800686240196228, -0.20592950284481049, -0.06687761843204498, 0.22787398099899292, 0.5174563527107239, -0.1798468679189682, 0.6113015413284302, -0.19248609244823456, -0.7426043748855591, 0.6421824097633362, 0.10191008448600769, 0.0429648831486702, -0.1791519671678543, -0.24331924319267273, 0.3796498477458954, 0.04714130610227585, -9.282771497964859e-05, -0.6511948108673096, -0.6378052234649658, 0.2761821448802948, -0.5213354229927063, 0.7390761375427246, 0.24647186696529388, -0.25688090920448303, 0.2220078408718109, 0.3681669235229492, 0.04160104691982269, -0.10749059915542603, -0.05549466609954834, -0.35176903009414673, 0.053874529898166656, 0.30607205629348755, 0.4697815477848053, 0.4421730637550354, -0.1728483885526657, 0.23139408230781555, 0.030845213681459427, 0.45758453011512756, 0.32244932651519775, 0.09439435601234436, -0.32650041580200195, -0.014815907925367355, 0.5494968891143799, 0.29680418968200684, 0.5948153734207153, -0.5544729828834534, 0.21740011870861053, 0.13780494034290314]	uploads/faces/user_6.jpg	2026-06-25 11:28:07.865928+08
\.


--
-- Data for Name: probe_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.probe_results (id, user_id, session_id, probe_type, status, sent_time, response_time, passed) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (id, class_name, lecturer_id, start_time, end_time, status) FROM stdin;
1	Web Technology	1	2026-06-09 11:51:03.660148+08	\N	active
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, student_id, full_name, email, password_hash, role, created_at) FROM stdin;
1	S12345	Ahmad Razif	ahmad@university.edu.my	$2b$12$.IEoxpGbzQrR.v21dUsruO1VkXgaXTD3CL63yXlGj4eXxecQqEXZa	student	2026-06-09 10:54:05.249933+08
5	\N	Admin	admin@attendsense.com	$2b$12$U6F1x5bRtvO4YK1oqxW1aO8U1DldFeIq1xl/yzqnZFGBLSVMwPu16	admin	2026-06-10 10:57:55.732963+08
6	22076921	Aden Luke Ng	aden@attendsense.com	$2b$12$NDcpjv3PD2K.FzRzm/FZ4ej2abuKuf10wMGx21kzIj40xh0sErMaS	admin	2026-06-25 10:52:19.843169+08
\.


--
-- Name: anomaly_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.anomaly_logs_id_seq', 1, false);


--
-- Name: attendance_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_logs_id_seq', 1, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 10, true);


--
-- Name: face_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.face_profiles_id_seq', 2, true);


--
-- Name: probe_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.probe_results_id_seq', 1, false);


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sessions_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: anomaly_logs anomaly_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_logs
    ADD CONSTRAINT anomaly_logs_pkey PRIMARY KEY (id);


--
-- Name: attendance_logs attendance_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_logs
    ADD CONSTRAINT attendance_logs_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: face_profiles face_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.face_profiles
    ADD CONSTRAINT face_profiles_pkey PRIMARY KEY (id);


--
-- Name: face_profiles face_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.face_profiles
    ADD CONSTRAINT face_profiles_user_id_key UNIQUE (user_id);


--
-- Name: probe_results probe_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probe_results
    ADD CONSTRAINT probe_results_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_student_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_student_id_key UNIQUE (student_id);


--
-- Name: ix_anomaly_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_anomaly_logs_id ON public.anomaly_logs USING btree (id);


--
-- Name: ix_attendance_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_logs_id ON public.attendance_logs USING btree (id);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_face_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_face_profiles_id ON public.face_profiles USING btree (id);


--
-- Name: ix_probe_results_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_probe_results_id ON public.probe_results USING btree (id);


--
-- Name: ix_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_id ON public.sessions USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: anomaly_logs anomaly_logs_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_logs
    ADD CONSTRAINT anomaly_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: anomaly_logs anomaly_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anomaly_logs
    ADD CONSTRAINT anomaly_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: attendance_logs attendance_logs_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_logs
    ADD CONSTRAINT attendance_logs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: attendance_logs attendance_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_logs
    ADD CONSTRAINT attendance_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: audit_logs audit_logs_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id);


--
-- Name: face_profiles face_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.face_profiles
    ADD CONSTRAINT face_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: probe_results probe_results_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probe_results
    ADD CONSTRAINT probe_results_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: probe_results probe_results_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probe_results
    ADD CONSTRAINT probe_results_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sessions sessions_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict GeBFd4RhshupUgINtERdRy8F6COYH5nnAFAnweDuSSi8bKwsCPOJdH3ighWr7N2

