from socket import *
from datetime import datetime
import sys

BUFFERSIZE = 1024

def receive(socket):
    reply = ""
    while True:
        reply += socket.recv(BUFFERSIZE).decode()
        if (reply[-1] == "\n"):
            break
    return reply

serverName, serverPort = sys.argv[1], int(sys.argv[2])

# Ipv4 with TCP protocol
with socket(AF_INET, SOCK_STREAM) as clientSocket:
    clientSocket.connect((serverName, serverPort))
    
    sentence = sys.stdin.readline()
    sentence += '\n'
    # Sending bytes object to the server
    clientSocket.sendall(sentence.encode())

    reply = receive(clientSocket)

    print("{}: Server [{}:{}]: {}"
            .format(datetime.now(), serverName, 
                    serverPort, reply))
        




    