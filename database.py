import sqlite3
import datetime

class DoctorExists(Exception): pass

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
	def patient_add(self, patient_key, last_name, first_name, gender,
					dob, height=None, weight=None, addr1=None, addr2=None,
					phone1=None, phone2=None, email=None, medical_history=None,
					medications=None, family_hx=None, allergy=None, note=None,
					attachment=None):

		suffix = 'suffix'
		create_date = datetime.date.today()

		query = 'INSERT INTO patient VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
		self.cur.execute(query, (
			create_date, suffix, patient_key, last_name, first_name, gender,
			dob, height, weight, addr1, addr2, phone1, phone2, email, medical_history,
			medications, family_hx, allergy, note, attachment
		))
		self.conn.commit()
	
	def patient_search(self, **kwargs):
		query = 'SELECT * FROM patient WHERE ' 
		query += ' AND '.join([ '%s=?' % a for a in kwargs ])
		values = [ kwargs[a] for a in kwargs ]
		resp = self.cur.execute(query, values)
		return resp
