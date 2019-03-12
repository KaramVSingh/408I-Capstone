import recognition
import communication

# run.py should house all of the commands that we will be using. It will do this in a hwile loop

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
