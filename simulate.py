import random
import numpy as np
from channel import Channel
from edgeServer import EdgeServer
from SelfCar import SelfCar
from PlotHelper import plotSingleCurve, plotAvgAOI, plotSampleAge, plotBox, plotFairness, plotFairnessCnt, plotAvgPenalty
import matplotlib.pyplot as plt
import json
import glob
import time

import matplotlib.style
import matplotlib as mpl
mpl.style.use('default')

resolutions = [720, 1080, 2000, 4000]
speeds = [x for x in range(10, 100, 10)] # priority?
intervals = [x for x in range(10, 50, 10)] # fps

# random.seed(10)

policyList = ('maxPenalty', 'FIFO', 'LCFS', 'maxAge', 'randomPick')

class Simulation:
    def __init__(self, carNum = 10, serverProcessRate=5, trafficRate=20):
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
                          # sendingInterval = (i+1) * self.trafficRate,
                          channel = self.channel)

            self.instanceIdMapping[i] = car
            self.cars.append(car)

    def collectServiceCount(self):
        res = []
        for car in self.cars:
            res.append(car.receiveCount)
        return res

    def initServer(self, processRate = 1):
        self.edgeServer = EdgeServer(self.serverId, self.channel, self.totalSimulateTime, processRate)
        self.instanceIdMapping[self.serverId] = self.edgeServer

    def initChannel(self, bw = 1024 * 1000):
        self.channel = Channel(bw)  # Mbps
        self.channel.setInstanceMap(self.instanceIdMapping)


    def runSimulate(self, policy):
        # start simulate!
        for time in range(self.totalSimulateTime):
            # random.shuffle(self.cars)
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

    def collectPenalty(self):
        res = []
        for i in range(len(self.cars)):
            # res.append(self.cars[i].ageList)
            res.append(self.cars[i].getPenaltyList())
        return res


def find_avg_aoi(path, isSingle = 0):

    policyList = ['maxCarAgeDrop', 'FIFO', 'LCFS', 'maxAge', 'randomPick']
    results = {}
    for file in glob.glob(path + '_*'):
        with open(file) as f:
            aoi_policy_dic = json.load(f)

        policy_aoi = {}
        if not isSingle:
            for policy in aoi_policy_dic:
                res = []
                for car in aoi_policy_dic[policy]:
                    res += car
                policy_aoi[policy] = sum(res) / len(res)
                # policy_aoi[policy] = res
                #print('file {}, age list {}'.format(file, res))
            results[file] = policy_aoi
        else:
            res = []
            for i, car in  enumerate(aoi_policy_dic['maxCarAgeDrop']):
                res.append(sum(car) / len(car))
            results[file.split('_')[1]] = res
            # policy_aoi[policy] = res
            # print('file {}, age list {}'.format(file, res))
    with open(path + '.log', 'w') as file:
        file.write(json.dumps(results))


def find_avg_penalty(path):

    policyList = ['maxPenalty', 'FIFO', 'LCFS', 'maxAge', 'randomPick']
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

    with open(path + '.log', 'w') as file:
        file.write(json.dumps(results))

def testServerProcessRate(testServerProcessRateRange, isPenalty = 0):

    for i in testServerProcessRateRange:
        print("Processing Rate: ", i)
        res = {}
        for policy in policyList:
            # print(policy)
            simulation = Simulation(carNum=5, serverProcessRate=i)
            simulation.runSimulate(policy)
            if not isPenalty:
                res[policy] = simulation.collectAOI()
            else:
                res[policy] = simulation.collectPenalty()
        if not isPenalty:
            with open('processRate_' + str(i) + '_ms.log', 'w') as file:
                file.write(json.dumps(res))
        else:
            with open('penaltyProcessRate_' + str(i) + '_ms.log', 'w') as file:
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
        with open('trafficRate_' + str(i) + '_ms.log', 'w') as file:
            file.write(json.dumps(res))

def testFairness(testFairnessRange):

    serviceCount = []
    for i in testFairnessRange:
        print("Processing Rate: ", i)
        res = {}
        policy = "maxCarAgeDrop"
        simulation = Simulation(carNum=5, serverProcessRate=i, trafficRate=10)
        simulation.runSimulate(policy)
        res[policy] = simulation.collectAOI()
        cnts = simulation.collectServiceCount()
        total = sum(cnts)
        for j, cnt in enumerate(cnts):
            cnts[j] = cnts[j] / total
        serviceCount.append(cnts)
        with open('fairnessAge_' + str(i) + '_ms.log', 'w') as file:
            file.write(json.dumps(res))
    with open('fairnessCnt.log', 'w') as file:
        file.write(json.dumps(serviceCount))

def testUserNum():
    for i in [2, 4, 6, 8, 10, 12, 14, 16]:
        print("User Cnt: ", i)
        res = {}
        for policy in policyList:
            simulation = Simulation(carNum=i, serverProcessRate=10, trafficRate=20)
            simulation.runSimulate(policy)
            res[policy] = simulation.collectAOI()

        with open('userCnt_' + str(i) + '_ms.log', 'w') as file:
            file.write(json.dumps(res))


def printSampleAge(carNum=2):

    policy = 'maxCarAgeDrop'
    simulation = Simulation(carNum=carNum, serverProcessRate=5)
    simulation.runSimulate(policy)
    res = simulation.collectAOI()

    with open('sampleAge.log', 'w') as file:
        file.write(json.dumps(res))


"""
Main Simulation
"""

startTime = time.time()

"""Varying server processing rate"""
testServerProcessRateRange = [2 * (i + 1) for i in range(10)]
# testServerProcessRate(testServerProcessRateRange)
# find_avg_aoi('processRate')
# plotAvgAOI('processRate.log', testServerProcessRateRange, 'Average Server Processing Time (ms)', 'Average Age (ms)')

"""Varying traffic rate from each user"""
testTrafficRateRange = [10 * (i + 1) for i in range(6)]
# testTrafficRate(testTrafficRateRange)
# find_avg_aoi('trafficRate')
plotAvgAOI('trafficRate.log',testTrafficRateRange, "$1/{\lambda}$", 'Average Age')

"""Varying the user count"""
# testUserNum()
# find_avg_aoi('userCnt')
# plotAvgAOI('userCnt.log', [2, 4, 6, 8, 10, 12, 14, 16] , 'Total User Count', 'Average Age')


"""Fairness between two users by different processing rate"""
testFairnessRange = [5 * (i + 1) for i in range(10)]
# testFairness(testFairnessRange)
# find_avg_aoi('fairnessAge', isSingle = 1)
# plotFairness('fairnessAge.log', testFairnessRange, '$1/{\mu}$', 'Individual Average Age')
# plotFairnessCnt('fairnessCnt.log', testFairnessRange, '$1/{\mu}$', 'User Service Fraction')


"""Evaluate penalty"""
testServerProcessRateRange = [2 * (i + 1) for i in range(7)]
# testServerProcessRate(testServerProcessRateRange, isPenalty=1)
# find_avg_penalty('penaltyProcessRate')
# plotAvgPenalty('penaltyProcessRate.log', testServerProcessRateRange, 'Average Server Processing Time (ms)', 'Penalty')

"""Backup Below"""

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