import numpy as np
from Packet import Packet


class EdgeServer:

    def __init__(self, serverId, channel, totalSimulationTime):
        self.serverId = serverId
        self.ageList = []
        self.channel = channel
        self.totalSimulateTime = totalSimulationTime
        self.pendingPackets = []
        self.isBusy = [False for _ in range(totalSimulationTime)]


    def run(self, time):
        if not self.isServerBusy(time) and self.pendingPackets:
            self.process(time)

    def receivePacket(self, packet):
        self.pendingPackets.append(packet)


    def getNextPacket(self):
        return self.pendingPackets.pop(0)

    def sendPacket(self, destination, packet):
        self.channel.forwardPacket(destination, packet)

    def process(self, time):
        packet = self.getNextPacket()
        processTime = int(np.random.exponential(scale=20, size=1)[0]) # ms
        self.reserveServer([time+x for x in range(processTime)])
        update = Packet(packet.packetId, self.serverId, packet.srcId, packet.size, 1, time+processTime)
        self.sendPacket(packet.srcId, update)


    def isServerBusy(self, time):
        return self.isBusy[time]

    def reserveServer(self, times):
        for time in times:
            self.isBusy[time] = True
