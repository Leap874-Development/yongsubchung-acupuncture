from flask import Flask, render_template
import json

app = Flask(__name__)

with open('config.json', 'r') as f:
	config = json.load(f)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login')
def login():
	return 'unimplemented'

@app.route('/logout')
def logout():
	return 'unimplemented'

@app.route('/revenue')

@app.route('/patients')
def patients():
	return 'unimplemented'

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