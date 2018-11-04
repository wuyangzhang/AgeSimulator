
class Channel:

    def __init__(self, bw):
        self.bandwidth = bw # Mbps
        self.instanceMap = None
        self.packets = {}

    def run(self, timeSlot):
        if timeSlot in self.packets:
            for packet in self.packets[timeSlot]:
                self.forwardPacket(packet)

    def receivePacket(self, packet):
        transmissionLatency = self.forwardTime(packet)
        packet.addAging(transmissionLatency)

        sendTimeStamp = packet.timestamp+packet.age
        if sendTimeStamp not in self.packets:
            self.packets[sendTimeStamp] = []
        self.packets[sendTimeStamp].append(packet)

    def setInstanceMap(self, instanceMap):
        self.instanceMap = instanceMap

    def forwardPacket(self, packet):
        destinationId = packet.destId
        if destinationId not in self.instanceMap:
            return
        destination = self.instanceMap[destinationId]
        destination.receivePacket(packet)

    def forwardTime(self, packet):
        return int(packet.getSize() * 8 / float(self.bandwidth) * 1000) # ms