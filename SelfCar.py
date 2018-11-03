from Packet import Packet


class SelfCar:

    def __init__(self, carId, startTime, endTime, resolution, speed, sendingInterval, channel):
        self.carId = carId
        self.ageList = []
        self.startTime = startTime
        self.endTime = endTime
        self.resolution = resolution
        self.speed = speed
        self.sendingInterval = sendingInterval
        self.packetSize = self.calculatePacketSize(self.resolution)
        self.requestId = 0
        self.channel = channel
        self.updates = []
        self.sendSlots = set()
        time = startTime
        while time < endTime:
            self.sendSlots.add(time)
            time += sendingInterval

    def sendPacket(self, serverId):
        packet = self.generatePacket(serverId)
        self.channel.forwardPacket(serverId, packet)
        self.requestId += 1

    def generatePacket(self, serverId):
        return Packet(self.requestId, self.carId, serverId, self.calculatePacketSize(self.resolution), 0, self.time)

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


    def run(self, timeSlot, serverId):
        if timeSlot in self.sendSlots:
            self.sendPacket(serverId)
