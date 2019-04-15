#!/usr/bin/env python

import socket

TCP_IP = '10.104.46.69'
TCP_PORT = 9000
BUFFER_SIZE = 2048
YOUR_NAME = 'ROBOT-ROBOT'
in_room = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def open_service(team_name, ip, port):
	s.connect((TCP_IP, TCP_PORT))

	# initialization process
	s.send(b'\x04\x17\x00\x00\x00\x05\xff\x48\x65\x6c\x6c\x6f')
	if len(s.recv(BUFFER_SIZE)) < 13:
		print('Failed to connect.')
		exit()

	s.send(b'\x04\x17' + (len(team_name) + 1).to_bytes(4, byteorder='BIG') + b'\x1b' + len(team_name).to_bytes(4, byteorder='BIG') + str.encode(team_name))
	if s.recv(BUFFER_SIZE) == 0:
		print('Failed to connect.')
		exit()

def join_room(room_name):
	if in_room:
		pass
		# \leave
	# \join room_name
	in_room = True
	s.send(MESSAGE)

def send_room_message(message):
	if not in_room:
		return None

	# \send

def send_personal_message(person, message):
	# \msg
	pass

def get_messages():
	data = s.recv(BUFFER_SIZE)

def close_service():
	s.close()

open_service('ROBOT-ROBOT', TCP_IP, TCP_PORT)
close_service()