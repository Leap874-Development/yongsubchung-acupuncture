from flask import Flask, render_template, redirect, request, session, abort
from datetime import datetime
import json
import database
import secrets
import sys

with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)
db = database.Database('database.db')

if config['debug']:
    app.secret_key = 'super_secret_debug_key'
    db.debug = True
else:
    app.secret_key = secrets.token_hex(config['secret_length'])

def format_phone(raw):
    raw = str(raw)
    if len(raw) != 10:
        return raw
    else:
        return '(%s)%s-%s' % (raw[0:3], raw[3:6], raw[6:10])

app.jinja_env.globals.update(format_phone=format_phone)

def require_authentication(func):
    def wrapper(*args, **kwargs):
        if session['logged_in']:
            return func(*args, **kwargs)
        else:
            return redirect('/login?err=2&redirect=%s' % request.path)
    wrapper.__name__ = func.__name__
    return wrapper

@app.before_request
def before_request():
    if 'logged_in' not in session:
        session['logged_in'] = False
        session['doctor'] = None

@app.errorhandler(400)
def page_not_found(error):
    return render_template('error.html',
        code=400,
        message='Invalid request',
        doctor=session['doctor']
    ), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html',
        code=404,
        message='Page not found',
        doctor=session['doctor']
    ), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template('error.html',
        code=405,
        message='Method not allowed',
        doctor=session['doctor']
    ), 405

@app.errorhandler(500)
def page_not_found(error):
    return render_template('error.html',
        code=500,
        message='An internal server error occured',
        doctor=session['doctor']
    ), 500

@app.route('/', methods=['GET'])
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session['logged_in']:
            return redirect('/home')
        return render_template('login.html')
    elif request.method == 'POST':
        doctor = request.values.get('doctor')
        password = request.values.get('password')
        redir = request.values.get('redirect')
        if db.doctor_check(doctor, password):
            session['logged_in'] = True
            session['doctor'] = doctor
            return redirect(redir)
        else:
            return redirect('login?err=1')
    else:
        abort(405)

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    session['doctor'] = None
    return redirect('/login')

@app.route('/reports')
@require_authentication
def reports():
    return render_template('reports.html', doctor=session['doctor'])

@app.route('/home')
@require_authentication
def home():
    accepted_sort = ['patient_pkey', 'first_name', 'last_name']

    icon_neutral = 'icon-angle-down'
    icon_up = 'icon-caret-up'
    icon_down = 'icon-caret-down'

    query = request.args.get('query')
    sort_by = request.args.get('sort_by')
    reverse = request.args.get('reverse') == 'true'
    if sort_by and sort_by not in accepted_sort:
        abort(400)
    else:
        if not query: query = ''
        if not sort_by:
            sort_by = 'patient_pkey'
            reverse = False

        sort_data = [icon_neutral] * 3
        sort_direction = icon_down if reverse else icon_up
        if sort_by == 'patient_pkey': sort_data[0] = sort_direction
        if sort_by == 'first_name': sort_data[1] = sort_direction
        if sort_by == 'last_name': sort_data[2] = sort_direction

        users = db.patient_search_query(query, sort_by=sort_by, reverse_sort=reverse)
        truncated = False
        result_len = len(users)
        if result_len > config['max_results']:
            users = users[:config['max_results']]
            truncated = True

    return render_template('home.html',
        doctor=session['doctor'],
        query=query,
        users=users,
        truncated=truncated,
        result_len=result_len,
        max_results=config['max_results'],
        sort_data=sort_data,
        sort_by=sort_by,
        reverse=str(reverse).lower()
    )

@app.route('/patient/new', methods=['GET', 'POST'])
@require_authentication
def patient_new():
    if request.method == 'GET':
        return render_template('patient/new.html', doctor=session['doctor'])
    elif request.method == 'POST':
        first_name = request.values.get('first_name')
        last_name = request.values.get('last_name')
        dob = request.values.get('dob')
        gender = request.values.get('gender')
        if not first_name or not last_name: abort(400)
        if gender not in ['m', 'f']: abort(400)
        try: dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError: abort(400)
        pkey = db.patient_add(last_name, first_name, gender, dob, **{
            'height': request.values.get('height'),
            'weight': request.values.get('weight'),
            'addr1': request.values.get('addr1'),
            'addr2': request.values.get('addr2'),
            'phone1': request.values.get('phone1'),
            'phone2': request.values.get('phone2'),
            'email': request.values.get('email'),
            'medical_history': request.values.get('medical_history'),
            'family_hx': request.values.get('family_hx'),
            'allergy': request.values.get('allergy'),
            'note': request.values.get('note'),
            'attachment': request.values.get('attachment')
        })
        return redirect('/patient/' + pkey)
    else:
        abort(400)

