
#Script to run Combine on the datacards in ./Datacards/



import os
import sys
import argparse


def parseArgs():
    argparser = argparse.ArgumentParser(description="Utility to script to run Combine")
    argparser.add_argument("-i", "--inDir", default="./Datacards/", help="A path to the directory containing datacards")
    argparser.add_argument("-f", "--files", nargs="+", help="A specific datacard file to run over. It should be in the path specified by --inDir")
    argparser.add_argument("-l", "--limit", action="store_true", help="If specified, runs AsymptoticLimits method")
    argparser.add_argument("-t", "--toys", type=int, default=100, help="The number of toys to use")
    argparser.add_argument("-n", "--nameTag", type=str, default="", help="A specific naming tag (will be present in output .root file)")
    args = argparser.parse_args()
    
    if len(args.files) == 0:
        args.files = os.listdir(args.inDir)

    return args

def runCombine(args):
    for dc in args.files:
        mass = dc.split("_")[-1][:-4]
        print("\n\n =================================== Running M" + mass + "  ===================================== \n\n")
        if args.limit:
            command = f"combine -M AsymptoticLimits {args.inDir}{dc} -t {args.toys} -m {mass}"
            if len(args.nameTag) > 0:
                command += " -n " + args.nameTag
            os.system(command)

if __name__ == "__main__":
    args = parseArgs()
    runCombine(args)
