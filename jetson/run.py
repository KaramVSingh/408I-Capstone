import recognition
import communication
from threading import Thread, RLock
from flask import Flask, render_template
from flask_ask import Ask, statement, question
from Client import *
from time import sleep
import json
import datetime

import time
millis = lambda: int(round(time.time() * 1000))

# run.py should house all of the commands that we will be using. It will do this in a hwile loop
mode = 'STOP'
LOCK = RLock()
open_service('Robot-Robot')

def read_messages():
	mess = get_messages()
	read = ''

	for message in mess:
		if len(message) == 3:
			read += message[1] + ' sent ' + '"' + message[2] + '"' + ' to room ' + message[0] + '.'
		else:
			read += message[0] + ' sent you ' + '"' + message[1] + '".'
	
	return read

def set_mode(new_mode):
	with LOCK:
		global mode
		mode = new_mode

def you_ded_boi():
	send_room_message('Nitin has fallen.')

def are_you_ded():
	sleep(2)
	command = recognition.process_frame()
	if command == 'ERROR' or command == b'6':
		you_ded_boi()
	
def movement():
	global mode
	last = 0
	command_count = 0
	while True:
		while millis() - last < 100:
			pass
		last = millis()

		# code body:
		curr_mode = str(mode)

		if command_count > 5:
			set_mode('STOP')

		if curr_mode != "LEFT" and curr_mode != "RIGHT":
			command_count = 0
		else:
			command_count += 1

		if curr_mode == "FOLLOW":
			# process camera coordinates and direct motors
			command = recognition.process_frame()
			if command != "ERROR":
				if command == b'6':
					are_you_ded()
				else:
					communication.send(command)
			else:
				communication.send(b'0')
		elif curr_mode == "WANDER":
			# wander command
			communication.send(b'5')
			# send_room_message('Nitin wandered off again, can you help me find him?')
		elif curr_mode == "FORWARDS":
			# forwards command
			communication.send(b'1')
		elif curr_mode == "BACKWARDS":
			# backwards command
			communication.send(b'2')
		elif curr_mode == "STOP":
			# stop command
			communication.send(b'0')
		elif curr_mode == "LEFT":
			# left command
			communication.send(b'4')
		elif curr_mode == "RIGHT":
			# right command
			communication.send(b'3')
		elif curr_mode == "MONITOR":
			# monitor command
			command = recognition.process_frame()
			communication.send(b'0')
			if command == b'6':
				are_you_ded()
		else:
			print('NO COMMAND')

Thread(target=movement).start()

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launched():
	return question('What would you like me to do?')

@ask.intent('ForwardsIntent')
def forwards():
	set_mode('FORWARDS')
	return statement('Chicken Shwarma.')

@ask.intent('BackwardsIntent')
def backwards():
	set_mode('BACKWARDS')
	return statement('Veggie Shwarma.')

@ask.intent('StopIntent')
def forwards():
	set_mode('STOP')
	return statement('Fine I will.')

@ask.intent('FollowIntent')
def backwards():
	set_mode('FOLLOW')
	return statement('Sahil Sharma.')

@ask.intent('LeftIntent')
def backwards():
	set_mode('LEFT')
	return statement('Turning Left.')

@ask.intent('RightIntent')
def backwards():
	set_mode('RIGHT')
	return statement('Turning Right.')

@ask.intent('WanderIntent')
def backwards():
	set_mode('WANDER')
	return statement('Lamb Shwarma.')

@ask.intent('MonitorIntent')
def backwards():
	set_mode('MONITOR')
	return statement('I mean, I can watch.')

@ask.intent('MessagesIntent')
def messages():
	set_mode('STOP')
	return statement(read_messages())

@ask.intent('PlayDeadIntent')
def play_dead():
	communication.send(b'7')
	set_mode('BACKWARDS')
	sleep(1)
	set_mode('FORWARDS')
	sleep(0.25)
	set_mode('STOP')
	communication.send(b'8')
	
	send_room_message('blegh')
	return statement('blegh')

@ask.intent('PillsIntent')
def pills():
	new_json = None
	pills = []
	with open('pills.json') as json_file:
		data = json.load(json_file)
		day = datetime.datetime.today().weekday()
		last = data['LAST']
		for i in range(int(last), day):
			pills += [data[str(i)]]

		new_json = data
		new_json['LAST'] = str(day)

	with open('pills.json', 'w') as outfile:
		json.dump(new_json, outfile)

	if(len(pills) == 0):
		return statement("You've already taken your pills today")
 
	stmt = ''
	for i, pill in enumerate(pills):
		if i == len(pills) - 1:
			stmt += pill + '.'
		else:
			stmt += pill + ', '

	return statement(stmt)

app.run(debug=True, use_reloader=False)



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
