import numpy as np
from Packet import Packet

class EdgeServer:

    def __init__(self, serverId, channel, totalSimulationTime):
        self.serverId = serverId
        self.ageList = []
        self.channel = channel
        self.totalSimulateTime = totalSimulationTime
        self.pendingPackets = []
        self.carWaitingRooms = {}
        self.isBusy = [False for _ in range(totalSimulationTime)]
        self.policyList = ('FIFO', 'FCLS', 'minAge', 'maxAge', 'maxCarAgeDrop')
        self.policy = 'maxAge'
        self.isPreemption = True
        self.carLastUpdateTimeStamp = {}
        self.time = 0
        np.random.seed(1)

    def run(self, time):
        self.time = time
        if not self.isServerBusy(time) and self.pendingPackets:
            self.process(time)

    def process(self, time):
        nextPacket = self.getNextPacket(self.policy)

        processTime = int(np.random.exponential(scale=10, size=1)[0]) # ms

        self.reserveServer([time+x for x in range(processTime)])

        updatePacket = Packet(nextPacket.packetId, self.serverId, nextPacket.srcId, nextPacket.size, 1, nextPacket.timestamp)
        updatePacket.addAging(time-nextPacket.timestamp+processTime)

        # update the timestamp of the previously processed packet
        self.updatePreviousProcessedPacketTimestamp(nextPacket)
        self.sendPacket(updatePacket)

        # clear waiting room
        del self.carWaitingRooms[nextPacket.srcId]

    def receivePacket(self, packet):
        if self.isPreemption:
            if packet.srcId not in self.carWaitingRooms:
                self.carWaitingRooms[packet.srcId] = [packet]
            else:
                prevPacket = self.carWaitingRooms[packet.srcId][0]
                for packet in self.pendingPackets:
                    if packet == prevPacket:
                        self.pendingPackets.remove(packet)
                        break
                self.carWaitingRooms[packet.srcId][0] = packet

        self.pendingPackets.append(packet)

    def FIFO(self):
        return self.pendingPackets[0]

    def FCLS(self):
        return self.pendingPackets[-1]

    def minAge(self):
        nextPacket = None
        minAge = float('inf')
        for packet in self.pendingPackets:
            if packet.age <= minAge:
                minAge = packet.age
                nextPacket = packet
        return nextPacket

    def maxAge(self):
        nextPacket = None
        maxAge = -float('inf')
        for packet in self.pendingPackets:
            if packet.age >= maxAge:
                maxAge = packet.age
                nextPacket = packet
        return nextPacket

    def maxCarAge(self):
        pass

    def minCarAge(self):
        pass

    def maxCarAgeDrop(self):
        maxDrop, nextPacket = 0, None
        for packet in self.pendingPackets:
            if packet.srcId not in self.carLastUpdateTimeStamp:
                self.carLastUpdateTimeStamp[packet.srcId] = packet.timestamp
            ageDrop = packet.timestamp - self.carLastUpdateTimeStamp[packet.srcId]
            if ageDrop >= maxDrop:
                maxDrop = ageDrop
                nextPacket = packet
        return nextPacket

    def getNextPacket(self, policy):
        packet = None
        if policy == 'FIFO':
            packet =  self.FIFO()
        elif policy == 'FCLS':
            packet = self.FCLS()
        elif policy == 'maxAge':
            packet = self.maxAge()
        elif policy == 'minAge':
            packet = self.minAge()
        elif policy == 'maxCarAge':
            packet = self.maxCarAge()
        elif policy == 'minCarAge':
            packet = self.minCarAge()
        elif policy == 'maxCarAgeDrop':
            packet = self.maxCarAgeDrop()

        self.pendingPackets.remove(packet)
        return packet


    def sendPacket(self, packet):
        self.channel.receivePacket(packet)


    def updatePreviousProcessedPacketTimestamp(self, packet):
        self.carLastUpdateTimeStamp[packet.srcId] = packet.timestamp

    def isServerBusy(self, time):
        return self.isBusy[time]

    def reserveServer(self, times):
        for time in times:
            if time < len(self.isBusy):
                self.isBusy[time] = True
