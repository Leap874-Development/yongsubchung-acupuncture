from werkzeug import security
import sqlite3
import datetime

class DoctorExists(Exception): pass
class PatientNotFound(Exception): pass
class InvalidColumn(Exception): pass

def with_database(func):
    def wrapped(self, *args, **kwargs):
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        resp = func(self, cur, *args, **kwargs)
        conn.commit()
        conn.close()
        return resp
    return wrapped


class Database:
    def __init__(self, path, schema='documents/schema.sql', debug=False):
        self.path = path
        self.schema = open(schema, 'r').read()
        self.debug = debug
 
        self.patient_columns = ['last_name', 'first_name', 'gender', 'dob',
            'height', 'weight', 'addr1', 'addr2', 'phone1', 'phone2', 'email',
            'medical_history', 'medications', 'family_hx', 'allergy', 'note',
            'attachment', 'patient_key', 'suffix', 'create_date']

        conn = sqlite3.connect(path)
        cur = conn.cursor()

        try: cur.executescript(self.schema)
        except sqlite3.OperationalError: pass

        conn.commit()
        conn.close()
    
    @with_database
    def doctor_exists(self, cur, username):
        if self.debug and username == 'admin': return True # debug login

        query = 'SELECT COUNT(*) FROM doctors WHERE username=?'
        count = cur.execute(query, (username,)).fetchone()[0]
        return bool(count)

    @with_database
    def doctor_add(self, cur, username, password):
        if self.doctor_exists(username): raise DoctorExists()
        hashed = security.generate_password_hash(password)
        query = 'INSERT INTO doctors VALUES (?,?)'
        cur.execute(query, (username, hashed))

    @with_database
    def doctor_check(self, cur, username, password):
        if self.debug and username == 'admin' and password == 'password': return True # debug login
        elif self.debug and username == 'admin': return False

        if not self.doctor_exists(username): return False
        query = 'SELECT * FROM doctors WHERE username=?'
        doctor, hashed = cur.execute(query, (username,)).fetchone()
        return security.check_password_hash(hashed, password)

    @with_database
    def patient_add(self, cur, last_name, first_name, gender, dob,
                    height=None, weight=None, addr1=None, addr2=None,
                    phone1=None, phone2=None, email=None, medical_history=None,
                    medications=None, family_hx=None, allergy=None, note=None,
                    attachment=None):

        create_date = datetime.date.today()
        pkey_date = create_date.strftime('%y%m%d')

        query = 'SELECT COUNT(*) FROM patient WHERE patient_key LIKE ?'
        suffix = cur.execute(query, ('%' + pkey_date + '%',)).fetchone()[0]

        patient_key = last_name[0].upper() + pkey_date + str(suffix)

        query = 'INSERT INTO patient VALUES (%s)' % ('?,' * 20)[:-1]
        cur.execute(query, (
            create_date, suffix, patient_key, last_name, first_name, gender,
            dob, height, weight, addr1, addr2, phone1, phone2, email,
            medical_history, medications, family_hx, allergy, note, attachment
        ))

        return patient_key
    
    @with_database
    def patient_delete(self, cur, pkey):
        query = 'DELETE FROM patient WHERE patient_key=?'
        cur.execute(query, (pkey,))

    # WARNING: data keywords must be trusted
    @with_database
    def patient_update(self, cur, pkey, data):
        middle = []
        vals = []
        for key in data:
            if key not in self.patient_columns:
                raise InvalidColumn()
            middle.append('%s=?' % key) # sql injection
            vals.append(data[key])
        query = 'UPDATE patient SET %s WHERE patient_key=?' % ', '.join(middle)
        vals.append(pkey)
        cur.execute(query, vals)

    @with_database    
    def patient_exists(self, cur, patient_key):
        query = 'SELECT COUNT(*) FROM patient WHERE patient_key=?'
        count = cur.execute(query, (patient_key,)).fetchone()[0]
        return bool(count)

    # WARNING: **kwargs must be trusted
    @with_database
    def patient_search(self, cur, **kwargs):
        for key in kwargs:
            if key not in self.patient_columns:
                raise InvalidColumn()
        query = 'SELECT * FROM patient WHERE '
        query += ' AND '.join([ a + '=?' for a in kwargs ]) # sql injection
        values = [ kwargs[a] for a in kwargs ]
        resp = cur.execute(query, values).fetchall()
        return resp
    
    # WARNING: columns and sort_by must be trusted
    @with_database
    def patient_search_query(self, cur, search,
                             columns=['first_name', 'last_name', 'phone1', 'phone2', 'email'],
                             sort_by='patient_key', reverse_sort=False):

        for col in columns:
            if col not in self.patient_columns:
                raise InvalidColumn()
        if sort_by not in self.patient_columns:
            raise InvalidColumn()

        if len(search) < 3: search = ''
        query = 'SELECT * FROM patient WHERE '
        search = search.split()
        concat = ' || " " || '.join(columns) # sql injection
        values, params = [], []
        for item in search:
            for col in columns:
                params.append(concat + ' LIKE ?')
                values.append('%' + item + '%')
        desc = ' DESC' if reverse_sort else ''
        query += ' AND '.join(params) + ' ORDER BY %s%s' % (sort_by, desc)
        if not len(params): query = 'SELECT * FROM patient ORDER BY %s%s' % (sort_by, desc)
        resp = cur.execute(query, values).fetchall()
        return resp

    @with_database
    def visit_add(self, cur, ):
        
        if not self.patient_exists(patient_key):
            raise PatientNotFound()
        
        visit_date = datetime.date.today()
