# A script to split a specific ROOT file or all of the ROOT files in a directory into smaller files
# Build around the command-line utility rooteventselector which ships with root

import os
import argparse
from ROOT import TFile, TTree

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Extract command line arguments and check inputs for validity
def parseArgs():
    argparser = argparse.ArgumentParser(description="Tool to split ROOT file(s) into smaller files. The -f xor -d must be provide + the -e xor -n must be provided. Additionally at least one tree name must be specified via -t")
    argparser.add_argument("-f", "--file", type=str, help="A path/filename of a root file to split. Must be in NFS (not EOS)")
    argparser.add_argument("-d", "--directory", type=str, help="A directory path where every ROOT file will be split. Must be in NFS (not EOS)")
    argparser.add_argument("-e", "--nEvents", type=int, help="The number of events to move to each output file")
    argparser.add_argument("-n", "--nFiles", type=int, help="The number of output files to split each input file into")
    argparser.add_argument("-t", "--trees", type=str, action="append", help="The name of the TTree(s) to copy between input and output files")
    argparser.add_argument("-o", "--outpath", type=str, default="./", help="A directory path to write output files to (NFS not EOS)")
    argparser.add_argument("--test", action="store_true", help="If provided, will print copy commands but not execute them")
    #argparser.add_argument("-c", "--cuts", type=str, "A set of cuts to use to select which events are copied to output files") #Need compatibility checks with -e/-n args if implemented

    args = argparser.parse_args()

    #Check that a valid combination of arguments have been provided
    if (args.file and args.directory) or not (args.file or args.directory):
        print("Please provide either the -f xor -d arguments")
        exit(1)
    if (args.nEvents and args.nFiles) or not (args.nEvents or args.nFiles):
        print("Please provide either the -e xor -n arguments")
        exit(1)
    if not args.trees:
        print("At least on TTree name must be provided via the -t argument")
        exit(1)

    #Check that at least one ROOT file can be found
    if args.file and not os.path.isfile(args.file):
        print("ERROR: File " + args.file + " could not be found")
        exit(2)
    if args.directory and os.path.exists():
        fileList = os.listdir(args.directory)
        validFiles = False
        if len(fileList) > 0:
            for filename in fileList:
                if filename.endswith(".root"):
                    validFiles = True
                    break
        if not validFiles:
            print("No valid ROOT files (files ending with .root) could be found in the provided directory: " + args.directory)
            exit(2)
    else:
        print("Directory " + args.directory + " could not be found")
        exit(2)

    #Check the outpath exists
    if not os.path.isdir(args.outpath):
        print("Outpath " + args.outpath + " is not a vaild directory")
        exit(2)
    if not args.outpath.endswith("/"):
        args.outpath += "/"


    return args

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Split each input file into smaller output files according to the extracted command line arguments in args
#Builds and executes commands using rooteventselector
#Run "rooteventselector -h" in the terminal to see its argument details
def splitFiles(args):

    if args.test:
        print("Running in test mode... The commands that would have been executed are:")
    else:
        print("Splitting files with the following commands: ")

    #Build the list of files to split
    inFileList = []
    if args.directory:
        for filename in os.listdir(args.directory):
            if filename.endswith(".root"):
                inFileList.append(filename)
    else:
        inFileList.append(args.file)

    for inFilename in inFileList:
        fileBase = inFilename[:inFilename.rfind("_")] + "_"

        inFile = TFile.Open(inFilename, "READ")

        aTree = inFile.Get(args.trees[0])
        nEntries = aTree.GetEntries()

        nFiles = 0
        if args.nFiles: #If we have a target number of output files, calculate number of events per file that works out
            nFiles = args.nFiles
            nEvents = nEntries / nFiles
            if nEvents < 10:
                print("ERROR: Requested number of output files per input file: " + str(nFiles) + " would put fewer than 10 events in each output file...")
                exit(3)
        elif args.nEvents: #Calulate number of output files to make from this input file if not fixed by args.nFiles
            nFiles = nEntries / args.nEvents
            nEvents = args.nEvents
            if nFiles < 1:
                print("ERROR: TTree " + args.trees[0] + " in file " + filename + " has fewer entries than are requested in the output files! Given nEvents/output file was " + str(args.nEvents))
                exit(3)
        
        #Now build and execute each copy command
        startIdx = 1
        endIdx = nEvents
        permitAll = False
        for outFileN in range(1, nFiles + 1):
            outFileName = args.outpath + fileBase + str(outFileN) + ".root"

            #If action will overwrite existing file get permission from the user for this file/all files
            if os.path.isfile(outFileName) and not permitAll and not args.test: 
                print("WARNING: " + outFileName + "will be overwritten. Do you wish to proceed?")
                print("Enter y to overwrite this file only and Y to overwrite this file and all other previously existing files encountered. Anything else will NOT overwrite this file.")
                response = input("Your reponse: " )
                if response != "y" or response != "Y":
                    continue
                if response == "Y":
                    permitAll = True

            for tree in args.trees:
                command = "rooteventselector -f " + str(startIdx) + " -l " + str(endIdx) + inFilename + ":" + tree + " " + outFileName          
                print(command)
                if not args.test:
                    os.system(command)

            startIdx += nEvents
            endIdx += nEvents

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    args = parseArgs()
    splitFiles(args)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#