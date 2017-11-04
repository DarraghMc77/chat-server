import socket
import sys

portNum = int(sys.argv[1])
request = raw_input("Input message: ")
request = request + "\n"
sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = ('localhost', portNum)
sck.connect(serverAddr)
join = "JOIN_CHATROOM: lads\nCLIENT_IP: 127.0.0.1\nPORT: 8000\nCLIENT_NAME: darragh"
leave = "LEAVE_CHATROOM: lads\nJOIN_ID: 13352\nCLIENT_NAME: darragh"

try:
    ## Test joining chat room
    sck.sendall(join)
    data = sck.recv(4096)
    print data

    ## Test leaving chat room
    sck.sendall(leave)
    data2 = sck.recv(4096)
    print data2
finally:
    sck.close()