from flask import Flask, render_template
from flask_ask import Ask, statement, question

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launched():
	return question('what would you like me to do?')

@ask.intent('HelloIntent', default={'name': 'World'})
def hello(name):
	return statement('Hello, {}'.format(name))

@ask.intent('ByeIntent', default={'name': 'World'})
def bye(name):
	return statement('Chicken Shwarma, {}'.format(name))

@ask.intent('ForwardsIntent')
def forwards(name):
	return statement('Going forwards')

@ask.intent('BackwardsIntent')
def backwards(name):
	return statement('Going backwards')

if __name__ == '__main__':
	app.run(debug=True)
