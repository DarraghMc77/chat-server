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
            print data[0:14]

            ######## join chatroom ####################
            if data[0:13] == "JOIN_CHATROOM":
                tags = joinChatRoom(data)
                print tags

                if tags[0] not in ROOMS:
                    tempRoom = ChatRoom(tags[0])
                    ROOMS[tags[0]] = tempRoom
                    print ROOMS

                ROOMS[tags[0]].addClient(connection)

                joinResponse = "JOINED_CHATROOM: %s\nCLIENT_IP: %s\nPORT: %s\nCLIENT_NAME: %s" % (
                tags[0], ip, tags[2], tags[3])
                print joinResponse
                connection.sendall(joinResponse)

            # joinMessage = "%s has joined the chat room" % (tags[3])
            # ROOMS[tags[0]].sendMessage(joinMessage)

            ########### Leave chatroom ####################
            if data[0:14] == "LEAVE_CHATROOM":
                tags = leaveChatRoom(data)
                print tags

                ROOMS[tags[0]].removeClient(connection)

                leaveResponse = "LEFT_CHATROOM: %s\nJOIN_ID: %s" % (tags[0], tags[1])
                print "here"
                print leaveResponse
                connection.sendall(leaveResponse)

            # leaveMessage = "%s has left the chatroom" % (tags[2])
            # ROOMS[tags[0]].sendMessage(leaveMessage)


            ########### send message to chatroom ##########
            # if data[0:4] == "CHAT":
            #	tags = sendMessage(data)
            #	print tags

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
    tags = []

    roomProcessed = message.rsplit('\n', 3)[0]
    roomName = roomProcessed[15:len(roomProcessed)]
    tags.append(roomName)

    ipProcessed = message.rsplit('\n', 2)[0]
    ip = ipProcessed[(len(roomProcessed) + 12):len(ipProcessed)]
    tags.append(ip)

    portProcessed = message.rsplit('\n', 1)[0]
    port = portProcessed[(len(ipProcessed) + 7):len(portProcessed)]
    tags.append(port)

    clientName = message[(len(portProcessed) + 14):len(message)]
    tags.append(clientName)
    return tags


# handle client sending message to chatroom
def sendMessage(message):
    tags = []

    roomProcessed = message.rsplit('\n', 5)[0]
    roomName = roomProcessed[6:len(roomProcessed)]
    tags.append(roomName)

    idProcessed = message.rsplit('\n', 4)[0]
    clId = idProcessed[(len(roomProcessed) + 10):len(idProcessed)]
    tags.append(clId)

    clNameProcessed = message.rsplit('\n', 3)[0]
    clName = clNameProcessed[(len(idProcessed) + 14):len(clNameProcessed)]
    tags.append(clName)

    clientMessage = message[(len(clNameProcessed) + 10):len(message)]
    tags.append(clientMessage)
    return tags


# handle message for client leaving chatroom
def leaveChatRoom(message):
    tags = []

    roomProcessed = message.rsplit('\n', 2)[0]
    roomName = roomProcessed[16:len(roomProcessed)]
    tags.append(roomName)

    idProcessed = message.rsplit('\n', 1)[0]
    clId = idProcessed[(len(roomProcessed) + 10):len(idProcessed)]
    tags.append(clId)

    clientName = message[(len(idProcessed) + 14):len(message)]
    tags.append(clientName)
    return tags

if __name__ == '__main__':
    start()