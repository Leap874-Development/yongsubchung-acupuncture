from flask import Flask, render_template, redirect, request, session, abort
import json
import database
import secrets
import sys

with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)
db = database.Database('database.db')

if config['debug']:
    app.secret_key = secrets.token_hex(config['secret_length'])
else:
    app.secret_key = 'super_secret_debug_key'

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
            return redirect('/login')
    wrapper.__name__ = func.__name__
    return wrapper

@app.before_request
def before_request():
    if 'logged_in' not in session:
        session['logged_in'] = False
        session['doctor'] = None

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html',
        code=404,
        message='Page not found',
        doctor=session['doctor']
    ), 404

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
        if db.doctor_check(doctor, password):
            session['logged_in'] = True
            session['doctor'] = doctor
            return redirect('/home')
        else:
            return redirect('login?err=1')

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
    query = request.args.get('query')
    if not query: query = ''
    users = db.patient_search_query(query)
    truncated = False
    if len(users) > config['max_results']:
        users = users[:config['max_results']]
        truncated = True
    return render_template('home.html',
        doctor=session['doctor'],
        query=query,
        users=users,
        truncated=truncated,
        max_results=config['max_results']
    )

@app.route('/patient/<pkey>')
@require_authentication
def patient_detail(pkey):
    results = db.patient_search(patient_key=pkey)
    if len(results) != 1: abort(500)
    else: patient = results[0]
    return render_template('patient/view.html', doctor=session['doctor'], pkey=pkey, patient=patient)

@app.route('/patient/new')
@require_authentication
def patient_new():
    return render_template('patient/new.html', doctor=session['doctor'])

@app.route('/patient/<pkey>/new_visit')
@require_authentication
def patient_new_visit(pkey):
    return render_template('patient/new_visit.html', doctor=session['doctor'], pkey=pkey)

@app.route('/patient/<pkey>/return_visit')
@require_authentication
def patient_return_visit(pkey):
    return render_template('patient/return_visit.html', doctor=session['doctor'], pkey=pkey)

app.run(
    debug=config['debug'],
    host=config['ip'],
    port=config['port']
)