import serial
import time

SLEEP_TIME = 3

class Communication:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM2')
		time.sleep(SLEEP_TIME)

	def send(self, message):
		self.ser.flush()
		print('sending')
		self.ser.write(message)
		print('sent')
		self.ser.flush()
		print('flushed')
	
	def read(self):
		if self.ser.in_waiting:
			return self.ser.readline()
		else:
			return None

	def close(self):
		self.ser.close()
