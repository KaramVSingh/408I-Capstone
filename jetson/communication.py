import serial
import time

SLEEP_TIME = 3
ser = serial.Serial('/dev/ttyACM0')
time.sleep(SLEEP_TIME)

def send(message):
	print('sending ' + str(message))
	ser.write(message)

def read():
	if ser.in_waiting:
		return ser.readline()
	else:
		return None

def close():
	ser.close()

'''
class Communication:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM0')
		time.sleep(SLEEP_TIME)

	def send(self, message):
		print('sending ' + str(message))
		self.ser.write(message)
	
	def read(self):
		if self.ser.in_waiting:
			return self.ser.readline()
		else:
			return None

	def close(self):
		self.ser.close()
'''
