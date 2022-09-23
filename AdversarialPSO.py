import argparse
import sys
import os

from Swarm import Swarm
from common import Defender

# Define arguments
parser = argparse.ArgumentParser(
    description="Metamorphic engine guided with PSO that modifies assembly code while keeping the same functionality")
parser.add_argument("-i", "--input", help="Input directory", default=None)
parser.add_argument("-s", "--sample", help="Single input file", default=None)
parser.add_argument("-o", "--output", help="Output directory", default=None)
parser.add_argument("-d", "--debug", action="store_true", help="print debug information", default=False)
parser.add_argument("-p", "--numOfParticles", help="Number of particles in the swarm", default=10, type=int)
parser.add_argument("-q", "--maxQueries", help="Maximum number of allowed queries", default=20000, type=int)
parser.add_argument("-r", "--randomMutation", help="Probability of random mutation", default=0.1, type=float)
parser.add_argument("-m", "--model", help="The type of model to use in the defense", default="basic_dnn",
                    type=str,
                    choices=['basic_dnn',
                             'atrfgsm',     # hardened DNN incorporating adversarial training with r-fgsm
                             'atadam',      # hardened DNN incorporating adversarial training with adam
                             'atma',        # hardened DNN incorporating adversarial training with a mixture of attacks
                             'adema'  # ,
                             # hardened ensemble-based DNN incorporating adversarial training with a mixture of attacks
                             # 'dadema'       # promoting the diversity of adversarial deep ensemble
                             ],
                    required=False)
parser.add_argument("-e", "--earlyTermination",
                    help="Number of iterations of unchanged fitness before terminating search process. Set to -1 to "
                         "disable",
                    default=60, type=int)
args = parser.parse_args()

# Panic if not defined
if (not args.input and not args.sample) or not args.output:
    parser.print_help()
    sys.exit(1)

# Import utils and important PSO bits


inputDir = args.input
outputDir = args.output
inputSample = args.sample
numOfParticles = args.numOfParticles
maxQueries = args.maxQueries
randomMutations = args.randomMutation
earlyTermination = args.earlyTermination
defModel = args.model
C1 = 1
C2 = 1


def logPSOOutput():
    model=Defender(defModel)
    if inputDir is not None:
        samples = []
        for dirPath, _, fileNames in os.walk(inputDir):
            for f in fileNames:
                samples.append(os.path.abspath(os.path.join(dirPath, f)))

    else:
        samples = [inputSample]
    with open('Malware_Samples_PSO_Results.csv', 'w') as f:
        f.write(
            'Sample,BaselineConfidence,BaselineFitness,Prediction_Before_PSO, Confidence_After_PSO,Fitness_After_PSO,'
            'Prediction_After_PSO,Iteration,Number_of_Required_Changes,Best_Position, Number_Of_Queries\n')
    if not os.path.exists("results"):
        os.mkdir("results")
    for i, samplePath in enumerate(samples):
        print("Handling... " + str(samplePath))
        if not os.path.exists("results/" + str(i)):
            os.mkdir("results/" + str(i))

        swarm = Swarm(numOfParticles, randomMutations, maxQueries, samplePath, C1, C2, earlyTermination, model)
        baselineConfidence, baselineLabel = swarm.calculateBaselineConfidence()
        print("Searching Optimum Adversarial Example... %s\n" % i)
        swarm.initializeSwarmAndParticles(inputDir)
        print('Model Prediction Before PSO= %s\n' % baselineLabel)
        print('Baseline Confidence= %s\n' % (str(baselineConfidence)))
        _, _, iterations, numberOfQueries = swarm.searchOptimum(inputDir)

        print('Model Prediction After PSO= %s' % swarm.label)  # later change 1= benign, 2 = mal
        print('Model Confidence After PSO= %s' % swarm.bestProba)
        print('Best Fitness Score= %s' % swarm.bestFitness)
        numberOfChanges = sum([int(pos) for pos in swarm.bestPosition[0:16]])

        posString = ""
        for e in swarm.bestPosition:
            posString += str(e)

        print('Required number of changes (L1)= %s' % numberOfChanges)
        with open('Malware_Samples_PSO_Results.csv', 'a') as f:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                samplePath, str(baselineConfidence),
                str(1 - baselineConfidence), str(swarm.baseLabel), str(swarm.bestProba),
                str(swarm.bestFitness), str(swarm.label), str(iterations), str(numberOfChanges), posString,
                str(numberOfQueries)))


if __name__ == "__main__":
    logPSOOutput()
