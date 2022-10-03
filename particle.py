import numpy as np
from Utilities import sigmoid
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
        self.pastPositions = []         # Logging!
        self.currentPosition = None
        self.particleDistanceArr = []
        self.nextPosition = None
        self.bestPosition = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.currentVelocity = None
        self.pathToAPK = None           # One that its testing 0001110001_......apk
        self.currentFitness = 0
        self.useOfAdvRef = False        # flags for use of dangerous obfuscators (they break things)
        self.useOfRef = False

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

    def setW(self):
        self.wEND = 0.2
        self.wSTART = 0.8

    def printParticleInformation(self):
        print('Particle %s -- Best Fitness %s \n' % (str(self.particleID), str(self.bestFitness)))

    def standardVelocity(self, swarmBestPosition, T, C1, C2, maxIterations):
        # Establish unique baselines for math
        particleBestPosition = deepcopy(self.bestPosition)
        particleCurrentPosition = deepcopy(self.particleDistanceArr)
        swarmBestPosition = deepcopy(swarmBestPosition)
        self.calculateW(T, swarmBestPosition, maxIterations)

        v = deepcopy(self.currentVelocity)

        for i, x in enumerate(particleCurrentPosition):  # 16 long char array of 0s and 1s
            # i = index, x = value
            # If either of these aren't the same, move in that direction. If they are the best, stay.
            # maintain 2 lists, currentPosition, and the second one which will have distances
            exploration = C1*np.random.uniform(0.0, 1.0) * (swarmBestPosition[i] - particleCurrentPosition[i])

            exploitation = C2*np.random.uniform(0.0, 1.0) * (particleBestPosition[i] - particleCurrentPosition[i])

            inertia = self.currentVelocity[i] * self.W

            v[i] = sigmoid(exploration + exploitation + inertia)

        self.currentVelocity = deepcopy(v)

    def calculateNextPosition(self, swarmBestPosition, T, C1, C2, maxIterations):
        """
        Leverages current velocity along with change constants to determine whether any given obfuscator is turned
        on or off, then returns a representative string value.

        """
        nextPosition = deepcopy(self.currentPosition)
        self.standardVelocity(swarmBestPosition, T, C1, C2, maxIterations)

        for i, x in enumerate(nextPosition):
            if self.currentVelocity[i] > np.random.uniform(0.0, 1.0):
                nextPosition[i] = 1
            else:
                # If the velocity is high in that direction, make 1, else make it a zero. It can flip!!
                nextPosition[i] = 0
        self.setCurrentPosition(nextPosition)
        self.particleDistanceArr = deepcopy(self.currentVelocity)
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
        
    def logOutput(self,iteration,sampleNumber):
        with open("results/" + str(sampleNumber) + "/" + str(self.particleID)+ ".csv","a") as f:
            f.write("%s,%s,%s,%s,%s,%s\n" %(iteration, self.currentPosition, self.bestPosition, self.currentFitness, self.bestFitness, self.currentVelocity()))
