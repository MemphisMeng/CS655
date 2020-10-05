from socket import *
from threading import Thread
from datetime import datetime
import sys
import time

class ServerThread(Thread):
    def __init__(self, connSocket, clientName, clientPort):
        super().__init__()
        self.connSocket = connSocket
        self.clientName = clientName
        self.clientPort = clientPort
        self.buffersize = 1024
        self.setDaemon(True) # Thread will be killed after main() terminates

        print("[+] {}: A new client [{}:{}] is connected to the server."
                .format(datetime.now(), self.clientName, self.clientPort))

    def run(self):
        with self.connSocket:
            self.echo()
    
    def echo(self):
        clientMsg = self.receive()
        print("{}: Client [{}:{}]: {}"
                    .format(datetime.now(), self.clientName, 
                            self.clientPort, clientMsg))

        self.connSocket.sendall(bytes(clientMsg, 'utf-8'))
        
        print("[-] {}: Client [{}:{}] has disconnected to the server."
                    .format(datetime.now(), self.clientName, self.clientPort))

    def receive(self):
        reply = ""
        while True:
            reply += self.connSocket.recv(self.buffersize).decode()
            if (reply[-1] == "\n"):
                break
        return reply


serverPort = int(sys.argv[1])

# Ipv4 with TCP protocol
# Start a main thread, listening to any requests from clients
with socket(AF_INET, SOCK_STREAM) as serverSocket:
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Allow reusing of previous addresses
    serverSocket.bind(("", serverPort)) # Set up on localhost
    threads = []

    while True:
        # Three-way handshake
        serverSocket.listen()
        connSocket, client = serverSocket.accept()
        clientName, clientPort = client
        # Add a new server connection socket thread
        serverThread = ServerThread(connSocket, clientName, clientPort)
        serverThread.start()
        threads.append(serverThread)

    for t in threads:
        t.join()