from math import exp
import subprocess


def sigmoid(x):
    return 1 / (1 + exp(-x))


def get_probs(x):
    """
    Gets the confidence array of a given file without obfsucation. Baseline fitness

    Parameters
    ----------
    A filename to pass in - our.apk

    Returns
    -------
    An array in the form [prediction, confidnece]

    """
    # Terminating condition for a successful attack, prediction = 1
    # As the attack progresses, focus on label 2
    # print("Single_dan_test with "+str(x)+"::")
    cmd = "sudo bash /root/Automation/single_dan_test.sh " + str(x) + " /root/Automation/init_test/ 0"
    # print("\t\'"+str(cmd)+"\'")
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, err = proc.communicate()
    conf = out.split()[-1]  # Make sure this works
    label = out.split()[-2]

    # print("\t\tDEBUG:: get_probs - out = '"+str(out)+"'")
    return [int(label), float(conf)]


def fitnessScore(x, baselineConfidence):
    label, conf = get_probs(x)
    fitness = baselineConfidence - conf
    return fitness, conf, label
