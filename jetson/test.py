import serial
import time
ser = serial.Serial('/dev/ttyACM2')  # open serial port
time.sleep(5)
print(ser.name)         # check which port was really used
<<<<<<< HEAD
while True:
	ser.write(b'0');
	print(ser.read())
=======

while True:
	ser.write(b'0');
	time.sleep(3)
	print('hello')
>>>>>>> c8ae64367950c8e0a72bb594b515e334cbde4041

ser.close()
'''
import serial
import time

SLEEP_TIME = 3

class Communication:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM1')
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

comm = Communication();
while(True):
	comm.send(b'0')
	print('hello')
'''
