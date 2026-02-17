
#Script to run Combine on the datacards in ./Datacards/



import os
import sys


def parseArgs():
    args = {}
    return args

def runCombine(args):
    for dc in os.listdir("./Datacards"):
        os.system("combine -M AsymptoticLimits Datacards/" + dc + " -t 10")

if __name__ == "__main__":
    args = parseArgs()
    runCombine(args)
