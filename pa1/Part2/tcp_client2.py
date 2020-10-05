from socket import *
import sys
import time
import csv
import matplotlib.pyplot as plt

serverName, serverPort = sys.argv[1], int(sys.argv[2])
BUFFERSIZE = 1024

def receive(socket):
    reply = ""
    while True:
        reply += socket.recv(BUFFERSIZE).decode()
        if (reply[-1] == "\n"):
            break
    return reply

def performanceTest(socket):
    # Phase 1: CSP
    print("\nConnection setup phase started...")
    cspFmt = "s<WS><MEASUREMENT TYPE><WS><NUMBER OF " + \
                "PROBES><WS><MESSAGE SIZE><WS><SERVER DELAY>\n"
    # print("Input a CSP message with the following format\n({}): ".format(cspFmt), end = "", flush = True)
    # cspStr = sys.stdin.readline()
    cspStr = input("Input a CSP message with the following format\n({}): ".format(cspFmt))
    cspStr += "\n"

    # Get parameters needed in phase 2
    cspFields = cspStr.rstrip().split()
    measurementType = cspFields[1]
    numOfProbes = int(cspFields[2])
    msgSize = int(cspFields[3])
    delay = float(cspFields[4])

    socket.sendall(cspStr.encode())

    reply = receive(socket)
    print(reply)

    if (reply == "404 ERROR: Invalid Connection Setup Message"):
        return

    # Phase 2: MP
    print("\nMeasurement phase started...")
    results = []

    for i in range(numOfProbes):
        # Generate bytes according to the message size
        payload = "?" * msgSize
        mpStr = "m {} {}\n".format(i + 1, payload)
        startTime = time.time()
        socket.sendall(mpStr.encode())

        reply = receive(socket)
        endTime = time.time()
        print(reply)
        
        if (reply == "404 ERROR: Invalid Measurement Message"):
            return

        results.append(endTime - startTime)
    

    # RTT/Throughput measurement
    # totalRtt = endTime - startTime - numOfProbes * delay
    # avgTput = (msgSize * 8 * numOfProbes) / totalRtt
    records = results.copy()
    records.append(measurementType)
    records.append(msgSize)
    records.append(delay)

    if (measurementType == "tput"):
        # save the data for visualization
        with open('TPUT.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(records)
        print("Average throughput of this link is {:0.3f} Mbps".format(1e-6 * sum([msgSize * 8 / res for res in results]) / len(results)))
    else:
        with open('RTT.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(records)
        print("Average round-trip time of this link is {:0.3f} ms".format(1e3 * sum(results) / len(results)))

    # Phase 3: CTP
    print("\nConnection termination started...")
    socket.sendall("t\n".encode())

    reply = receive(socket)
    print(reply)
    print("\nDisconnected from the server.")
    

# Ipv4 with TCP protocol
with socket(AF_INET, SOCK_STREAM) as clientSocket:
    clientSocket.connect((serverName, serverPort))
    performanceTest(clientSocket)


    