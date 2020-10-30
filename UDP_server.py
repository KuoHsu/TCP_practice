from socket import *

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('127.0.0.1', serverPort))
print('Server start running..')
while True:
    message, clientAddress = serverSocket.recvfrom(4096)
    message = message.decode("UTF-8")
    print(message)
    print(clientAddress)

    upperMsg = message.upper().encode("UTF-8")
    serverSocket.sendto(upperMsg, clientAddress)
