import os.path

from particle import particle

import numpy as np
from copy import deepcopy
import random
import subprocess
from common import Defender

random.seed(0)
np.random.seed(0)


class Swarm:

    def __init__(self, numOfParticles, randomMutation, maxQueries, x, C1, C2, e, defenseModel):
        """

        Parameters
        ----------
        numOfParticles = num particles in PSO
        randomMutation = random mutation chance for each particle
        maxQueries = number of stages of PSO we want to accomplish
        x = FilePath
        C1 = constant that controls exploration
        C2 = constant that controls exploitation
        e = terminating condition (in our case, it will be the num of iterations w/o improvement)
        """
        # The fields the python linting gods demand we have
        self.changeRate = None
        self.flag = None
        self.bestProba = None
        self.baselineConfidence = None
        # The actual fields we need RIGHT NOW
        self.particles = []
        self.baseLabel = None
        self.label = 1
        self.numberOfParticles = numOfParticles
        self.bestFitness = 0
        self.dLength = 2 ** 16  # 2 choices, 16 dimensions
        self.numberOfQueries = 0
        self.bestPosition = [0] * self.dLength  # Everything starts as on in 17 dimensions
        self.randomMutation = randomMutation
        self.maxQueries = maxQueries
        self.pastFitness = []
        self.apkFile = x                # Original APK file PATH that is being modified xyz.apk
        self.earlyTermination = e
        self.C1 = C1
        self.C2 = C2
        self.targetModel = defenseModel


    def setBestPosition(self, newPosition):
        self.bestPosition = deepcopy(newPosition)

    def setBestFitnessScore(self, newScore):
        self.bestFitness = newScore

    def getProbs(self,apk):
        """
        Gets the confidence array of a given file without obfuscation. Baseline fitness

        Parameters
        ----------
        A filename to pass in - our.apk

        Returns
        -------
        An array in the form [prediction, confidence]

        """

        # Propagates the defender object with the assumption that the model passed in, is malicious.
        # Dumps out 'y_pred' which should be the models confidence that it is malicious.
        mal_conf = self.targetModel.predict([apk], [1])  #TODO: Double check that 1 is malicious.

        # # Terminating condition for a successful attack, prediction = 1
        # # As the attack progresses, focus on label 2
        # # print("Single_dan_test with "+str(x)+"::")
        # cmd = "sudo bash /root/Automation/single_dan_test.sh " + str(x) + " /root/Automation/init_test/ 0"
        # # print("\t\'"+str(cmd)+"\'")
        # proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        # out, err = proc.communicate()
        # conf = out.split()[-1]  # Make sure this works
        # label = out.split()[-2]

        # print("\t\tDEBUG:: get_probs - out = '"+str(out)+"'")

        return [int(1 if mal_conf[0][1] > .5 else 0), float(mal_conf[0][1])]
        # return [int(label), float(conf)]


    def fitnessScore(self,apk):
        # Takes in APK and baseline confidence.
        label, conf = self.getProbs(apk)
        fitness = self.baselineConfidence - conf
        return fitness, conf, label


    def calculateBaselineConfidence(self):
        """
        Establishes baseline confidence and best probability based on assessment of the input file through a dry run
        of the ML model.
        """
        pred, conf = self.getProbs(self.apkFile)        # Get the confidence f

        self.baseLabel = pred                       # This is base
        self.label = pred                           # This changes

        self.baselineConfidence = conf              # This is base
        self.bestProba = conf                       # This changes
        return conf, pred

    def initializeSwarmAndParticles(self, inputDir):
        """
        Does what it says on the box.
        """
        print('Initializing Swarm and Particles...\n')
        self.initializeSwarm()
        self.initializeParticles(inputDir)

    def initializeSwarm(self):
        """
        Sets up the swarm with our most basic assumptions. Establish how much the particles change, set the initial
        flag that would stop the process to off (flicks to on if enough iterations go by with no change), establishes
        a baseline best position of [no change] and similarly for the fitness score.
        """
        self.changeRate = 3.0/16.0  # Chances, each iter, 3 obfuscators out of the 16 present
        self.flag = False           # Tells us if there is no change after n number of iterations
        self.bestPosition = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.setBestFitnessScore(0)

    def initializeParticles(self, inputDir):
        particleList = []
        for x in range(self.numberOfParticles):
            # Set up the initial particle
            p = particle(x)
            p.setW()
            p.currentVelocity = {}
            p.pathToAPK = deepcopy(self.apkFile)
            self.randomizeParticle(p, p.currentPosition, inputDir)

            p.particleDistanceArr.extend(p.currentVelocity)
            particleList.append(deepcopy(p))
        self.particles = deepcopy(particleList)

    def randomizeParticle(self, p, basePosition, inputDir):
        """
        Randomly selects obfuscators based on the velocity, applies them to a file, and returns the modified filename
        of the apk after it was modified.
        """
        p.currentVelocity = [np.random.uniform(0.0, 1.0) for i in range(16)]  # Randomize init particle
        p.currentPosition = [1 if p.currentVelocity[i] <= self.changeRate else 0 for i in range(16)]
        self.check(p, inputDir)

        p.pastPositions.append(p.currentPosition)
        return True

    def searchOptimum(self, inputDir):

        # If its not malicious then exit
        if self.label != 1:
            return self.bestPosition, self.bestFitness, 0, self.numberOfQueries
        iteration = 1

        # While we have queries left and are still malicious
        while self.numberOfQueries < self.maxQueries:
            if self.label != 1:
                return self.bestPosition, self.bestFitness, 0, self.numberOfQueries

            # Get the next position, and check / update those positions while adding them to the historical record
            for p in self.particles:
                p.calculateNextPosition(self.bestPosition, self.numberOfQueries, self.C1, self.C2, self.maxQueries)
                self.check(p, inputDir)
            self.pastFitness.append(self.bestFitness)
            posString = ""

            # Utility method don't think too much about it
            for e in self.bestPosition:
                posString += str(e)

            print('++ Iteration %s - Best Fitness %s - Best Position %s - Confidence %s - Number of Queries %s' % (
                str(iteration), str(self.bestFitness), posString, self.bestProba, self.numberOfQueries))

            if self.earlyTermination > 0 and len(self.pastFitness[(-1*self.earlyTermination):]) >= \
                    self.earlyTermination and len(set(self.pastFitness[(-1*self.earlyTermination):])) == 1:
                return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries

            if self.label != 1:
                return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries
            iteration = iteration + 1

        print("== Number of Queries: %s" % self.numberOfQueries)
        return deepcopy(self.bestPosition), self.bestFitness, iteration, self.numberOfQueries

    def check(self, p, inputDir):
        """
        p is our particle
        new position is current position
        """
        apkFile = self.apkFile
        apkBasename = os.path.basename(apkFile)  # Could error out if the pathToApK is not actually a parsable path
        obf_string = ""
        for e in p.currentPosition:
            obf_string += str(e)
        # print("Gen sample script...")
        # To compound the files, switch out str(self.apkFile) in first arg, to p.pathToAPK.

        cmd = "bash gen_sample.sh " + str(self.apkFile) + " " + obf_string + \
              " "+inputDir+" " + str(p.particleID) + " " + str(self.apkFile)
        # print("\t\'" + str(cmd) + "\'")
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

        # Communicate so the output goes to python, and is auto setting the return code
        out, err = proc.communicate()
        ret_code = proc.returncode

        if ret_code == 0:
            # Generate the output name of the new APK
            APKDir = str(os.path.dirname(self.apkFile))
            newAPKPath = APKDir + "/" + obf_string+"_Particle_"+str(p.particleID)+"_"+str(apkBasename)
            # print("New APK Path for particle is: \'"+str(newAPKPath)+"\'")
            p.pathToAPK = newAPKPath

            # Run the assessment script on this path - get the confidence / label
            newFitness, newProba, newLabel = self.fitnessScore(p.pathToAPK)
            os.remove(newAPKPath)

            # Increment metrics
            self.numberOfQueries = self.numberOfQueries + 1
            p.setCurrentFitnessScore(newFitness)

            posString = ""
            for e in p.currentPosition:
                posString += str(e)

            velocityString = ""
            for e in p.currentVelocity:
                velocityString += '%.5f, ' % e
            velocityString = "["+velocityString[:-2]+"]"

            print("-- ParticleID: " + str(p.particleID)+" | Current Fitness: "+str(p.currentFitness) +
                  "\t| Position: "+posString+" | Label / Confidence: " + str(self.label) + " / " + str(newProba) +
                  "\n\t| Velocity: "+velocityString)

            # Modify awareness of the best fitness of particle / swarm accordingly
            if newFitness > p.bestFitness:
                p.setBestFitnessScore(newFitness)
                p.setBestPosition(p.currentPosition)
            if p.bestFitness > self.bestFitness:
                self.bestProba = newProba
                self.setBestFitnessScore(p.bestFitness)
                self.label = newLabel
                self.setBestPosition(p.bestPosition)

            
            
        else:
            # This means that the obfuscation process made things bad
            # Randomize the particle, try it again.
            self.randomizeParticle(p, p.currentPosition, inputDir)
