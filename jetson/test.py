import serial
ser = serial.Serial('/dev/ttyACM0')  # open serial port
print(ser.name)         # check which port was really used
while True:
	ser.write(b'0');
	print(ser.read())

ser.close()
