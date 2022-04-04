import os.path

from particle import particle
from Utilities import fitnessScore, get_probs
import numpy as np
from copy import deepcopy
import random
import subprocess

from IPython import embed

random.seed(0)
np.random.seed(0)


class Swarm:

    def __init__(self, numOfParticles, randomMutation, maxQueries, x, C1, C2, e):
        """

        Parameters
        ----------
        numOfParticles = num particles in PSO
        randomMutation = random mutation chance for each particle
        maxQueries = number of stages of PSO we want to accomplish
        x = FilePath
        C1 = constant that controls exploration
        C2 = constant that controls explotiation
        e = terminating condition (in our case, it will be the num of iterations w/o improvement)
        """
        self.particles = []
        self.label = 2
        self.numberOfParticles = numOfParticles
        self.bestFitness = 0
        self.dLength = 2 ** 16  # 2 choices, 17 dimensions
        self.numberOfQueries = 0
        self.bestPosition = [0] * self.dLength  # Everything starts as on in 17 dimensions
        self.randomMutation = randomMutation
        self.maxQueries = maxQueries
        self.pastFitness = []
        self.apkFile = x                # Original APK file PATH that is being modified xyz.apk
        self.earlyTermination = e
        self.C1 = C1
        self.C2 = C2

    def setBestPosition(self, newPosition):
        self.bestPosition = deepcopy(newPosition)


    def setBestFitnessScore(self, newScore):
        self.bestFitness = newScore


    def calculateBaselineConfidence(self):
        """
        Establishes baseline confidence and best probability based on assessment of the input file through a dry run
        of the ML model.
        """
        pred, conf = get_probs(self.apkFile)        # Get the confidence f
        self.baselineConfidence = conf              # This is base
        self.bestProba = conf                       # This changes
        return conf

    def initializeSwarmAndParticles(self):
        """
        Does what it says on the box.
        """
        print('Initializing Swarm and Particles...\n')
        self.initializeSwarm()
        self.initializeParticles()

    def initializeSwarm(self):
        """
        Sets up the swarm with our most basic assumptions. Establish how much the particles change, set the intiial
        flag that would stop the process to off (flicks to on if enough iterations go by with no change), establishes
        a baseline best position of [no change] and similarly for the fitness score.
        """
        self.changeRate = 3.0/16.0  # Chances, each iter, 3 obfuscators out of the 17 present
        self.flag = False           # Tells us if there is no change after n number of iterations
        self.bestPosition = [0000000000000000]
        self.setBestFitnessScore(0)

    def initializeParticles(self):
        particleList = []
        for x in range(self.numberOfParticles):
            # Set up the initial particle
            p = particle(x)
            p.setW(self.C1, self.C2)
            p.currentVelocity = {}
            p.pathToAPK = deepcopy(self.apkFile)
            self.randomizeParticle(p, p.currentPosition)
            particleList.append(deepcopy(p))
        self.particles = deepcopy(particleList)

    def randomizeParticle(self, p, basePosition):
        """
        Randomly selects obfuscators based on the velocity, applies them to a file, and returns the modified filename
        of the apk after it was modified.
        """
        p.currentVelocity = [np.random.uniform(0.0, 1.0) for i in range(16)]  # Randomize init particle
        p.currentPosition = [1 if p.currentVelocity[i] <= self.changeRate else 0 for i in range(16)]
        #embed()
        self.check(p)

        p.pastPositions.append(p.currentPosition)
        return True

    def searchOptimum(self, sampleNumber=None):
        if self.label != 2:
            return self.bestPosition, self.bestFitness, 0, self.numberOfQueries
        iteration = 1

        while self.numberOfQueries < self.maxQueries:
            if self.label != 2:
                return self.bestPosition, self.bestFitness, 0, self.numberOfQueries

            for p in self.particles:
                # self.randomizeParticle(p, p.currentPosition)
                p.calculateNextPosition(self.bestPosition, self.numberOfQueries, self.C1, self.C2, self.maxQueries)
                self.check(p)
            self.pastFitness.append(self.bestFitness)
            print('Iteration %s - Best Fitness %s - Number of Queries %s' % (
            str(iteration), str(self.bestFitness), str(self.numberOfQueries)))

            if self.earlyTermination > 0 and len(self.pastFitness) >= self.earlyTermination and len(
                    set(self.pastFitness)) == 1:
                return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries
            if self.label != 2:
                return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries
            iteration = iteration + 1
        print("Number of Queries: %s" % (self.numberOfQueries))
        return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries

    def check(self, p):
        """
        p is our particle
        new position is current position
        """
        apkFile = self.apkFile
        apkBasename = os.path.basename(apkFile)  # Could error out if the pathToApK is not actually a parsable path

        #from IPython import embed
        #embed()
        obf_string = ""
        for e in p.currentPosition:
            obf_string += str(e)
        print("Gen sample script...")
        cmd = "sudo bash /root/Automation/gen_sample.sh " + str(p.pathToAPK) + " " + obf_string + " /root/Automation/ " + str(p.particleID)
        print("\t\'" + str(cmd) + "\'")
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

        # Communicate so the output goes to python, and is auto setting the return code
        out, err = proc.communicate()
        ret_code = proc.returncode

        if ret_code == 0:
            # Generate the output name of the new APK
            APKDir = str(os.path.dirname(self.apkFile))
            newAPKPath = APKDir + "/" + obf_string+"_Particle_"+str(p.particleID)+"_"+str(apkBasename) # Add an output dir


            # Assign new path to the particle
            p.pathToAPK = newAPKPath

            # Run the assessment script on this path - get the confidence / label
            newFitness, newProba, self.label = fitnessScore(p.pathToAPK, self.baselineConfidence)

            # Increment metrics
            self.numberOfQueries = self.numberOfQueries + 1
            p.setCurrentFitnessScore(newFitness)

            # Modify awareness of the best fitness of particle / swarm accordingly
            if newFitness > p.bestFitness:
                p.setBestFitnessScore(newFitness)
                p.setBestPosition(p.currentPosition)
            if p.bestFitness > self.bestFitness:
                self.setBestFitnessScore(p.bestFitness)
                self.setBestPosition(p.bestPosition)

        else:
            # This means that the obfuscation process made things bad
            # Randomize the particle, try it again.
            self.randomizeParticle(p, p.currentPosition)

