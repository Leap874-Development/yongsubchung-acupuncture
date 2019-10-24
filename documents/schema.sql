-- Specify index for each table, when necessary.


-- password is werkzeug hsh:
--    hsh = werkzeug.generate_password_hash("plain_text")
create table doctors (
       username varchar(255),     -- Required:
       password varchar(255)      -- Required:
);


-- Patient_fkey is from patient field.
--
create table new_visit (
	patient_fkey	VARCHAR(255),       -- Required:  Fkey
	doctor	VARCHAR(255),               -- Required:
	visit_date	DATE,               -- Auto
	temperature	DOUBLE,
	heart_rate	DOUBLE,
	blood_pressure_h	INTEGER,
	blood_pressure_l	INTEGER,
	chief_complaint	VARCHAR(255),
	location	VARCHAR(255),
	onset	VARCHAR(255),
	provocation	VARCHAR(255),
	palliation	VARCHAR(255),
	quality	VARCHAR(255),
	region	VARCHAR(255),
	severity	VARCHAR(255),
	frequency	VARCHAR(255),
	timing	VARCHAR(255),
	possible_cause	VARCHAR(255),
	remark	TEXT,
	present_illness         TEXT,
	tq_fever	VARCHAR(255),
	tq_perspiration	VARCHAR(255),
	tq_thirst	VARCHAR(255),
	tq_appetite	VARCHAR(255),
	tq_digestion	VARCHAR(255),
	tq_taste	VARCHAR(255),
	tq_bm	VARCHAR(255),
	exam_urine	VARCHAR(255),
	exam_sleep	VARCHAR(255),
	exam_pain	VARCHAR(255),
	exam_consciousness	VARCHAR(255),
	exam_energy_level	INTEGER,
	exam_stress_level	INTEGER,
	exam_pulse_l	VARCHAR(255),
	exam_pulse_r	VARCHAR(255),
	women_menarche	VARCHAR(255),
	women_menopause	VARCHAR(255),
	women_num_pregnant	VARCHAR(255),
	women_num_child	VARCHAR(255),
	women_miscarriage	VARCHAR(255),
	women_leukorrhea	VARCHAR(255),
	women_birth_control	VARCHAR(255),
	women_menstruation	text,
	tcm_diag_1	VARCHAR(255),
	tcm_diag_2	VARCHAR(255),
	tcm_diag_3	VARCHAR(255),
	tcm_diag_4	VARCHAR(50),
	treat_principle	text,
	acu_points	text,
	moxa	BOOLEAN,
	cupping	BOOLEAN,
	eacu	BOOLEAN,
	auricular	VARCHAR(255),
	condition_treated	VARCHAR(255),
	fee	DOUBLE,
	paid	BOOLEAN,
	paid_check_by  VARCHAR(255),       -- Doctor(username) who received the fee.
	note	TEXT
);
       

--
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
	create_date	DATE,      -- Auto
	suffix	    INTEGER,       -- Auto
	patient_key	VARCHAR(255) UNIQUE,      -- Required:
	last_name	VARCHAR(255),             -- Required:
	first_name	VARCHAR(255),             -- Required:
	gender          VARCHAR(1),               -- Required:
	dob	DATE,                             -- Required:	
	height	VARCHAR(255), 
	weight	VARCHAR(255),
	addr1   VARCHAR(255),
	addr2   VARCHAR(255),
	phone1  VARCHAR(255),
	phone2  VARCHAR(255),
	email   VARCHAR(255),
	medical_history	  TEXT,
	medications	TEXT,
	family_hx	TEXT,
	allergy		TEXT,
	note            TEXT,
	attachment	  TEXT       -- Just show:  It will be the URL for s3-object
);


create table visit (
	patient_fkey	VARCHAR(255),       -- Required: Fkey
	doctor	VARCHAR(255),               -- Required:
	visit_date	text,               -- Auto
	temperature	DOUBLE,
	heart_rate	DOUBLE,
	blood_pressure_h	INTEGER,
	blood_pressure_l	INTEGER,
	chief_complaint	VARCHAR(255),
	present_illeness	text,
	feedback	text,
	exam_appetite	VARCHAR(255),
	exam_digest	VARCHAR(255),
	exam_bm	VARCHAR(255),
	exam_sleep	VARCHAR(255),
	exam_tongue	VARCHAR(255),
	exam_pulse_l	VARCHAR(255),
	exam_pulse_r	VARCHAR(255),
	tcm_diag_1	VARCHAR(255),
	tcm_diag_2	VARCHAR(255),
	tcm_diag_3	VARCHAR(255),
	tcm_diag_4	VARCHAR(50),
	treat_principle	text,
	acu_points	text,
	moxa	BOOLEAN,
	cupping	BOOLEAN,
	eacu	BOOLEAN,
	auricular	VARCHAR(255),
	condition_treated	VARCHAR(255),
	fee	DOUBLE,
	paid	BOOLEAN,
	paid_check_by  VARCHAR(255),       -- Doctor(username) who received the fee.
	note	text
);
