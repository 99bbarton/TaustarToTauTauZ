#A script to combine the outputs of crab jobs


import os
import argparse
import subprocess

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

def parseArgs():
    argparser = argparse.ArgumentParser(description="hadd together output root files from crab jobs")
    argparser.add_argument("-d", "--dir", required = True, action = "store", help="CRAB submission directory relative to current directory")
    argparser.add_argument("-o", "--out", required = False, action = "store", help="Output directory relative to /store/user/bbarton/TaustarToTauTauZ/")
    argparser.add_argument("-t", "--typ", required = True, choices = ["SIG", "MC", "DATA"], help="What type of files to process")
    argparser.add_argument("-n", "--noHadd", action = "store_true", help="If specified, will not try to hadd files and will only produce dir list")
    argparser.add_argument("-f", "--force", required = False, action="store_true", help="If specified, will add the -f flags to hadd and xrdcp commands")
    args = argparser.parse_args()

    return args

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

#Gets all of the necessary information from the crab submission logs and status to construct the EOS directory names containing the output root files
def buildDirList(args):
    print("\nBuilding directory list..." )
    
    eosDirList = []
    if args.typ == "SIG":
        dirBase = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/"
    elif args.typ == "MC":
        dirBase = "/store/user/bbarton/TaustarToTauTauZ/BackgroundMC/"
    dirBase += args.dir

    if args.typ == "MC":
        dirBase = dirBase.replace("MCPFNano/", "PFNano")

    dirPath = args.dir + "/"
    for subDir in os.listdir(dirPath):
        if os.path.isfile(args.dir+"/"+subDir) or not subDir.startswith("crab_"):
            continue
        print("\tgetting status of " + subDir)
        command = 'crab status -d ' + dirPath + subDir + ' | grep "Task name:" ' 
        stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        #print(stdout)
        
        splitOut = stdout.split(":")
        subTime = splitOut[1].strip()
        jobName = splitOut[2][8:].strip()
        print(jobName)
        jobName = jobName[jobName.find("Run"):jobName.find("rea")] + "realistic_"
        #print("subTime=" + subTime)
        print("sliced jobName=" + jobName)

        command = 'less ' + dirPath + subDir + '/crab.log | grep "config.Data.inputDataset ="'
        stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if len(stdout) == 0:
            print("ERROR: No dataset found")
            exit(2)
        #print(stdout)
        #exit(0)

        if args.typ == "SIG":
            dataset = stdout.split("'")[-2].split("/")[1]
            massStr = dataset[dataset.find("Z_m")+2:dataset.find("_TuneCP5")]
            versStr = stdout.split("'")[-2].split("/")[2]
            versStr = versStr[versStr.find("realistic_")+10:]
            #print("massStr", massStr)
            #print("versStr", versStr)
            #print("dataset",dataset)
            
            eosDirPath = dirBase + "/" + dataset + "/" + jobName + versStr + "__" + massStr + "/" + subTime + "/0000/"
            #print(eosDirPath)
            eosDirList.append(eosDirPath)
        elif args.typ == "MC":
            if jobName.find("22EE") >= 0:
                yrStr = "2022post"
            elif jobName.find("2022") >= 0:
                yrStr = "2022"
            elif jobName.find("23BPix") >= 0:
                yrStr = "2023post"
            elif jobName.find("2023") >= 0:
                yrStr = "2023"

            dataset = stdout.split("'")[-2].split("/")[1]
            dsStart = dataset[:2].upper()
            if dsStart == "TW" or dsStart == "TB":
                dsStart = "ST"
            elif dsStart == "QC":
                dsStart = "QCD"
            elif dsStart == "WT":
                dsStart = "WJets"

            dataset = stdout.split("'")[-2].split("/")[1]

            versStr = stdout.split("'")[-2].split("/")[2]
            versStr = versStr[versStr.find("realistic_")+10:]
            
            eosDirPath = dirBase + "/" + yrStr + "/" + dsStart + "/" + dataset + "/" + jobName + versStr + "_" + dataset[:dataset.find("_")] + "/" + subTime + "/0000/"
            print(eosDirPath)
            

    print("... done building directory list\n")
    return eosDirList

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

def haddFiles(dirList, args):
    print("\nhadd'ing files together...")

    if args.force:
        force = "-f "
    else:
        force = ""
    
    fileList = []
    for dirPath in dirList:
        targetName = dirPath.split("/")[-4][5:] + ".root"
        #print(targetName)
        fileList.append(targetName)
        
        os.system("hadd " + force + targetName + " `xrdfsls -u " + dirPath + " | grep .root `")

    print("...done hadd'ing files together")
    return fileList


#-------------------------------------------------------------------------------------------------------------------------------------------------------#

def copyFiles(fileList, args):
    print("\nCopying files...")

    outdir = os.environ["XRDURL"] + "/store/user/bbarton/TaustarToTauTauZ/" + args.out
    if outdir[-1] != "/":
        outdir += "/"

    if args.force:
        force = "-f "
    else:
        force = ""
    
    for fil in fileList:
        os.system("xrdcp " + force + fil + " " + outdir)
        
    print("...done copying files")

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    args = parseArgs()
    dirList = buildDirList(args)
    if not args.noHadd:
        fileList = haddFiles(dirList, args)
        if args.out:
            copyFiles(fileList, args)
    else:
        print("dirList = " + str(dirList))

        
    
