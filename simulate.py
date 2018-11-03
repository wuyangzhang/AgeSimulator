import random
from channel import Channel
from edgeServer import EdgeServer
from SelfCar import SelfCar


instanceIdMapping = {}
carNum = 10
totalSimulateTime = 5 * 60 * 1000 # 5 min
random.seed(10)
cars = []
resolutions = [720, 1080, 2000, 4000]
speeds = [x for x in range(10, 100, 10)]
intervals = [x for x in range(10, 100, 10)] # fps


channel = Channel(2000) # Mbps
for i in range(carNum):

    car = SelfCar(i, startTime = random.randint(0, totalSimulateTime // 5) ,
                  endTime = random.randint(totalSimulateTime - totalSimulateTime // 5, totalSimulateTime),
                  totalSimulationTime = totalSimulateTime,
                  resolution = random.choice(resolutions),
                  speed = random.choice(speeds),
                  sendingInterval = 1000//random.choice(intervals),
                  channel = channel)

    instanceIdMapping[i] = car
    cars.append(car)

serverId = 10001
edgeServer = EdgeServer(serverId, channel, totalSimulateTime)
instanceIdMapping[serverId] = edgeServer
channel.setInstanceMap(instanceIdMapping)
cars[0].run(serverId)

# for car in cars:
#     car.run(edgeServer.serverId)
