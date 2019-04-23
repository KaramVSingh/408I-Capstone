from Client import *

open_service('Robot-Robot')
send_room_message('wow')
print(str(get_messages()))
close_service()