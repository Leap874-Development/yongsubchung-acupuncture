import sqlite3

class Database:
	def __init__(self, path, schema='schema.sql'):
		self.conn = sqlite3.connect(path)
		self.cur = self.conn.cursor()
		self.schema = open(schema, 'r').read()

		try: self.cur.executescript(self.schema)
		except sqlite3.OperationalError: pass

class DatabaseObject:
	def __init__(self):
		pass

class Doctor(DatabaseObject):
	def __init__(self):
		DatabaseObject.__init__(self)

class NewVisit(DatabaseObject):
	def __init__(self):
		DatabaseObject.__init__(self)

class Visit(DatabaseObject):
	def __init__(self):
		DatabaseObject.__init__(self)

class Patient(DatabaseObject):
	def __init__(self):
		DatabaseObject.__init__(self)

db = Database('database.db')