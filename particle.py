import numpy as np
from copy import deepcopy
import random

random.seed(0)
np.random.seed(0)


class particle:
    W = None
    wEND = 0
    wSTART = 1.0

    def __init__(self, particleid=0):
        self.particleID = particleid
        self.bestFitness = 0
        self.pastPositions = []
        self.currentPosition = None
        self.nextPosition = None
        self.bestPosition = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.currentVelocity = None
        self.pathToAPK = None           # One that its testing 0001110001_......apk
        self.currentFitness = 0



    def setNextPosition(self, newPosition):
        self.nextPosition = deepcopy(newPosition)


    def setCurrentPosition(self, newPosition):
        self.currentPosition = deepcopy(newPosition)


    def setBestPosition(self, newPosition):
        self.bestPosition = deepcopy(newPosition)


    def setBestFitnessScore(self, newScore):
        self.bestFitness = newScore


    def setCurrentFitnessScore(self, newScore):
        self.currentFitness = newScore


    def setW(self, C1, C2):
        self.wEND = 0.2
        self.wSTART = 0.8


    def printParticleInformation(self):
        print('Particle %s -- Best Fitness %s \n' % (str(self.particleID), str(self.bestFitness)))


    def standardVelocity(self, swarmBestPosition, T, C1, C2, maxIterations):
        # Establish unique baselines for math
        particleBestPosition = deepcopy(self.bestPosition)
        particleCurrentPosition = deepcopy(self.currentPosition)
        swarmBestPosition = deepcopy(swarmBestPosition)
        self.calculateW(T, swarmBestPosition, maxIterations)

        v = deepcopy(self.currentVelocity)

        for i, x in enumerate(particleCurrentPosition):  # 16 long char array of 0s and 1s
            # i = index, x = value

            # from IPython import embed
            # embed()


            # If either of these arent the same, move in that direction. If they are the best, stay.
            if particleCurrentPosition[i] != swarmBestPosition[i]:                 # pCurrent vs sBest
                v[i] = C1*np.random.uniform(0.0, 1.0)
                continue # if current is the not the best, then move in direction

            # if (particleBestPosition[i] == swarmBestPosition[i]) and \
            #        not (swarmBestPosition[i] == particleCurrentPosition[i]):

            if particleBestPosition[i] != particleCurrentPosition[i]:
                v[i] = C2*np.random.uniform(0.0, 1.0)
                continue

        self.currentVelocity = np.add(deepcopy(v), np.multiply(self.currentVelocity, self.W))
        return self.currentVelocity


    def calculateNextPosition(self, swarmBestPosition, T, C1, C2, maxIterations):
        v = self.standardVelocity(swarmBestPosition, T, C1, C2, maxIterations)
        nextPosition = deepcopy(self.currentPosition)
        for i, x in enumerate(nextPosition):
            if v[i] > np.random.uniform(0.0, 1.0):
                nextPosition[i] = 1
        self.setCurrentPosition(nextPosition)
        return nextPosition


    def calculateW(self, T, swarmBestPosition, maxIterations):
        # dONT CHANGE THIS
        if np.all(np.equal(self.bestPosition, swarmBestPosition)):
            W = self.wEND
            self.W = W
            return self.W
        elif not np.all(np.equal(self.bestPosition, swarmBestPosition)):
            W = self.wEND + ((self.wSTART - self.wEND) * (1 - (T / maxIterations)))
            self.W = W
            return self.W
