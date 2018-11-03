
class Packet:

    def __init__(self, packetId, srcId, destId, size, type, timestamp):
        self.packetId = packetId
        self.srcId = srcId
        self.destId = destId
        self.size = size
        self.age = 0
        self.type = type
        self.speed = 0
        self.timestamp = timestamp

    def setSpeed(self, speed):
        self.speed = speed

    '''
        unit: MB
    '''
    def getSize(self):
        return self.size

    def getAge(self):
        return self.age

    def addAging(self, agingTime):
        self.age += agingTime
        self.timestamp += agingTime