from flask import Flask, render_template, redirect, request, session
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

def require_authentication(func):
	def wrapper(*args, **kwargs):
		if session['logged_in']:
			return func(*args, **kwargs)
		else:
			return redirect('login')
	return wrapper

@app.before_request
def before_request():
	if 'logged_in' not in session:
		session['logged_in'] = False
		session['doctor'] = None

@app.route('/', methods=['GET'])
def index():
	return redirect('login')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		if session['logged_in']:
			return redirect('home')
		return render_template('login.html')
	elif request.method == 'POST':
		doctor = request.values.get('doctor')
		password = request.values.get('password')
		if db.doctor_check(doctor, password):
			session['logged_in'] = True
			session['doctor'] = doctor
			return redirect('home')
		else:
			return redirect('login?err=1')

@app.route('/logout', methods=['GET'])
def logout():
	session['logged_in'] = False
	session['doctor'] = None
	return redirect('login')

@app.route('/revenue')
def revenue():
	return 'unimplemented'

@app.route('/home')
@require_authentication
def home():
	return render_template('home.html', doctor=session['doctor'])

@app.route('/patient/<name>')
def patient_detail(name):
	return name

@app.route('/patient/<name>/new_visit')
def patient_new_visit(name):
	return name

@app.route('/patient/<name>/return_visit')
def patient_return_visit(name):
	return name

@app.route('/patient/new')
def patient_new():
	return 'unimplemented'

app.run(
	debug=config['debug'],
	host=config['ip'],
	port=config['port']
)