from math import exp
import subprocess


def sigmoid(x):
    return 1 / (1 + exp(-x))



def fitnessScore(x, baselineConfidence):
    # Takes in APK and baseline confidence.
    label, conf = get_probs(x)
    fitness = baselineConfidence - conf
    return fitness, conf, label
