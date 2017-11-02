import socket
import sys

portNum = int(sys.argv[1])
request = raw_input("Input message: ")
request = request + "\n"
sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = ('localhost', portNum)
sck.connect(serverAddr)
message = "JOIN_CHATROOM: lads\nCLIENT_IP: 127.0.0.1\nPORT: 8000\nCLIENT_NAME: Darragh"

try:
		sck.sendall(message)
		data = sck.recv(4096)
		print data
finally:
	sck.close()
