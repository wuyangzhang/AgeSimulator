import random
import numpy as np
from channel import Channel
from edgeServer import EdgeServer
from SelfCar import SelfCar
from PlotHelper import plotSingleCurve, plotAvgAOI, plotSampleAge, plotBox
import matplotlib.pyplot as plt
import json
import glob
import time

resolutions = [720, 1080, 2000, 4000]
speeds = [x for x in range(10, 100, 10)] # priority?
intervals = [x for x in range(10, 50, 10)] # fps

# random.seed(10)

policyList = ('maxCarAgeDrop', 'FIFO', 'LCFS', 'maxAge', 'randomPick')

class Simulation:
    def __init__(self, carNum = 10, serverProcessRate=5, trafficRate=50):
        self.cars = []
        self.instanceIdMapping = {}
        self.channel = None
        self.totalSimulateTime = 10 * 60 * 1000 # 1 min / unit - ms
        self.serverId = 10001
        self.trafficRate = trafficRate
        self.initChannel()
        self.initCars(carNum)
        self.initServer(serverProcessRate)

    def initCars(self, carNum):

        for i in range(carNum):
            car = SelfCar(i, startTime = 1,
                          endTime = self.totalSimulateTime,
                          resolution = 720,
                          speed = 10,
                          sendingInterval =  self.trafficRate, #+ random.randint(1, 20), #fps self.trafficRate,
                          channel = self.channel)

            self.instanceIdMapping[i] = car
            self.cars.append(car)

    def initServer(self, processRate = 1):
        self.edgeServer = EdgeServer(self.serverId, self.channel, self.totalSimulateTime, processRate)
        self.instanceIdMapping[self.serverId] = self.edgeServer

    def initChannel(self, bw = 1024 * 1000):
        self.channel = Channel(bw)  # Mbps
        self.channel.setInstanceMap(self.instanceIdMapping)


    def runSimulate(self, policy):
        # start simulate!
        for time in range(self.totalSimulateTime):
            random.shuffle(self.cars)
            for car in self.cars:
                car.run(self.serverId, time)
            self.channel.run(time)
            self.edgeServer.run(time, policy)

    def collectAOI(self):
        res = []
        for i in range(len(self.cars)):
            res.append(self.cars[i].ageList)
            # res.append(self.cars[i].getAverageAge())
        return res


def find_avg_aoi(path):

    policyList = ['maxCarAgeDrop', 'FIFO', 'LCFS', 'maxAge', 'randomPick']
    results = {}
    for file in glob.glob(path + '_*'):
        with open(file) as f:
            aoi_policy_dic = json.load(f)

        policy_aoi = {}
        for policy in aoi_policy_dic:
            res = []
            # res = 0
            for car in aoi_policy_dic[policy]:
                res += car
            policy_aoi[policy] = sum(res) / len(res)
            # policy_aoi[policy] = res
            #print('file {}, age list {}'.format(file, res))
        results[file] = policy_aoi

    with open(path + '.log', 'w+') as file:
        file.write(json.dumps(results))

def testServerProcessRate():

    for i in [1, 2, 5, 10, 20, 33]:
        res = {}
        for policy in policyList:
            print(policy)
            simulation = Simulation(carNum=10, serverProcessRate=i)
            simulation.runSimulate(policy)
            res[policy] = simulation.collectAOI()

        with open('processRate_' + str(i) + '_ms.log', 'w+') as file:
            file.write(json.dumps(res))


def testTrafficRate(testTrafficRateRange):

    for i in testTrafficRateRange:
        print("Traffice Rate: ", i)
        res = {}
        for policy in policyList:
            # print(policy)
            simulation = Simulation(carNum=5, serverProcessRate=10, trafficRate=i)
            simulation.runSimulate(policy)
            res[policy] = simulation.collectAOI()
        with open('trafficRate_' + str(i) + '_ms.log', 'w+') as file:
            file.write(json.dumps(res))


def testUserNum():
    for i in [2, 4, 6, 8, 10, 12, 14, 16]:
        res = {}
        for policy in policyList:
            simulation = Simulation(carNum=i, serverProcessRate=10, trafficRate=30)
            simulation.runSimulate(policy)
            res[policy] = simulation.collectAOI()

        with open('userCnt_' + str(i) + '_ms.log', 'w+') as file:
            file.write(json.dumps(res))


def printSampleAge(carNum=2):

    policy = 'maxCarAgeDrop'
    simulation = Simulation(carNum=carNum, serverProcessRate=5)
    simulation.runSimulate(policy)
    res = simulation.collectAOI()

    with open('sampleAge.log', 'w+') as file:
        file.write(json.dumps(res))


startTime = time.time()

#
# testServerProcessRate()
# find_avg_aoi('processRate')
# plotAvgAOI('processRate.log', [1, 2, 5, 10, 20, 33] , 'edge server processing rate for a single frame (ms)', 'average AOI (ms)')

"""Varying traffic rate from each user"""
testTrafficRateRange = [10 * (i + 1) for i in range(6)]
testTrafficRate(testTrafficRateRange)
find_avg_aoi('trafficRate')
plotAvgAOI('trafficRate.log',testTrafficRateRange, 'Average User Inter-Update Time (ms)', 'Average Age (ms)')

# testUserNum()
# find_avg_aoi('userCnt')
# plotAvgAOI('userCnt.log', [2, 4, 6, 8, 10, 12, 14, 16] , 'total user count', 'average AOI (ms)')


# printSampleAge(2)
# plotSampleAge('sampleAge.log', 'time slot', 'AOI (ms)')

# printSampleAge(10)
# plotBox('sampleAge.log', 'user id', 'AOI (ms)')






# res = []
# for i in range(10000):
#     a = int(np.random.exponential(scale=5, size=1)[0])
#     res.append(a)
#
# avg = sum(res) / len(res)
# print(avg)


#res = cars[0].getEnd2EndLatency()
#plotSingleCurve(res)

# isum = 0
# for car in cars:
#     res = car.getAgeHist()
#     print('Car AoI: ', np.mean(res))
#     isum += np.mean(res)
# print('Mean Car AoI: ', isum / len(cars))
#
# plt.figure()
# # res = [car.getAgeHist() for car in cars]
# # print(res)
# # plt.plot(res)
# # plt.show()
# i = 0
# for car in cars[:]:
#     res = car.getAgeHist()
#     # instantMeanAge = []
#     # for i, val in enumerate(instantAge):
#     #     print(i)
#     #     instantMeanAge.append( np.mean(instantAge[:i]) )
#     plt.plot(res, label = i)
#     i += 1
# plt.ylabel('Age')
# plt.legend()
# plt.savefig('agepath.png')

# for car in cars:
#     print(car.getEnd2EndLatency())

elapsedTime = time.time() - startTime
print('Execution time: ', elapsedTime)