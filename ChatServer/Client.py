#!/usr/bin/env python

import socket

TCP_IP = '10.104.37.198'
TCP_PORT = 9000
BUFFER_SIZE = 2048
_room_name = 'default'
_messages = b''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def _update_messages():
	global _messages
	while True:
		try:
			buff = s.recv(BUFFER_SIZE)
			_messages += buff
		except socket.timeout:
			return

def open_service(team_name):
	s.connect((TCP_IP, TCP_PORT))
	s.settimeout(0.25)
	global _room_name

	# initialization process
	s.send(b'\x04\x17\x00\x00\x00\x05\xff\x48\x65\x6c\x6c\x6f')
	buff = s.recv(BUFFER_SIZE)
	if len(buff) < 13:
		print('Failed to connect.')
		exit()

	s.send(b'\x04\x17' + (len(team_name) + 1).to_bytes(4, byteorder='big') + b'\x1b' + len(team_name).to_bytes(1, byteorder='big') + str.encode(team_name))
	buff = s.recv(BUFFER_SIZE)
	if len(buff) == 0:
		print('Failed to connect.')
		exit()

	# by default we will join the room 'default'
	s.send(b'\x04\x17' + (len('default') + 1 + 1).to_bytes(4, byteorder='big') + b'\x17' + len('default').to_bytes(1, byteorder='big') + str.encode('default') + b'\x00')
	buff = s.recv(BUFFER_SIZE)
	if len(buff) == 0:
		print('Failed to connect.')
		exit()
	
	_room_name = 'default'

def join_room(room_name):
	# \join room_name
	_update_messages()
	s.send(b'\x04\x17' + (len(room_name) + 1 + 1).to_bytes(4, byteorder='big') + b'\x17' + len(room_name).to_bytes(1, byteorder='big') + str.encode(room_name) + b'\x00')
	buff = s.recv(BUFFER_SIZE)
	if len(buff) == 0:
		print('Failed to connect.')
		exit()

	_room_name = room_name

def send_room_message(message):
	# \send
	_update_messages()
	s.send(b'\x04\x17' + (len(message + _room_name) + 1 + 1 + 1).to_bytes(4, byteorder='big') + b'\x1d' + len(_room_name).to_bytes(1, byteorder='big') + str.encode(_room_name) + b'\x00' + len(message).to_bytes(1, byteorder='big') + str.encode(message))
	buff = s.recv(BUFFER_SIZE)
	if len(buff) == 0:
		print('Failed to connect.')
		exit()

def send_personal_message(person, message):
	# \msg
	_update_messages()
	s.send(b'\x04\x17' + (len(message + person) + 1 + 1 + 1).to_bytes(4, byteorder='big') + b'\x1c' + len(person).to_bytes(1, byteorder='big') + str.encode(person) + b'\x00' + len(message).to_bytes(1, byteorder='big') + str.encode(message))
	buff = s.recv(BUFFER_SIZE)
	if len(buff) == 0:
		print('Failed to connect.')
		exit()

def get_messages():
	_update_messages()
	global _messages
	i = 0
	ret_messages = []
	while i < len(_messages):
		msg_length = int.from_bytes(_messages[i+2:i+6], byteorder='big')
		i = i + 7
		current_message = []
		current_sub_message = b''
		current_length = 0
		for j in range(msg_length):
			if _messages[i] != 0:
				if current_length == 0:
					current_length = _messages[i]
					if len(current_sub_message) > 0:
						current_message += [current_sub_message.decode('utf-8')]
						current_sub_message = b''
				else:
					current_length -= 1
					current_sub_message += bytes([_messages[i]])
			i += 1

		current_message += [current_sub_message.decode('utf-8')]
		ret_messages += [current_message]

	_messages = b''
	return ret_messages

def close_service():
	s.close()

'''
open_service('ROBOT-ROBOT', TCP_IP, TCP_PORT)
send_room_message('Hello world')
close_service()
'''