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
        self.policyList = ('FIFO', 'FCLS')
        self.policy = 'FIFO'

    def run(self, time):
        if not self.isServerBusy(time) and self.pendingPackets:
            self.process(time)

    def receivePacket(self, packet):
        self.pendingPackets.append(packet)


    def FIFO(self):
        return self.pendingPackets.pop(0)

    def FCLS(self):
        return self.pendingPackets.pop()

    def minAge(self):
        nextPacket = None
        minAge = float('inf')
        for packet in self.pendingPackets:
            if packet.age < minAge:
                minAge = packet.age
                nextPacket = packet
        return nextPacket

    def maxAge(self):
        nextPacket = None
        maxAge = -float('inf')
        for packet in self.pendingPackets:
            if packet.age > maxAge:
                maxAge = packet.age
                nextPacket = packet
        return nextPacket

    def getNextPacket(self, policy):
        if policy == 'FIFO':
            return self.FIFO()
        elif policy == 'FCLS':
            return self.FCLS()
        elif policy == 'maxAge':
            return self.maxAge()
        elif policy == 'minAge':
            return self.minAge()

        return


    def sendPacket(self, destination, packet):
        self.channel.forwardPacket(destination, packet)

    def process(self, time):
        nextPacket = self.getNextPacket(self.policy)

        processTime = int(np.random.exponential(scale=2, size=1)[0]) # ms

        self.reserveServer([time+x for x in range(processTime)])

        updatePacket = Packet(nextPacket.packetId, self.serverId, nextPacket.srcId, nextPacket.size, 1, time+processTime)
        self.sendPacket(nextPacket.srcId, updatePacket)


    def isServerBusy(self, time):
        return self.isBusy[time]

    def reserveServer(self, times):
        for time in times:
            if time < len(self.isBusy):
                self.isBusy[time] = True
