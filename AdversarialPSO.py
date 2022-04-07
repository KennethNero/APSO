import argparse
import sys
import os

# Define arguments
parser = argparse.ArgumentParser(
    description="Metamorphic engine guided with PSO that modifies assembly code while keeping the same functionality")  # CHANGE
parser.add_argument("-i", "--input", help="Input directory", default=None)
parser.add_argument("-s", "--sample", help="Single input file", default=None)
parser.add_argument("-o", "--output", help="Output directory", default=None)
parser.add_argument("-d", "--debug", action="store_true", help="print debug information", default=False)
parser.add_argument("-p", "--numOfParticles", help="Number of particles in the swarm", default=10, type=int)
parser.add_argument("-q", "--maxQueries", help="Maximum number of allowed queries", default=20000, type=int)
parser.add_argument("-r", "--randomMutation", help="Probability of random mutation", default=0.1, type=float)
parser.add_argument("-e", "--earlyTermination",
                    help="Number of iterations of unchanged fitness before terminating search process. Set to -1 to disable",
                    default=60, type=int)
args = parser.parse_args()

# Panic if not defined
if (not args.input and not args.sample) or not args.output:
    parser.print_help()
    sys.exit(1)

# Import utils and important PSO bits
from Swarm import Swarm
from Utilities import get_probs

inputDir = args.input
outputDir = args.output
inputSample = args.sample
numOfParticles = args.numOfParticles
maxQueries = args.maxQueries
randomMutations = args.randomMutation
earlyTermination = args.earlyTermination
C1 = 1
C2 = 1


def logPSOOutput():
    if not inputDir == None:
        samples = os.listdir(inputDir)
    else:
        samples = [inputSample]
    with open('Malware_Samples_PSO_Results.csv', 'w') as f:
        f.write(
            'Sample,BaselineCofidence,BaselineFitness,Prediction_Before_PSO, Confidence_After_PSO,Fitness_After_PSO,Prediction_After_PSO,Iteration,Number_of_Required_Changes,Number_Of_Queries\n')
    i = 0
    for samplePath in samples:
        print(samplePath)
        # MAYBE do a try
        swarm = Swarm(numOfParticles, randomMutations, maxQueries, samplePath, C1, C2, earlyTermination)
        # MAYBE do an except if it fails a lot
        # try:
        baselineConfidence = swarm.calculateBaselineConfidence()
        baselineLabel = swarm.label
        if baselineLabel != 2:          # This means not benign
            continue
        print("Searching Optimum Adversarial Example... %s\n" % i)
        swarm.initializeSwarmAndParticles()
        print('Model Prediction Before PSO= %s\n' % baselineLabel)
        print('Baseline Confidence= %s\n' % (str(baselineConfidence)))
        _, _, iterations, numberOfQueries = swarm.searchOptimum()
        modelConfidence = baselineConfidence - swarm.bestFitness
        print('Model Confidence After PSO %s' % modelConfidence)
        print('Best Fitness Score= %s' % swarm.bestFitness)
        finalPosition = swarm.apkFile
        labelAfter, predAfter = get_probs(finalPosition)
        print(swarm.apkFile)
        numberOfChanges = sum([int(pos) for pos in swarm.bestPosition[0:16]])
        print('Model Prediction After PSO= %s' % (str(predAfter)))  # later change 1= benign, 2 = mal
        print('Required number of changes (L1)= %s' % (numberOfChanges))
        with open('Malware_Samples_PSO_Results.csv', 'a') as f:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            samplePath, str(baselineConfidence),
            str(1 - baselineConfidence), labelAfter, str(modelConfidence),
            str(swarm.bestFitness), str(predAfter), str(iterations), str(numberOfChanges), str(numberOfQueries)))
        i = i + 1
        #     os.system("mv " + str(samplePath) + " dataset/tested")
        # except:
        #     os.system("mv " + str(samplePath) + " dataset/failed")


if __name__ == "__main__":
    logPSOOutput()
