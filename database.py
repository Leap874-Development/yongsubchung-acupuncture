import sqlite3

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
		resp = self.cur.execute(query, (username,)).fetchone()[0]
		return bool(count)

	def doctor_add(self, username, password):
		if self.doctor_exists(username): raise DoctorExists()
		query = 'INSERT INTO doctors VALUES (?,?)'
		self.cur.execute(query, (username, password))
		self.conn.commit()

	def doctor_check(self, username, password):
		query = 'SELECT COUNT(*) FROM doctors WHERE username=? AND password=?'
		count = self.cur.execute(query, (username, password)).fetchone()[0]
		return bool(count)

db = Database('database.db')
db.add_doctor('test', 'password')
print(db.check_doctor('test', 'passworsd'))
db.test()