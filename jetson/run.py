import recognition
import communication
from Threading import Thread, RLock
from flask import Flask, render_template
from flask_ask import Ask, statement, question

# run.py should house all of the commands that we will be using. It will do this in a hwile loop
mode = 'FOLLOW'
LOCK = RLock()

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launched():
	return question('What would you like me to do?')

@ask.intent('ForwardsIntent')
def forwards():
	with LOCK:
		mode = 'FORWARDS'
	return statement('Going forwards.')

@ask.intent('BackwardsIntent')
def backwards():
	with LOCK:
		mode = 'BACKWARDS'
	return statement('Going backwards.')

def get_new_mode():
	# will return any of the following depending on what alex says
	# "FOLLOW"
	# "WANDER"
	with LOCK:
		return str(mode)

def movement():
	while True:
		# code body:
		curr_mode = get_new_mode()

		if curr_mode == "FOLLOW":
			# process camera coordinates and direct motors
			command = recognition.process_frame()
			if command != "ERROR":
				communication.send(command)
			else:
				communication.send(b'0')
			print("Command: " + str(command))
		elif curr_mode == "WANDER":
			# wander command
			communication.send(b'5')
		elif curr_mode == "FORWARDS":
			# forwards command
			communication.send(b'1')
		elif curr_mode == "BACKWARDS":
			# backwards command
			communication.send(b'2')

Thread(movement).start()
app.run(debug=True)







'''
def get_new_mode():
	# will return any of the following depending on what alex says
	# "FOLLOW"
	# "WANDER"
	return "WANDER"

while True:
	# code body:
	mode = get_new_mode()
	
	if mode == "FOLLOW":
		# process camera coordinates and direct motors
		command = recognition.process_frame()
		if command != "ERROR":
			communication.send(command)
		else:
			communication.send(b'0')
		print("Command: " + str(command))
	elif mode == "WANDER":
		# wander command
		communication.send(b'5')
'''
