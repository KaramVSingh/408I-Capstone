from recognition import Recognition
from communication import Communication

#rec = Recognition()
comm = Communication()

#rec.begin()
while True:
	get = comm.read()
	if(get):
		print(get)
