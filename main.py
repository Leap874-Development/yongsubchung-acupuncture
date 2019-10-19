from flask import Flask
import json

app = Flask(__name__)

with open('config.json', 'r') as f:
	config = json.load(f)

@app.route('/')
def index():
	return 'Hello, world!'

app.run(host=config['ip'], port=config['port'], debug=config['debug'])