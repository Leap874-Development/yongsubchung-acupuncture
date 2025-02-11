from werkzeug import security
from datetime import datetime, timedelta, date
import sqlite3

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
            'attachment', 'patient_pkey', 'suffix', 'create_date']
        
        self.visit_columns = ['visit_pkey', 'suffix', 'new_visit',
            'patient_pkey', 'doctor', 'visit_date', 'temperature',
            'heart_rate', 'blood_pressure_h', 'blood_pressure_l',
            'chief_complaint', 'present_illness', 'exam_pulse_l',
            'exam_pulse_r', 'exam_sleep', 'exam_tongue', 'tcm_diag_1',
            'tcm_diag_2', 'tcm_diag_3', 'tcm_diag_4', 'treat_principle',
            'acu_points', 'moxa', 'cupping', 'eacu', 'auricular',
            'condition_treated', 'fee', 'paid', 'paid_check_by', 'note',
            'feedback', 'exam_appetite', 'exam_digest', 'exam_bm', 'location',
            'onset', 'provocation', 'palliation', 'quality', 'region',
            'severity', 'frequency', 'timing', 'possible_cause', 'remark',
            'tq_fever', 'tq_perspiration', 'tq_thirst', 'tq_appetite',
            'tq_digestion', 'tq_taste', 'tq_bm', 'exam_urine', 'exam_pain',
            'exam_consciousness', 'exam_energy_level', 'exam_stress_level',
            'women_menarche', 'women_menopause', 'women_num_pregnant',
            'women_num_child', 'women_miscarriage', 'women_leukorrhea',
            'women_birth_control', 'women_menstruation']

        conn = sqlite3.connect(path)
        cur = conn.cursor()

        try: cur.executescript(self.schema)
        except sqlite3.OperationalError: pass

        conn.commit()
        conn.close()
    
    @with_database
    def doctor_list(self, cur):
        query = 'SELECT username FROM doctors'
        return cur.execute(query).fetchall()
    
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
                    height='', weight='', addr1='', addr2='',
                    phone1='', phone2='', email='', medical_history='',
                    medications='', family_hx='', allergy='', note='',
                    attachment=''):

        create_date = date.today()
        pkey_date = create_date.strftime('%y%m%d')

        query = 'SELECT COUNT(*) FROM patient WHERE patient_pkey LIKE ?'
        suffix = cur.execute(query, ('%' + pkey_date + '%',)).fetchone()[0]

        patient_pkey = last_name[0].upper() + pkey_date + str(suffix)

        query = 'INSERT INTO patient VALUES (%s)' % ('?,' * 20)[:-1]
        cur.execute(query, (
            create_date, suffix, patient_pkey, last_name, first_name, gender,
            dob, height, weight, addr1, addr2, phone1, phone2, email,
            medical_history, medications, family_hx, allergy, note, attachment
        ))

        return patient_pkey
    
    @with_database
    def patient_delete(self, cur, pkey):
        query = 'DELETE FROM patient WHERE patient_pkey=?'
        cur.execute(query, (pkey,))

    @with_database
    def patient_update(self, cur, pkey, data):
        middle = []
        vals = []
        for key in data:
            if key not in self.patient_columns:
                raise InvalidColumn()
            middle.append('%s=?' % key)
            vals.append(data[key])
        query = 'UPDATE patient SET %s WHERE patient_pkey=?' % ', '.join(middle)
        vals.append(pkey)
        cur.execute(query, vals)

    @with_database    
    def patient_exists(self, cur, patient_pkey):
        query = 'SELECT COUNT(*) FROM patient WHERE patient_pkey=?'
        count = cur.execute(query, (patient_pkey,)).fetchone()[0]
        return bool(count)

    @with_database
    def patient_search(self, cur, **kwargs):
        for key in kwargs:
            if key not in self.patient_columns:
                raise InvalidColumn()
        query = 'SELECT * FROM patient WHERE '
        query += ' AND '.join([ a + '=?' for a in kwargs ])
        values = [ kwargs[a] for a in kwargs ]
        resp = cur.execute(query, values).fetchall()
        return resp
    
    @with_database
    def patient_search_query(self, cur, search,
                             columns=['first_name', 'last_name', 'phone1',
                             'phone2', 'email'], sort_by='patient_pkey',
                             reverse_sort=False):

        for col in columns:
            if col not in self.patient_columns:
                raise InvalidColumn()
        if sort_by not in self.patient_columns:
            raise InvalidColumn()

        if len(search) < 3: search = ''
        query = 'SELECT * FROM patient WHERE '
        search = search.split()
        concat = ' || " " || '.join(columns)
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
    def visit_add(self, cur, new_visit, patient_pkey, doctor, temperature='',
                  heart_rate='', blood_pressure_h='', blood_pressure_l='',
                  chief_complaint='', present_illness='', exam_pulse_l='',
                  exam_pulse_r='', exam_sleep='', exam_tongue='',
                  tcm_diag_1='', tcm_diag_2='', tcm_diag_3='',
                  tcm_diag_4='', treat_principle='', acu_points='',
                  moxa='', cupping='', eacu='', auricular='',
                  condition_treated='', fee='', paid='',
                  paid_check_by='', note='', feedback='',
                  exam_appetite='', exam_digest='', exam_bm='',
                  location='', onset='', provocation='', palliation='',
                  quality='', region='', severity='', frequency='',
                  timing='', possible_cause='', remark='', tq_fever='',
                  tq_perspiration='', tq_thirst='', tq_appetite='',
                  tq_digestion='', tq_taste='', tq_bm='', exam_urine='',
                  exam_pain='', exam_consciousness='',
                  exam_energy_level='', exam_stress_level='',
                  women_menarche='', women_menopause='',
                  women_num_pregnant='', women_num_child='',
                  women_miscarriage='', women_leukorrhea='',
                  women_birth_control='', women_menstruation=''):

        visit_date = date.today()
        pkey_date = visit_date.strftime('%y%m%d')
        
        new_visit = str(new_visit).lower()
        moxa = str(moxa).lower()
        cupping = str(cupping).lower()
        eacu = str(eacu).lower()
        paid = str(paid).lower()

        query = 'SELECT COUNT(*) FROM visit WHERE visit_pkey LIKE ?'
        suffix = cur.execute(query, ('%' + pkey_date + '%',)).fetchone()[0]

        visit_pkey = patient_pkey[0].upper() + pkey_date + str(suffix)

        if not self.patient_exists(patient_pkey):
            raise PatientNotFound()
        
        query = 'INSERT INTO visit VALUES (%s)' % ('?,' * 66)[:-1]
        cur.execute(query, (
            visit_pkey, suffix, new_visit, patient_pkey, doctor, visit_date,
            temperature, heart_rate, blood_pressure_h, blood_pressure_l,
            chief_complaint, present_illness, exam_pulse_l, exam_pulse_r,
            exam_sleep, exam_tongue, tcm_diag_1, tcm_diag_2, tcm_diag_3,
            tcm_diag_4, treat_principle, acu_points, moxa, cupping, eacu,
            auricular, condition_treated, fee, paid, paid_check_by, note,
            feedback, exam_appetite, exam_digest, exam_bm, location, onset,
            provocation, palliation, quality, region, severity, frequency,
            timing, possible_cause, remark, tq_fever, tq_perspiration,
            tq_thirst, tq_appetite, tq_digestion, tq_taste, tq_bm, exam_urine,
            exam_pain, exam_consciousness, exam_energy_level, exam_stress_level,
            women_menarche, women_menopause, women_num_pregnant,
            women_num_child, women_miscarriage, women_leukorrhea,
            women_birth_control, women_menstruation
        ))
    
    @with_database
    def visit_search(self, cur, **kwargs):
        for key in kwargs:
            if key not in self.visit_columns:
                raise InvalidColumn()
        query = 'SELECT * FROM visit WHERE '
        query += ' AND '.join([ a + '=?' for a in kwargs ]) + ' ORDER BY visit_date DESC, visit_pkey DESC'
        values = [ kwargs[a] for a in kwargs ]
        resp = cur.execute(query, values).fetchall()
        return resp
    
    @with_database
    def visit_between(self, cur, date_min, date_max, sort_by='patient_name', reverse_sort=False):
        values = [date_min, date_max]
        query = 'SELECT * FROM visit WHERE visit_date BETWEEN ? AND ?'
        query += ' ORDER BY visit_date DESC, visit_pkey DESC'
        resp = cur.execute(query, [ a.strftime('%Y-%m-%d') for a in values ]).fetchall()
        return resp

    @with_database
    def visit_paid(self, cur, visit_pkey, doctor, paid=True):
        paid = str(paid).lower()
        query = 'UPDATE visit SET paid=?, paid_check_by=? WHERE visit_pkey=?'
        cur.execute(query, (paid, doctorm, visit_pkey))

db = Database('database.db')
# x = db.visit_between(date.today() - timedelta(days=30), date.today())
# print(x)
# db.visit_paid('A191115321')