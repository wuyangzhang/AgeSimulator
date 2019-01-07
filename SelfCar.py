from Packet import Packet
import numpy as np
import random

class SelfCar:

    def __init__(self, carId, startTime, endTime, resolution, speed, sendingInterval, channel):
        self.carId = carId
        self.ageList = [0]
        self.startTime = startTime
        self.endTime = endTime
        self.resolution = resolution
        self.speed = speed
        self.sendingInterval = sendingInterval
        self.packetSize = self.calculatePacketSize(self.resolution)
        self.requestId = 0
        self.channel = channel
        self.updates = []
        self.latencies = {}
        self.sendSlots = set()
        self.receiveCount = 0

        time = startTime
        while time < endTime:
            self.sendSlots.add(time) # + random.randint(-10, 10))
            # time += sendingInterval # Fixed sending interval
            time += max(1, int(np.random.exponential(scale=sendingInterval, size=1)[0])) # Random Exponential sending interval

    def run(self, serverId, timeSlot):
        if self.startTime <= timeSlot:
            self.ageList.append(self.ageList[-1]+1)

        if timeSlot in self.sendSlots:
            self.sendPacket(serverId, timeSlot)

    def sendPacket(self, serverId, timeSlot):
        packet = self.generatePacket(serverId, timeSlot)
        self.updateLatency(packet)
        self.channel.receivePacket(packet)

    def generatePacket(self, serverId, time):
        self.requestId += 1
        return Packet(self.requestId, self.carId, serverId, self.calculatePacketSize(self.resolution), 0, time)

    def calculatePacketSize(self, resolution):
        #MB
        if resolution == 720:
            return 1
        elif resolution == 1080:
            return 1.5
        elif resolution == 2000:
            return 3
        elif resolution == 4000:
            return 4

    def receivePacket(self, packet):
        self.updates.append(packet)
        self.updateLatency(packet)
        self.updateAge(packet)
        self.receiveCount += 1

    def updateAge(self, packet):
        self.ageList.append(packet.age)

    def updateLatency(self, packet):
        packetId, endTime = packet.packetId, packet.timestamp
        if packetId not in self.latencies:
            self.latencies[packetId] = [endTime, endTime, endTime]
            return
        startTime = self.latencies[packetId][0]
        self.latencies[packetId][1] = endTime
        self.latencies[packetId][2] = endTime - startTime

    def getEnd2EndLatency(self):
        return [x[2] for x in self.latencies.values()]

    def getAgeHist(self):
        return self.ageList[:]

    def getAverageAge(self):
        return sum(self.ageList[:]) / len(self.ageList[:])

    def getPenaltyList(self):
        penList = []
        for i in self.ageList:
            penList.append(np.exp(0.05*i))
        return penList