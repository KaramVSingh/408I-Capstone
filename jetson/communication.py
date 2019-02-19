import serial

class Communication:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM0')

	def send(self, message):
		self.ser.write(message)
	
	def read(self):
		if self.ser.in_waiting:
			return self.ser.readline()
		else:
			return None

	def close(self):
		self.ser.close()
