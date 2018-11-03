
class Channel:

    def __init__(self, bw):
        self.bandwidth = bw # Mbps
        self.instanceMap = None

    def setInstanceMap(self, instanceMap):
        self.instanceMap = instanceMap

    def forwardPacket(self, destinationId, packet):
        if destinationId not in self.instanceMap:
            return
        forwardTime = self.forwardTime(packet)
        packet.addAging(forwardTime)
        destination = self.instanceMap[destinationId]
        destination.receivePacket(packet)

    def forwardTime(self, packet):
        return int(packet.getSize() * 8 / float(self.bandwidth) * 1000) # ms