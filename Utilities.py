from math import exp
import numpy as np
import subprocess


def nLargestValues(lst, stepSize):
    n = sorted(range(len(lst)), key=lambda i: lst[i])[-1 * stepSize:]
    return n


def all_pairs(lst):
    if len(lst) < 2:
        yield []
        return
    if len(lst) % 2 == 1:
        # Handle odd length list
        for i in range(len(lst)):
            for result in all_pairs(lst[:i] + lst[i + 1:]):
                yield result
    else:
        a = lst[0]
        for i in range(1, len(lst)):
            pair = (a, lst[i])
            for rest in all_pairs(lst[1:i] + lst[i + 1:]):
                yield [pair] + rest


def common_elements(list1, list2):
    return [element for element in list1 if element in list2]


def common_nonzero_elements(list1, list2):
    return [element for element in list1 if element in list2 and element == 0]


def list_rindex(li, x):
    for i in reversed(range(len(li))):
        if li[i] == x:
            return i
    raise ValueError("{} is not in list".format(x))


def chunks(l, n):
    for i in range(0, len(l), n):
        if len(l) - n < i + n:
            yield l[i:]
        else:
            yield l[i:i + n]


def sigmoid(x):
    return 1 / (1 + exp(-x))


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def toBin(ind, sequenceLength):
    lst = [0] * (sequenceLength - 1)
    lst[ind] = 1
    return lst


def fromBin(lst):
    encoding = lst.index(1)
    return encoding


def bytez_to_numpy(bytez, maxlen):
    padding_char = 256
    b = np.ones((maxlen,), dtype=np.uint16) * padding_char
    bytez = np.frombuffer(bytez[:maxlen], dtype=np.uint8)
    b[:len(bytez)] = bytez
    return b


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
    # print("Single_dan_test with "+str(x)+"::")  #TODO: It doesn't like it here for some reason and apparently the file doesnt exist
    #todo: MAYBE the file isnt being put where it should be??? Consult the texts.
    cmd = "sudo bash /root/Automation/single_dan_test.sh " + str(x) + " /root/Automation/init_test/ 0"
    # print("\t\'"+str(cmd)+"\'")
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, err = proc.communicate()
    conf = out.split()[-1]  # Make sure this works
    label = out.split()[-2]

    # from IPython import embed
    # embed()
    # print("\t\tDEBUG:: get_probs - out = '"+str(out)+"'")
    return [int(label), float(conf)]


def fitnessScore(x, baselineConfidence):
    label, conf = get_probs(x)
    fitness = baselineConfidence - conf
    return fitness, conf, label


def normalizeVector(X, lb, hb):
    minimum = np.min(X)
    maximum = np.max(X)
    normalized = [((hb - lb) * ((x - minimum) / (maximum - minimum))) + lb for x in X]
    return normalized
