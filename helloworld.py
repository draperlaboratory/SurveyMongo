from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask import request
from surveymongo_test import collect_responses

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
	user_agent = request.headers.get('User-Agent')
	return '<h1>Hello World!</h1><p>Your browser is %s</p>' % user_agent

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

@app.route('/surveymongo/<session_id>')
def surveymongo(session_id):
	# this = [{'ID':'one', 'Name':'Bob', 'Role':'developer'}, {'ID':'two'}]
	responses = collect_responses(session_id)
	sorted_responses = sorted(responses, key=lambda k: k['question_id'])
	if len(sorted_responses) > 0:
		return render_template('list.html', list=responses)
	else:
		return render_template('unknown_id.html', session_id=session_id)

if __name__ == '__main__':
	app.run(debug=True, port=8000)

