import os, sys, thread, socket
from concurrent.futures import ThreadPoolExecutor

CONN_QUEUE = 50
BUFFER_SIZE = 4096
ROOMS = {}


class ChatRoom:
    def __init__(self, name):
        self.name = name
        print self.name
        self.clientList = []  # replace with dictionary containing clientid: clientSocket

    def addClient(self, clientSocket):
        if clientSocket not in self.clientList:
            self.clientList.append(clientSocket)
            print self.clientList
        # send client id has joined chat room
        else:
            print "Client in chat room"

    def removeClient(self, clientSocket):
        if clientSocket in self.clientList:
            self.clientList.remove(clientSocket)
            print self.clientList
        else:
            print "Client not in room"

    def sendMessage(self, message):
        for person in self.clientList:
            person.sendall(message)


def start():
    hostName = ''
    portNum = int(sys.argv[1])
    print "Server Running on port: ", portNum

    try:
        pool = ThreadPoolExecutor(128)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((hostName, portNum))
        s.listen(CONN_QUEUE)

    except:
        s.close()
        print "Could not open socket"
        sys.exit(1)

    while 1:
        try:
            connection, addr = s.accept()
            pool.submit(ServerHandler, connection, addr, portNum, s)
        except KeyboardInterrupt:
            print "server closing"
            connection.close()
            s.close()
            sys.exit(1)
    s.close()


def ServerHandler(connection, addr, portNum, s):
    try:
        print 'connection from', addr

        while True:
            data = connection.recv(BUFFER_SIZE)
            print 'received "%s"' % data
            message = data[0:4]
            text = data[5:len(data)]
            ip = socket.gethostbyname(socket.gethostname())
            print ip
            print data[0:13]

            ######## join chatroom ####################
            if data[0:13] == "JOIN_CHATROOM":
                roomProcessed = data.rsplit('\n', 3)[0]
                roomName = roomProcessed[15:len(roomProcessed)]

                ipProcessed = data.rsplit('\n', 2)[0]
                ip = ipProcessed[32:len(ipProcessed)]

                portProcessed = data.rsplit('\n', 1)[0]
                port = portProcessed[47:len(portProcessed)]

                clientName = data[65:len(data)]

                print roomName
                print ip
                print port
                print clientName

                if roomName not in ROOMS:
                    tempRoom = ChatRoom(roomName)
                    ROOMS[roomName] = tempRoom
                    print ROOMS

                ROOMS[roomName].addClient(connection)

                response1 = "JOINED_CHATROOM: %s\nCLIENT_IP: %s\nPORT: %s\nCLIENT_NAME: %s" % (
                roomName, ip, portNum, clientName)
                print response1
                connection.sendall(response1)

            # ROOMS[roomName].sendMessage("%s has joined the chat room" % (clientName))


            ########### send message to chatroom ##########



            elif message == "HELO":
                response = "%sIP:%s\nPort:%d\nStudentID:13328582\n" % (data, ip, portNum)
                connection.sendall(response)

            ########### kill server ######################
            elif data == "KILL_SERVICE\n":
                print "server closing"
                connection.close()
                s.close()
                sys.exit(1)

            ######### other messages to server #############
            elif (len(data) > 0):
                # handle other messages
                print data

            ######## no more data to receive from client ##########
            else:
                print 'no more data from', addr[0]
                break
    finally:
        connection.close()


# handle message for client joining chat room
def joinChatRoom(message):
    roomProcessed = message.rsplit('\n', 3)[0]
    roomName = roomProcessed[15:len(roomProcessed)]

    ipProcessed = message.rsplit('\n', 2)[0]
    ip = ipProcessed[(len(roomProcessed) + 12):len(ipProcessed)]

    portProcessed = message.rsplit('\n', 1)[0]
    port = portProcessed[(len(ipProcessed) + 7):len(portProcessed)]

    clientName = message[(len(portProcessed) + 14):len(message)]


# handle client sending message to chatroom
def sendMessage(message):
    roomProcessed = message.rsplit('\n', 5)[0]
    roomName = roomProcessed[6:len(roomProcessed)]

    idProcessed = message.rsplit('\n', 4)[0]
    id = idProcessed[(len(roomProcessed) + 10):len(idProcessed)]

    clNameProcessed = message.rsplit('\n', 3)[0]
    clName = clNameProcessed[(len(idProcessed) + 14):len(clNameProcessed)]

    clientMessage = message[(len(clNameProcessed) + 10):len(message)]


def main():
    start()


if __name__ == '__main__':
    main()