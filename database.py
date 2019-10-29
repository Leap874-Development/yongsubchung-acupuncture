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
    def visit_add(self, cur, patient_key, doctor, temperature=None,
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
        cur.execute(query, (
            patient_key, doctor, visit_date, temperature, heart_rate,
            blood_pressure_h, blood_pressure_l, chief_complaint,
            present_illness, feedback, exam_appetite, exam_digest, exam_bm,
            exam_sleep, exam_tongue, exam_pulse_l, exam_pulse_r, tcm_diag_1,
            tcm_diag_2, tcm_diag_3, tcm_diag_4, treat_principle, acu_points,
            moxa, cupping, eacu, arricular, condition_treated, fee, paid,
            paid_check_by, note
        ))
    
    @with_database
    def new_visit_add(self, cur, patient_key, doctor, temperature=None,
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
        cur.execute(query, (
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