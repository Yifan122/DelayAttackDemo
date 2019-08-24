import socket

class Connection(object):
    def __init__(self, ipDst, portDst):
        self.ipDst = ipDst
        self.portDst = portDst

    def createConnection(self):
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mysocket.connect((self.ipDst, self.portDst))

    def sendPacket(self, packet):
        self.mysocket.send(packet)

    def close(self):
        self.mysocket.close()
