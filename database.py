import sqlite3
import datetime

class DoctorExists(Exception): pass
class PatientNotFound(Exception): pass

class Database:
	def __init__(self, path, schema='schema.sql'):
		self.conn = sqlite3.connect(path)
		self.cur = self.conn.cursor()
		self.schema = open(schema, 'r').read()

		try: self.cur.executescript(self.schema)
		except sqlite3.OperationalError: pass
	
	def doctor_exists(self, username):
		query = 'SELECT COUNT(*) FROM doctors WHERE username=?'
		count = self.cur.execute(query, (username,)).fetchone()[0]
		return bool(count)

	# TODO: salt and hashing
	def doctor_add(self, username, password):
		if self.doctor_exists(username): raise DoctorExists()
		query = 'INSERT INTO doctors VALUES (?,?)'
		self.cur.execute(query, (username, password))
		self.conn.commit()

	# TODO: salt and hashing
	def doctor_check(self, username, password):
		query = 'SELECT COUNT(*) FROM doctors WHERE username=? AND password=?'
		count = self.cur.execute(query, (username, password)).fetchone()[0]
		return bool(count)
	
	# TODO: generate suffix
	def patient_add(self, patient_key, last_name, first_name, gender, dob,
					height=None, weight=None, addr1=None, addr2=None,
					phone1=None, phone2=None, email=None, medical_history=None,
					medications=None, family_hx=None, allergy=None, note=None,
					attachment=None):

		suffix = 'suffix'
		create_date = datetime.date.today()

		query = 'INSERT INTO patient VALUES (%s)' % ('?,' * 20)[:-1]
		self.cur.execute(query, (
			create_date, suffix, patient_key, last_name, first_name, gender,
			dob, height, weight, addr1, addr2, phone1, phone2, email,
			medical_history, medications, family_hx, allergy, note, attachment
		))
		self.conn.commit()
	
	def patient_exists(self, patient_key):
		query = 'SELECT COUNT(*) FROM patient WHERE patient_key=?'
		count = self.cur.execute(query, (patient_key,)).fetchone()[0]
		return bool(count)

	def patient_search(self, **kwargs):
		query = 'SELECT * FROM patient WHERE ' 
		query += ' AND '.join([ '%s=?' % a for a in kwargs ])
		values = [ kwargs[a] for a in kwargs ]
		resp = self.cur.execute(query, values)
		return resp

	def visit_add(self, patient_key, doctor, temperature=None,
				  heart_rate=None, blood_pressure_h=None, blood_pressure_l=None,
				  chief_complaint=None, present_illness=None, feedback=None,
				  exam_appetite=None, exam_digest=None, exam_bm=None,
				  exam_sleep=None, exam_tongue=None, exam_pulse_l=None,
				  exam_pulse_r=None, tcm_diag_1=None, tcm_diag_2=None,
				  tcm_diag_3=None, tcm_diag_4=None, treat_principle=None,
				  acu_points=None, moxa=None, cupping=None, eacu=None,
				  arricular=None, condition_treated=None, fee=None, paid=None, 
				  paid_check_by=None, note=None): 
		
		if not self.patient_exists(patient_key):
			raise PatientNotFound()
		
		visit_date = datetime.date.today()

		query = 'INSERT INTO visit VALUES (%s)' % ('?,' * 32)[:-1]
		self.cur.execute(query, (
			patient_key, doctor, visit_date, temperature, heart_rate,
			blood_pressure_h, blood_pressure_l, chief_complaint,
			present_illness, feedback, exam_appetite, exam_digest, exam_bm,
			exam_sleep, exam_tongue, exam_pulse_l, exam_pulse_r, tcm_diag_1,
			tcm_diag_2, tcm_diag_3, tcm_diag_4, treat_principle, acu_points,
			moxa, cupping, eacu, arricular, condition_treated, fee, paid,
			paid_check_by, note
		))
		self.conn.commit()
	
	def new_visit_add(self, patient_key, doctor, temperature=None,
					  heart_rate=None, blood_pressure_h=None,
					  blood_pressure_l=None, chief_complaint=None,
					  location=None, onset=None, provocation=None,
					  palliation=None, quality=None, region=None, severity=None,
					  frequency=None, timing=None, possible_cause=None,
					  remark=None, present_illness=None, tq_fever=None,
					  tq_perspiration=None, tq_thirst=None, tq_appetite=None,
					  tq_digestion=None, tq_taste=None, tq_bm=None,
					  exam_urine=None, exam_sleep=None, exam_pain=None,
					  exam_consciousness=None, exam_energy_level=None,
					  exam_stress_level=None, exam_pulse_l=None,
					  exam_pulse_r=None, women_menarche=None,
					  women_menopause=None, women_num_pregnant=None,
					  women_num_child=None, women_miscarriage=None,
					  women_leukorrhea=None, women_birth_control=None,
					  women_menstruation=None, tcm_diag_1=None, tcm_diag_2=None,
					  tcm_diag_3=None, tcm_diag_4=None, treat_principle=None,
					  acu_points=None, moxa=None, cupping=None, eacu=None,
					  auricular=None, condition_treated=None, fee=None,
					  paid=None, paid_check_by=None, note=None):

		if not self.patient_exists(patient_key):
			raise PatientNotFound()
		
		visit_date = datetime.date.today()

		query = 'INSERT INTO visit VALUES (%s)' % ('?,' * 58)[:-1]
		self.cur.execute(query, (
			patient_key, doctor, visit_date, temperature, heart_rate,
			blood_pressure_h, blood_pressure_l, chief_complaint, location,
			onset, provocation, palliation, quality, region, severity,
			frequency, timing, possible_cause, remark, present_illness,
			tq_fever, tq_perspiration, tq_thirst, tq_appetite, tq_digestion,
			tq_taste, tq_bm, exam_urine, exam_sleep, exam_pain,
			exam_consciousness, exam_energy_level, exam_stress_level,
			exam_pulse_l, exam_pulse_r, women_menarche, women_menopause,
			women_num_pregnant, women_num_child, women_miscarriage,
			women_leukorrhea, women_birth_control, women_menstruation,
			tcm_diag_1, tcm_diag_2, tcm_diag_3, tcm_diag_4, treat_principle,
			acu_points, moxa, cupping, auricular, condition_treated, fee, paid,
			paid_check_by, note
		))
		self.conn.commit()

db = Database('database.db')
db.visit_add('fff', 'doc', exam_tongue='tongue', note='COOL!', cupping=True)