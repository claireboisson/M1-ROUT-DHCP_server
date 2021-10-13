from socket import *

MAX_BYTES = 8192
serverPort = 67
clientPort = 1234

""" ----- CLIENT SETTINGS ----- """
dest = ('255.255.255.255', serverPort)
socket = socket(AF_INET, SOCK_DGRAM)
socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
socket.bind(('', clientPort))

message = { "1": "Available addresses", "2": "Addresses currently in use", "3": "Memory of couples MAC/IP"}
b = False

while b is False:
	rcv = None
	print('\n')
	print("Please enter the information you want to see")
	print("  -Available addresses : 1")
	print("  -Addresses currently in use : 2")
	print("  -Memory of couples MAC/IP : 3")
	print("  -All the information : 4")
	d = input('The entry : ')
	if(d not in message) and (d!="4"):
		print("You did not put a correct number")
		exit(-1)
	print('\n')
	if d != "4" :
		data = d.encode('utf-8')
		socket.sendto(data, dest)
		rcv, address = socket.recvfrom(MAX_BYTES)
		for key in message:
			if key == d:
				print(message[key], " : ", rcv.decode('utf-8'))
				break
			else:
				pass
	else:
		for keys in message:
			data = keys.encode('utf-8')
			socket.sendto(data, dest)
			rcv, address = socket.recvfrom(MAX_BYTES)
			print(message[keys], " : ", rcv.decode('utf-8'))

	print('\n')
	inp = input("Do you want another information ? (y/n) ")
	while (inp != "y") and (inp != "n"):
		inp = input("Do you want another information ? (y/n) ")
	if inp == 'n':
		b = True
