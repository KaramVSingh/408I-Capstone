#!/usr/bin/env python3

import socket
import sys
from threading import RLock, Thread
from LinkedList import LinkedList


# clients will be a mapping of name => Client objects which keep track of state
BASE = b'\x04\x17'
clients = {}
clients_order = LinkedList()
rooms = {}
ROOM_LOCK = RLock()
CLIENT_LOCK = RLock()

# this is the class that will maintain room state
class Room:
	def __init__(self, name, password):
		self.name = name
		self.password = password
		self.clients = []
		self.CURR_LOCK = RLock()

	def get_client_names(self):
		lst = []
		with self.CURR_LOCK:
			for client in self.clients:
				lst += [client.name]

		return lst

	def index_of_client(self, client):
		with self.CURR_LOCK:
			for i in range(0, len(self.clients)):
				if(self.clients[i] == client):
					return i
		return None

	def add_client(self, client):
		with self.CURR_LOCK:
			self.clients += [client]

	def remove_client(self, client):
		ret_val = True
		with ROOM_LOCK:
			i = self.index_of_client(client)
			if(i == None):
				ret_val = False
			else:
				with self.CURR_LOCK:
					del self.clients[i]
					if(len(self.clients) == 0):
						del rooms[self.name]

		return ret_val

# this is the class that will maintain state
class Client:
	def __init__(self, index):
		self.index = index
		self.name = 'rand' + str(index)
		self.state = 'WAITING'
		self.room = None
		self.WRITE_LOCK = RLock()

	def close_connection(self):
		with CLIENT_LOCK:
			del clients[self.name]
			clients_order.remove(self)
		
		self.connection.close()
		exit()

	def recv(self, num_bytes):
		data = self.connection.recv(num_bytes)
		if(not data):
			self.close_connection()

		return data

	def send(self, payload):
		with self.WRITE_LOCK:
			self.connection.send(payload)

	def handle_client(self, connection, client_address):
		self.connection = connection
		self.client_address = client_address
		while(True):
			# first part of the message seems to be the same for each request
			self.recv(2)
			print('got message from ' + str(client_address), end=': ')

			# next four bytes seem to be the payload length
			length = int.from_bytes(self.recv(4), byteorder="big")
			
			# next item is the opcode (one byte)
			op = self.recv(1)
			print('op = ' + str(op))

			# now we want to read in the rest of the payload
			payload = b''
			if(length != 0):
				payload = self.recv(length)

			# we have the opcode and the length, now we want to do the rest of the information
			if(op == b'\xff'):
				# this is the initialize message
				# we respond with the name of the client opcode \xfe prepended with a \x00
				# this should succeed in all cases so the response should be uniform
				return_length = len(self.name) + 1
				message = BASE + return_length.to_bytes(4, byteorder="big")
				message += b'\xfe' + b'\x00' + self.name.encode()
				self.state = 'READY'
				self.send(message)
			elif(op == b'\x17'):
				# this is the join room message
				# we will respond with success of fail accordingly
				# success: got right name and pass / making new room
				# fail: got wrong password, reenter same room
				room = ''
				room_length = 0
				password = ''
				password_length = 0
				state = 'ROOM_LENGTH'

				for i in range(0, len(payload)):
					c = payload[i]
					if(state == 'ROOM_LENGTH'):
						room_length = c
						state = 'ROOM'
					elif(state == 'ROOM'):
						room += chr(c)
						room_length -= 1
						if(room_length == 0):
							state = 'PASSWORD_LENGTH'
					elif(state == 'PASSWORD_LENGTH'):
						password_length = c
						state = 'PASSWORD'
					elif(state == 'PASSWORD'):
						password += chr(c)
						password_length -= 1

				success = False
				reason = ''

				# now we have room and pass, we need to evaluate expression
				with ROOM_LOCK:
					if(not room in rooms):
						if(self.room != None):
							self.room.remove_client(self)
						# then we have to add it
						rooms[room] = Room(room, password)
						self.room = rooms[room]
						rooms[room].add_client(self)
						success = True
					else:
						if(rooms[room].index_of_client(self) != None):
							success = False
							reason = 'You fail to bend space and time to reenter where you already are.'
						else:
							if(rooms[room].password == password):
								if(self.room != None):
									self.room.remove_client(self)
								# then we have to add it
								self.room = rooms[room]
								rooms[room].add_client(self)
								success = True
							else:
								success = False
								reason = 'Wrong password. You shall not pass!'

				if(success):
					msg = BASE + (1).to_bytes(4, byteorder="big") + b'\xfe\x00'
					self.send(msg)
				else:
					msg = BASE + (len(reason) + 1).to_bytes(4, byteorder="big")
					msg += b'\xfe\x01' + reason.encode()
					self.send(msg)
			elif(op == b'\x18'):
				# this is a leave command
				# it should succeed always
				msg = BASE + (1).to_bytes(4, byteorder="big") + b'\xfe\x00'

				if(self.room != None):
					self.room.remove_client(self)
					self.room = None
				else:
					self.close_connection()

				self.send(msg)
			elif(op == b'\x19'):
				# this is the request to list all the rooms
				# this should always succeed but always send opcode
				# as well as return value
				# we also want to send all rooms in sorted order
				with ROOM_LOCK:
					curr_rooms = list(rooms.keys())

				# now we just need to construct the message back
				curr_rooms.sort()
				total_length = 1
				for room in curr_rooms:
					total_length += 1 + len(room)

				msg = BASE + total_length.to_bytes(4, byteorder="big") + b'\xfe\x00'

				for room in curr_rooms:
					msg += len(room).to_bytes(1, byteorder="big")
					msg += room.encode()

				self.send(msg)
			elif(op == b'\x1a'):
				# this is the list users command
				# this should list all users if they are not in a room
				# this should list the users in the room if they are in a room
				# this should list all users in order of creation/time they joined room
				msg = BASE
				curr_clients = []

				if(self.room != None):
					# we are in a room and should get the list for that room
					curr_clients = self.room.get_client_names()
					curr_clients.reverse()
				else:
					# here we need to descide the order of joining the server
					with CLIENT_LOCK:
						curr_clients = clients_order.get_list()

					temp = []
					for client in curr_clients:
						temp += [client.name]

					curr_clients = temp
					curr_clients.reverse()

				total_length = 1
				for client in curr_clients:
					total_length += 1 + len(client)

				msg += total_length.to_bytes(4, byteorder="big") + b'\xfe\x00'

				for client in curr_clients:
					msg += len(client).to_bytes(1, byteorder="big")
					msg += client.encode()

				self.send(msg)
			elif(op == b'\x1b'):
				# this is the nick call. It should fail when:
				# the nick already exists in the list of users
				name = payload[1:len(payload)].decode("utf-8")

				curr_clients = []
				with CLIENT_LOCK:
					curr_clients = clients_order.get_list()

					success = True
					for client in curr_clients:
						if client.name == name:
							success = False

					if(success):
						del clients[self.name]
						clients[name] = self
						self.name = name
						msg = BASE + (1).to_bytes(4, byteorder="big") + b'\xfe\x00'
						self.send(message)
					else:
						reason = 'Someone already nicked that nick.'
						msg = BASE + (len(reason) + 1).to_bytes(4, byteorder="big")
						msg += b'\xfe\x01' + reason.encode()

						self.send(msg)
			elif(op == b'\x1c'):
				# this is the msg command it should fail if it is sending to an unknown erson
				name_length = 0
				name = ''
				message_length = 0
				message = ''
				check = True
				state = 'NAME_LENGTH'

				for i in range(0, len(payload)):
					c = payload[i]
					if(state == 'NAME_LENGTH'):
						name_length = c
						state = 'NAME'
					elif(state == 'NAME'):
						name += chr(c)
						name_length -= 1
						if(name_length == 0):
							state = 'MESSAGE_LENGTH'
					elif(state == 'MESSAGE_LENGTH'):
						if(check):
							check = False
							message_length = int.from_bytes(payload[i:i+1], byteorder="big")
						else:
							state = 'MESSAGE'
					elif(state == 'MESSAGE'):
						message += chr(c)
						message_length -= 1

				with CLIENT_LOCK:
					curr_clients = clients_order.get_list()

					success = False
					send_to = None
					for client in curr_clients:
						if client.name == name:
							send_to = client
							success = True

					if(success):
						# in this case we want to send the message and send a response saying it happened
						msg = BASE + len(payload).to_bytes(4, byteorder="big") + op + payload
						send_to.send(msg)
						msg = BASE + (1).to_bytes(4, byteorder="big") + b'\xfe\x00'
						self.send(msg)
					else:
						# this is the case where we do not find the user in the list
						reason = 'Nick not found.'
						msg = BASE + (len(reason) + 1).to_bytes(4, byteorder="big")
						msg += b'\xfe\x01' + reason.encode()
						self.send(msg)
			elif(op == b'\x1d'):
				# this is an in room message and should forward to all of the clients
				# in the room 
				# if you are not in a room, this returns an error message:
				if(self.room == None):
					# this is the fail case:
					reason = 'You shout into the void and hear nothing but silence.'
					msg = BASE + (len(reason) + 1).to_bytes(4, byteorder="big")
					msg += b'\xfe\x01' + reason.encode()
					self.send(msg)
				else:
					# this is the success case, we want to collect and forward the message
					# first we want to decode the message to extract the 
					# we will be reading in a room and a message
					room_length = 0
					room = ''
					message_length = 0
					message = ''
					check = True
					state = 'ROOM_LENGTH'

					for i in range(0, len(payload)):
						c = payload[i]
						if(state == 'ROOM_LENGTH'):
							room_length = c
							state = 'ROOM'
						elif(state == 'ROOM'):
							room += chr(c)
							room_length -= 1
							if(room_length == 0):
								state = 'MESSAGE_LENGTH'
						elif(state == 'MESSAGE_LENGTH'):
							if(check):
								check = False
								message_length = int.from_bytes(payload[i:i+1], byteorder="big")
							else:
								state = 'MESSAGE'
						elif(state == 'MESSAGE'):
							message += chr(c)
							message_length -= 1

					# now we have the room and message being sent (why do we need the room?)
					# first we can send an ack to the client sending the message
					msg = BASE + (1).to_bytes(4, byteorder="big") + b'\xfe\x00'
					self.send(msg)

					# now we want to construct a message to send to all other clients
					# in the room
					msg = BASE + (len(room) + 1 + len(self.name) + 1 + len(message) + 2).to_bytes(4, byteorder="big")
					msg += b'\x1d' 
					msg += len(room).to_bytes(1, byteorder="big") + room.encode()
					msg += len(self.name).to_bytes(1, byteorder="big") + self.name.encode()
					msg += len(message).to_bytes(2, byteorder="big") + message.encode()

					# now we want to get every client in the room and send it to them
					# with the exception of the current client
					with self.room.CURR_LOCK:
						for client in self.room.clients:
							if(client != self):
								client.send(msg)











# <===================================================================================> #
# server setup and creation:
if(len(sys.argv) < 3 or sys.argv[1] != '-p'):
	print("Must provide port flag.")
	exit()

port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', port)
sock.bind(server_address)

sock.listen(1)

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    # we have a server

    # now we want to get the id, however we need to be attentitive of threads that
    # drop off the server.
    with CLIENT_LOCK:
	    i = 0
	    while(True):
	    	if(not 'rand' + str(i) in clients):
	    		c = Client(i)
	    		clients['rand' + str(i)] = c
	    		clients_order.add(c)
	    		break

	    	i += 1

	    # we have a valid id
	    Thread(target = clients['rand' + str(i)].handle_client, args = (connection, client_address)).start()
# <==================================================================================> #