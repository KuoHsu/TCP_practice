from socket import *
serverIP = '127.0.0.1'
serverPort = 8080
clientSocket = socket(AF_INET, SOCK_DGRAM)
while True:
    inputMsg = input("input some english sentence message: ").encode("UTF-8")
    clientSocket.sendto(inputMsg, (serverIP, serverPort))
    recvMsg, serverAddress = clientSocket.recvfrom(4096)
    recvMsg = recvMsg.decode("UTF-8")
    print("get server-msg %s from %s" % (recvMsg, serverAddress))
