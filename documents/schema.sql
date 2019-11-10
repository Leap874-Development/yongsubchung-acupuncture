create table doctors (
	username TEXT NOT NULL,
	password TEXT NOT NULL		-- Auto: werkzeug hash
);

--  patient_key format : LYYMMDD[S+]
--    For example, C1910051
--        Lastname: Chung
--        Date: 2019-10-05
--        Suffix: 1
--    Another example, C19100123
--        Lastname: Chung
--        Date: 2019-10-01
--        Suffix: 23
--
create table patient (
	create_date		DATE NOT NULL,			-- Auto
	suffix			INTEGER NOT NULL,		-- Auto
	patient_pkey	TEXT NOT NULL UNIQUE,	-- Auto
	last_name		TEXT NOT NULL,
	first_name		TEXT NOT NULL,
	gender			TEXT NOT NULL,
	dob				DATE NOT NULL,
	height			TEXT, 
	weight			TEXT,
	addr1			TEXT,
	addr2			TEXT,
	phone1			TEXT,
	phone2			TEXT,
	email			TEXT,
	medical_history	TEXT,
	medications		TEXT,
	family_hx		TEXT,
	allergy			TEXT,
	note			TEXT,
	attachment		TEXT       -- URL for s3-object
);

create table visit (
	-- BOTH TYPES
	visit_fkey			TEXT NOT NULL UNIQUE,	-- Auto
	suffix				INTEGER NOT NULL,		-- Auto
	new_visit			BOOLEAN NOT NULL,
	patient_pkey		TEXT NOT NULL,
	doctor				TEXT NOT NULL,
	visit_date			DATE NOT NULL,			-- Auto
	temperature			REAL,
	heart_rate			REAL,
	blood_pressure_h	INTEGER,
	blood_pressure_l	INTEGER,
	chief_complaint		TEXT,
	present_illness		TEXT,
	exam_pulse_l		TEXT,
	exam_pulse_r		TEXT,
	exam_sleep			TEXT,
	exam_tongue			TEXT,
	tcm_diag_1			TEXT,
	tcm_diag_2			TEXT,
	tcm_diag_3			TEXT,
	tcm_diag_4			TEXT,
	treat_principle		TEXT,
	acu_points			TEXT,
	moxa				BOOLEAN,
	cupping				BOOLEAN,
	eacu				BOOLEAN,
	auricular			TEXT,
	condition_treated	TEXT,
	fee					REAL,
	paid				BOOLEAN,
	paid_check_by		TEXT, 		-- Doctor(username) who received the fee.
	note				TEXT

	-- VISIT ONLY
	feedback			TEXT,
	exam_appetite		TEXT,
	exam_digest			TEXT,
	exam_bm				TEXT,

	-- NEW VISIT ONLY
	location			TEXT,
	onset				TEXT,
	provocation			TEXT,
	palliation			TEXT,
	quality				TEXT,
	region				TEXT,
	severity			TEXT,
	frequency			TEXT,
	timing 				TEXT,
	possible_cause		TEXT,
	remark				TEXT,
	tq_fever			TEXT,
	tq_perspiration		TEXT,
	tq_thirst			TEXT,
	tq_appetite			TEXT,
	tq_digestion		TEXT,
	tq_taste			TEXT,
	tq_bm				TEXT,
	exam_urine			TEXT,
	exam_pain 			TEXT,
	exam_consciousness	TEXT,
	exam_energy_level	INTEGER,
	exam_stress_level	INTEGER,
	women_menarche		TEXT,
	women_menopause		TEXT,
	women_num_pregnant	TEXT,
	women_num_child		TEXT,
	women_miscarriage	TEXT,
	women_leukorrhea	TEXT,
	women_birth_control	TEXT,
	women_menstruation	TEXT
);



-- 0  create_date
-- 1  suffix
-- 2  patient_key
-- 3  last_name
-- 4  first_name
-- 5  gender
-- 6  dob
-- 7  height
-- 8  weight
-- 9  addr1
-- 10 addr2
-- 11 phone1
-- 12 phone2
-- 13 email
-- 14 medical_history
-- 15 medications
-- 16 family_hx
-- 17 allergy
-- 18 note
-- 19 attachment
