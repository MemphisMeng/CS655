from socket import *
from threading import Thread
from datetime import datetime
import sys
import time
import re

class ServerThread(Thread):
    def __init__(self, connSocket, clientName, clientPort):
        super().__init__()
        self.connSocket = connSocket
        self.clientName = clientName
        self.clientPort = clientPort
        self.setDaemon(True) # Thread will be killed after main() terminates
        self.buffersize = 1024

        # TCP experienments
        self.measurementType = ""
        self.numOfProbes = 0
        self.msgSize = 0
        self.serverDelay = 0.0

        print("[+] {}: A new client [{}:{}] is connected to the server."
                .format(datetime.now(), self.clientName, self.clientPort))

    def run(self):
        with self.connSocket:
            self.performanceTest(debug = True)

    def receive(self):
        reply = ""
        while True:
            reply += self.connSocket.recv(self.buffersize).decode()
            if (reply[-1] == "\n"):
                break
        return reply

    def performanceTest(self, debug = False):
        clientMsg = self.receive()

        packet = clientMsg.rstrip().split()
        # Connection Setup Phase (CSP)
        valid, reply = self.CSP(packet, debug)
        # Send the reply to the client
        self.connSocket.sendall(reply.encode())

        if (not valid):
            print("{}: Client [{}:{}] has disconnected to the server."
                    .format(datetime.now(), self.clientName, self.clientPort))
            return

        # Measurement Phase (MP)
        startTime = time.time()
        for i in range(self.numOfProbes):
            clientMsg = self.receive()

            packet = clientMsg.rstrip().split()
            
            reply = clientMsg # Suppose we will echo back the message
            valid = self.MP(packet, i + 1)
            if (not valid):
                reply = "404 ERROR: Invalid Measurement Message\n"

            # Send the reply to the client
            time.sleep(self.serverDelay)
            self.connSocket.sendall(reply.encode())

            if (not valid):
                print("{}: Client [{}:{}] has disconnected to the server."
                    .format(datetime.now(), self.clientName, self.clientPort))
                return

        # Connection Termination Phase (CTP)
        clientMsg = self.receive()

        packet = clientMsg.rstrip().split()
        valid, reply = self.CTP(packet)

        # Send the reply to the client
        self.connSocket.sendall(reply.encode())
        if (not valid):
            print("{}: Client [{}:{}] has disconnected to the server."
                .format(datetime.now(), self.clientName, self.clientPort))
            return


    def CSP(self, packet, debug = False):
        """
        Connection setup phase

        ---

        @params:

        packet: the probe packet

        debug: flag for printing loggings

        ---

        @return:

        `valid`: Boolean flag indicating the validation status of the packet

        `msg`: The status reply generated from server
        """
        errorMsg = "404 ERROR: Invalid Connection Setup Message\n"
        if (len(packet) != 5 or packet[0] != "s"):
            return False, errorMsg
        if (packet[1] != "rtt" and packet[1] != "tput"):
            return False, errorMsg
        if (not (packet[2].isdigit()) or not (packet[3].isdigit())):
            return False, errorMsg
        # Float number (i.e. 48.35) check
        if (not re.fullmatch("^\d+(\.\d+)?$", packet[4])):
            return False, errorMsg

        self.measurementType = packet[1]
        self.numOfProbes = int(packet[2])
        self.msgSize = int(packet[3])
        self.serverDelay = float(packet[4])

        if (debug):
            print("\n{}: Client [{}:{}]"
                    .format(datetime.now(), self.clientName, self.clientPort))
            print("Connection Setup Phase")
            print("<MEASUREMENT TYPE>: {}".format(self.measurementType.upper()))
            print("<NUMBER OF PROBES>: {}".format(self.numOfProbes))
            print("<MESSAGE SIZE>: {}B".format(self.msgSize))
            print("<SERVER DELAY>: {}s".format(self.serverDelay))
            print()
            
        return True, "200 OK: Ready\n"

    def MP(self, packet, curSeqNum):
        """
        RTT/Throughput measurement phase

        ---

        @params:

        packet: the probe packet

        n: the number of probes

        ---

        @return:

        `valid`: Boolean flag indicating the validation status of the packet
        """
        if (len(packet) != 3 or packet[0] != "m"):
            return False
        if (not (packet[1].isdigit()) or (int(packet[1]) != curSeqNum)):
            return False
        if (len(packet[2]) != self.msgSize):
            return False

        return True

    def CTP(self, packet):
        errorMsg = "404 ERROR: Invalid Connection Termination Message"
        if (len(packet) != 1 or packet[0] != "t"):
            return False, errorMsg
        
        return True, "200 OK: Closing Connection\n"

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