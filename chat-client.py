import socket
import sys

portNum = int(sys.argv[1])
request = raw_input("Input message: ")
request = request + "\n"
sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = ('localhost', portNum)
sck.connect(serverAddr)

try:
		sck.sendall(request)
		data = sck.recv(4096)
		print data
finally:
	sck.close()
