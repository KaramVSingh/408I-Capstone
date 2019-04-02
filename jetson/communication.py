import serial
import time

SLEEP_TIME = 3
ser = serial.Serial('/dev/ttyACM0')
time.sleep(SLEEP_TIME)

def send(message):
	print('sending ' + str(message))
	ser.write(message)
	print('sent')

def read():
	if ser.in_waiting:
		return ser.readline()
	else:
		return None

def close():
	ser.close()