@app.route('/patient/<pkey>', methods=['GET', 'POST'])
@require_authentication
def patient_detail(pkey):
    if request.method == 'GET':
        results = db.patient_search(patient_pkey=pkey)
        visits = db.visit_search(patient_pkey=pkey)
        new_visit = not len(db.visit_search(patient_pkey=pkey, new_visit='true'))
        if len(results) != 1: abort(500)
        else: patient = results[0]
        return render_template('patient/view.html',
            doctor=session['doctor'],
            pkey=pkey,
            patient=patient,
            visits=visits,
            new_visit=new_visit
        )
    elif request.method == 'POST':
        visit_keys = [
            'temperature', 'blood_pressure_l', 'blood_pressure_h', 'heart_rate',
            'chief_complaint', 'location', 'onset', 'provocation', 'palliation',
            'quality', 'region', 'severity', 'frequency', 'timing',
            'possible_cause', 'remark', 'present_illness', 'tq_fever',
            'tq_perspiration', 'tq_thirst', 'tq_appetite', 'tq_digestion',
            'tq_taste', 'tq_bm', 'exam_urine', 'exam_sleep', 'exam_pain',
            'exam_tongue', 'exam_consciousness', 'exam_energy_level',
            'exam_stress_level', 'exam_pulse_l', 'exam_pulse_r', 'tcm_diag_1',
            'treat_principle', 'acu_points', 'tcm_diag_2', 'tcm_diag_3',
            'tcm_diag_4', 'moxa', 'cupping', 'eacu', 'auricular',
            'condition_treated', 'fee', 'paid', 'note', 'women_menarche',
            'women_menopause', 'women_num_pregnant', 'women_num_child',
            'women_miscarriage', 'women_leukorrhea', 'women_birth_control',
            'women_menstruation'
        ]

        patient_keys = [
            'medical_history', 'medications', 'family_hx', 'allergy'
        ]

        visit_data, patient_data = {}, {}
        for key in visit_keys: visit_data[key] = request.values.get(key)
        for key in patient_keys: patient_data[key] = request.values.get(key)

        new_visit = request.values.get('new_visit')
        doctor = session['doctor']

        db.patient_update(pkey, patient_data)
        db.visit_add(new_visit, pkey, doctor, **visit_data)

        return redirect('/patient/' + pkey)
    else:
        abort(405)

@app.route('/patient/<pkey>/edit', methods=['GET', 'POST'])
@require_authentication
def patient_edit(pkey):
    if request.method == 'GET':
        results = db.patient_search(patient_pkey=pkey)
        if len(results) != 1: abort(500)
        else: patient = results[0]
        return render_template('patient/edit.html', doctor=session['doctor'], pkey=pkey, patient=patient)
    elif request.method == 'POST':
        first_name = request.values.get('first_name')
        last_name = request.values.get('last_name')
        gender = request.values.get('gender')
        dob = request.values.get('dob')
        if not first_name or not last_name: abort(400)
        if gender not in ['m', 'f']: abort(400)
        try: dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError: abort(400)
        db.patient_update(pkey, {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob, 'gender': gender,
            'height': request.values.get('height'),
            'weight': request.values.get('weight'),
            'addr1': request.values.get('addr1'),
            'addr2': request.values.get('addr2'),
            'phone1': request.values.get('phone1'),
            'phone2': request.values.get('phone2'),
            'email': request.values.get('email'),
            'medical_history': request.values.get('medical_history'),
            'family_hx': request.values.get('family_hx'),
            'allergy': request.values.get('allergy'),
            'note': request.values.get('note'),
            'attachment': request.values.get('attachment')
        })
        return redirect('/patient/' + pkey)
    else:
        abort(405)

@app.route('/patient/<pkey>/delete')
@require_authentication
def patient_delete(pkey):
    db.patient_delete(pkey)
    return redirect('/home?alert=Patient deleted')

app.run(
    debug=config['debug'],
    host=config['ip'],
    port=config['port']
)