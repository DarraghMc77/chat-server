import os, sys, thread, socket
from concurrent.futures import ThreadPoolExecutor

CONN_QUEUE = 50
BUFFER_SIZE = 4096
ROOMS = {}
ROOMNAMES = {}
ROOMREFS = []
roomnum = 0
clientnum = 0


class ChatRoom:
    def __init__(self, name):
        self.name = name
        print self.name
        self.clientList = []  # replace with dictionary containing clientid: clientSocket

    def addClient(self, clientSocket):
        if clientSocket not in self.clientList:
            self.clientList.append(clientSocket)
            print self.clientList
        else:
            print "Client in chat room"

    def removeClient(self, clientSocket):
        print "here3"
        if clientSocket in self.clientList:
            self.clientList.remove(clientSocket)
            print self.clientList
        else:
            print "Client not in room"

    def sendMessage(self, message):
        print self.clientList
        print message
        for person in self.clientList:
            print message
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


def getRoom():
    global roomnum
    return roomnum


def incrementRoom():
    global roomnum
    roomnum = roomnum + 1


def getClient():
    global clientnum
    return clientnum


def incrClient():
    global clientnum
    clientnum = clientnum + 1


def ServerHandler(connection, addr, portNum, s):
    try:
        print 'connection from', addr

        while True:
            print "top of while"
            data = connection.recv(BUFFER_SIZE)
            print 'received "%s"' % data
            text = data[5:len(data)]
            ip = socket.gethostbyname(socket.gethostname())
            print data[0:4]

            ######## join chatroom ####################
            if data[0:13] == "JOIN_CHATROOM":
                tags = requestHandler(data)
                print tags
                roomnumber = getRoom()
                print roomnumber

                if tags[0] not in ROOMS:
                    tempRoom = ChatRoom(tags[0])
                    ROOMS[tags[0]] = tempRoom
                    ROOMREFS.append(tags[0])
                    ROOMNAMES[tags[0]] = roomnumber
                    print "here"
                    incrementRoom()
                print "here"

                ROOMS[tags[0]].addClient(connection)
                roomRef = ROOMNAMES[tags[0]]
                joinId = getClient()
                incrClient()
                joinResponse = "JOINED_CHATROOM: %s\nSERVER_IP: %s\nPORT: %s\nROOM_REF: %s\nJOIN_ID: %d\n" % (
                tags[0], ip, tags[2], roomRef, joinId)
                print joinResponse
                connection.sendall(joinResponse)
                print "here"
                joinMessage = "CHAT: %s\nCLIENT_NAME: %s\nMESSAGE: %s has joined this chatroom\n\n" % (
                roomRef, tags[3], tags[3])
                print "here2"
                ROOMS[tags[0]].sendMessage(joinMessage)

            ########### Leave chatroom ####################
            elif data[0:14] == "LEAVE_CHATROOM":
                tags = requestHandler(data)
                print tags
                numba = int(tags[0])
                room = ROOMREFS[numba]
                print room
                ROOMS[room].removeClient(connection)
                print "here1"
                leaveResponse = "LEFT_CHATROOM: %s\nJOIN_ID: %s\n" % (tags[0], tags[1])
                print "here"
                print leaveResponse
                connection.sendall(leaveResponse)

                leaveMessage = "CHAT: %s\nCLIENT_NAME: %s\nMESSAGE: %s has left this chatroom\n\n" % (
                tags[0], tags[2], tags[2])
                ROOMS[room].sendMessage(leaveMessage)
                connection.sendall(leaveMessage)
                print "leave finished"

            ########### send message to chatroom ##########
            elif data[0:4] == "CHAT":
                tags = requestHandler(data)
                print tags
                numba = int(tags[0])
                room = ROOMREFS[numba]
                print tags
                chatMessage = "CHAT: %s\nCLIENT_NAME: %s\nMESSAGE: %s\n\n" % (tags[0], tags[2], tags[3])
                print chatMessage
                ROOMS[room].sendMessage(chatMessage)

            ########## Disconnect ########################
            elif data[0:10] == "DISCONNECT":
                tags = requestHandler(data)
                for room in ROOMS:
                    room.removeClient(connection)
                connection.close()

            ########## HELO message ######################
            elif data[0:4] == "HELO":
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
    roomName = roomProcessed[14:len(roomProcessed)]
    tags.append(roomName)

    ipProcessed = message.rsplit('\n', 2)[0]
    ip = ipProcessed[(len(roomProcessed) + 11):len(ipProcessed)]
    tags.append(ip)

    portProcessed = message.rsplit('\n', 1)[0]
    port = portProcessed[(len(ipProcessed) + 6):len(portProcessed)]
    tags.append(port)

    clientName = message[(len(portProcessed) + 13):len(message)]
    tags.append(clientName)
    return tags


def requestHandler(message):
    message_lines = message.split('\n')
    tags = []
    for line in message_lines:
        if line:
            tag = line.split(':')[1]
            tags.append(tag)
    print tags
    return tags


# handle client sending message to chatroom
def sendMessage(message):
    tags = []

    roomProcessed = message.rsplit('\n', 5)[0]
    roomName = roomProcessed[5:len(roomProcessed)]
    tags.append(roomName)

    idProcessed = message.rsplit('\n', 4)[0]
    clId = idProcessed[(len(roomProcessed) + 9):len(idProcessed)]
    tags.append(clId)

    clNameProcessed = message.rsplit('\n', 3)[0]
    clName = clNameProcessed[(len(idProcessed) + 13):len(clNameProcessed)]
    tags.append(clName)

    clientMessage = message[(len(clNameProcessed) + 9):len(message)]
    tags.append(clientMessage)
    return tags


# handle message for client leaving chatroom
def leaveChatRoom(message):
    tags = []

    roomProcessed = message.rsplit('\n', 2)[0]
    roomName = roomProcessed[15:len(roomProcessed)]
    tags.append(roomName)

    idProcessed = message.rsplit('\n', 1)[0]
    clId = idProcessed[(len(roomProcessed) + 9):len(idProcessed)]
    tags.append(clId)

    clientName = message[(len(idProcessed) + 13):len(message)]
    tags.append(clientName)
    return tags

if __name__ == '__main__':
    start()