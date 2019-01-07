import numpy as np
from Packet import Packet
import random

# np.random.seed(2)

class EdgeServer:

    def __init__(self, serverId, channel, totalSimulationTime, processRate = 10):
        self.serverId = serverId
        self.ageList = []
        self.channel = channel
        self.totalSimulateTime = totalSimulationTime
        self.pendingPackets = []
        self.carWaitingRooms = {}
        self.isBusy = [False for _ in range(totalSimulationTime)]
        self.policyList = ('FIFO', 'LCFS', 'minAge', 'maxAge', 'maxCarAgeDrop', 'randomPick')
        self.policy = self.policyList[4]
        self.isPreemption = True
        self.carLastUpdateTimeStamp = {}
        self.time = 0
        self.processRate = processRate

    def run(self, time, policy):
        self.time = time
        if not self.isServerBusy(time) and self.pendingPackets:
            self.process(time, policy)

    def process(self, time, policy):
        nextPacket = self.getNextPacket(policy)
        # processTime = self.processRate
        processTime = max(1, int(np.random.exponential(scale=self.processRate, size=1)[0])) # ms
        # processTime = np.random.exponential(scale=self.processRate * 1000, size=1)[0]  # ms

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
                for p in self.pendingPackets:
                    if p == prevPacket:
                        self.pendingPackets.remove(p)
                        break
                self.carWaitingRooms[packet.srcId][0] = packet

        self.pendingPackets.append(packet)

    def randomPick(self):
        return random.choice(self.pendingPackets)

    def FIFO(self):
        return self.pendingPackets[0]

    def LCFS(self):
        return self.pendingPackets[-1]

    def minAge(self):
        nextPacket = None
        minAge = float('inf')
        for packet in self.pendingPackets:
            if packet.age <= minAge:
                minAge = packet.age
                nextPacket = packet
        return nextPacket

    # def maxAge(self):
    #     nextPacket = None
    #     maxAge = -float('inf')
    #     for packet in self.pendingPackets:
    #         if packet.age >= maxAge:
    #             maxAge = packet.age
    #             nextPacket = packet
    #     return nextPacket

    def maxAge(self):
        nextPacket = None
        maxCarAge = -float('inf')
        for packet in self.pendingPackets:
            if packet.srcId not in self.carLastUpdateTimeStamp:
                self.carLastUpdateTimeStamp[packet.srcId] = packet.timestamp
            if self.time - self.carLastUpdateTimeStamp[packet.srcId] >= maxCarAge:
                maxCarAge = self.time - self.carLastUpdateTimeStamp[packet.srcId]
                nextPacket = packet
        return nextPacket

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
        elif policy == 'LCFS':
            packet = self.LCFS()
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
        elif policy == 'randomPick':
            packet = self.randomPick()

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
