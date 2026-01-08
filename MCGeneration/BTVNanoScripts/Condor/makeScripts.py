import os
import sys
from datetime import date
import argparse
import subprocess
import copy

sys.path.append("../../../Framework/")
from datasets import bkgdDatasets_mini, sigDatasets_mini

#-------------------------------------------------------------------------------------------------------------------------------------------

def parseArgs():
    argparser = argparse.ArgumentParser(description="Tool to make the .sh and .jdl scripts necessary to add PF info to background MC samples and then process them with nanoAOD-tools")
    argparser.add_argument("-p", "--processes", required=True, nargs="+", choices=["ALL", "SIG", "BKGD", "BKDGDnoQCD", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD", "M250","M500","M750","M1000","M1250","M1500","M1750","M2000","M2500","M3000","M3500","M4000","M4500","M5000"], help="Which samples to process")
    argparser.add_argument("-y", "--years", required=True, nargs="+", choices=["ALL", "RUN2", "RUN3", "2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"], help="Which years to process")
    argparser.add_argument("-f", "--filesPerJob", required=False, type=int, default=10, help="The number of miniAOD dataset files to process per Condor job")
    argparser.add_argument("--justCount", action="store_true", help="If specified, will just print the number of jobs for each dataset and won't actually make configs")
    args = argparser.parse_args()

    hasSB = [False, False]
    if "ALL" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD", "M250", "M500", "M750", "M1000", "M1250", "M1500", "M1750", "M2000", "M2500", "M3000", "M3500", "M4000", "M4500", "M5000"]
        hasSB = [True, True]
    elif "BKGD" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
        hasSB = [False, True]
    elif "BKGDnoQCD" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST"]
        hasSB = [False, True]
    elif "SIG" in args.processes:
        args.processes = ["M250","M500","M750","M1000","M1250","M1500","M1750","M2000","M2500","M3000","M3500","M4000","M4500","M5000"]
        hasSB = [True, False]
    else:
        for proc in args.processes:
            if proc.startswith("M"):
                hasSB[0] = True
            else:
                hasSB[1] = True
    

    if "ALL" in args.years:
        args.years = ["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"]
    elif "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]
    elif "RUN2" in args.years:
        args.years = ["2016", "2016post", "2017", "2018"]
    
    return args, hasSB

#-------------------------------------------------------------------------------------------------------------------------------------------

def main(args):
    args, hasSB = parseArgs()

    months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    tod = date.today()
    dateStr = str(tod.day) + months[tod.month] + str(tod.year)
    with open("./scriptCreation.log", "a+") as logFile:
        logFile.write("Creating job configs and excecution scripts in directory JobSubmissions" + dateStr + "/" + str(args.years) + "/\n")
        logFile.write("parseArgs returned the following parameters: " + str(args) + "\n")
    
    makeScripts(args, dateStr, hasSB)
        #logFile.write("The cmsDriver command of the last job was: \n")
        #logFile.write(command + "\n\n")

#-------------------------------------------------------------------------------------------------------------------------------------------

def makeScripts(args, dateStr, hasSB):
    dirsToMake = []

    os.system("mkdir Jobs/" + dateStr)
    for year in args.years:
        if year in ["2016", "2016post", "2017", "2018"]:
            era = 2
        else:
            era = 3

        
        print("Making configuration files for " + year)

        if not args.justCount:
            if hasSB[0]:
                command = "eosmkdir /store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/JobOutputs/" + dateStr
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                command = command + "/" + year + "/"
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if hasSB[1]:
                command = "eosmkdir /store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/JobOutputs/" + dateStr
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                command = command + "/" + year + "/"
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            
            
        
        scriptDir = "Jobs/" + dateStr + "/" + year + "/" 

        os.system("mkdir Jobs/" + dateStr + "/" + year)

        if era == 3:
            cmssw_pfNano = "CMSSW_13_0_13"
            cmssw_nano = "CMSSW_14_1_1"
        else: 
            cmssw_pfNano = "CMSSW_10_6_29"
            cmssw_nano = "CMSSW_10_6_30_patch1"

        for proc in args.processes:
            if proc.startswith("M"):
                outDir = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/JobOutputs/" + dateStr + "/" + year + "/"
            else:
                outDir = "/store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/JobOutputs/" + dateStr + "/" + year + "/" + proc + "/"
            
            if not args.justCount and not proc.startswith("M"):
                print("Making directory: " + outDir)
                command = "eosmkdir " + outDir
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

            if proc.startswith("M"):
                dataSets = [sigDatasets_mini[year][proc]]
            else:
                dataSets = bkgdDatasets_mini[year][proc]
            for dataset in dataSets:
                dasCommand = 'dasgoclient --query="file dataset=' + dataset + '"'
                stdout, stderr  = subprocess.Popen(dasCommand, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                stdout = stdout.strip()
                inpDsFiles = stdout.split("\n")
                #print(inpDsFiles)

                if dataset.startswith("/"):
                    if dataset.find("TuneCP5") > 0:
                        subDataset = dataset[1:dataset.find("TuneCP5")]
                    else:
                        subDataset = dataset[1:dataset.find("_")+1]
                else:
                    if dataset.find("TuneCP5") > 0:
                        subDataset = dataset[:dataset.find("TuneCP5")]
                    else:
                        subDataset = dataset[:dataset.find("_")+1]

                nJobs = len(inpDsFiles) // args.filesPerJob

                if len(inpDsFiles) % args.filesPerJob > 0:
                    nJobs += 1
                print("Making", nJobs, "configs with", args.filesPerJob, "input files per job to handle", len(inpDsFiles), subDataset[:-1], "files")
                if args.justCount:
                    continue
                
                for jobN in range(nJobs):
                    start = jobN*args.filesPerJob
                    jobFiles = inpDsFiles[start: start + args.filesPerJob]

                    with open(scriptDir + "run_" + subDataset + year + "_" + str(jobN) + ".sh", "w+") as executable:
                        executable.write("#!/bin/bash\n")
                        executable.write("set -x\n")
                        executable.write("OUTDIR="+ outDir + "\n")
                        executable.write("export HOME=$_CONDOR_SCRATCH_DIR \n") 
                        executable.write('echo "HOME = " $HOME \n')
                        executable.write('echo "Starting job on " `date` #Date/time of start of job\n')

                        executable.write("xrdcp root://cmseos.fnal.gov//store/user/bbarton/"+ cmssw_pfNano + ".tgz .\n")
                        executable.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
                        executable.write("tar -xf " + cmssw_pfNano + ".tgz\n")
                        executable.write("rm " + cmssw_pfNano + ".tgz\n")
                        if era == 2:
                            executable.write("cd " + cmssw_pfNano + "/src/PhysicsTools/PFNano/\n")
                        else:
                            executable.write("cd " + cmssw_pfNano + "/src/btvnano-prod/\n")
                        executable.write("scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile\n")
                        executable.write("eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers\n")

                        for fileN, inpFilePath in enumerate(jobFiles):
                            #executable.write("xrdcp root://cmseos.fnal.gov/" + inpFilePath + " .\n") #Get miniAOD input file
                            #inpFile = inpFilePath.split("/")[-1]
                            executable.write("export INP_FILE=" + inpFilePath + "\n")
                            executable.write("export OUT_FILE=" + subDataset + year + "_" + str(jobN) + "_" + str(fileN) + ".root\n")
                            #confFileName = makeConfigFile(subDataset, year, jobN, fileN, inpFilePath)
                            executable.write("cmsRun baseConf_" + year + ".py\n") #Perform custom nanoAOD production
                            #executable.write("rm " + inpFile + "\n") #Remove miniAOD file

                        #Now setup nanoAOD-tools CMSSW area
                        executable.write('echo "ls of current directory gives:"\n')
                        executable.write("ls $PWD\n")
                        executable.write("cd\n")
                        executable.write("xrdcp root://cmseos.fnal.gov//store/user/bbarton/"+ cmssw_nano + ".tgz .\n")
                        executable.write("tar -xf " + cmssw_nano + ".tgz\n")
                        executable.write("rm " + cmssw_nano + ".tgz\n")
                        executable.write("cd " + cmssw_nano + "/src/\n")
                        executable.write("scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile\n")
                        executable.write("eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers\n")
                        executable.write("cd PhysicsTools/NanoAODTools/condor/\n")
                        if era == 2: 
                            executable.write("mv $HOME/" + cmssw_pfNano + "/src/PhysicsTools/PFNano/" + subDataset +"*.root .\n")
                            executable.write("rm -r $HOME/" + cmssw_pfNano + "\n")
                            executable.write("python condorScript.py " + year + "\n")
                        else:
                            executable.write("mv $HOME/" + cmssw_pfNano + "/src/btvnano-prod/" + subDataset +"*.root .\n")
                            executable.write("rm -r $HOME/" + cmssw_pfNano + "\n")
                            #Perform the NanoAOD-tools processing of the new custom nano+PF files
                            executable.write("python3 condorScript.py " + year + "\n")
                        executable.write("ls $PWD/outputs/\n")
                        outFileName = subDataset + year + "_" + str(jobN) + ".root"
                        #executable.write("hadd -f9 " + outFileName + " " + "$PWD/outputs/" +subDataset+"*.root\n") #* was not being evalualted correctly in jobs (ok locally)
                        executable.write("xrdcp tree.root root://cmseos.fnal.gov/" + outDir + subDataset + year + "_" + str(jobN) + ".root\n")
                        executable.write("XRDEXIT=$?\n")
                        executable.write("if [[ $XRDEXIT -ne 0 ]]; then\n")
                        executable.write('echo "exit code $XRDEXIT, failure in xrdcp"\n')
                        executable.write("exit $XRDEXIT\n")
                        executable.write("fi\n")
                    #End executable creation

                    with open(scriptDir + "jobConfig_" + subDataset + str(jobN) + ".jdl", "w+") as jdlFile:
                        if era == 2:
                            jdlFile.write('+ApptainerImage = "/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7"\n')
                        jdlFile.write('universe = vanilla\n')
                        jdlFile.write("Executable = run_" + subDataset + year + "_" + str(jobN) + ".sh\n")
                        if era == 2:
                            jdlFile.write('request_memory = 5000\n')
                        jdlFile.write('should_transfer_files = YES\n')
                        jdlFile.write('when_to_transfer_output = ON_EXIT\n')
                        jdlFile.write('Output = condor_PFNano-Nano_$(Cluster)_$(Process).stdout\n')
                        jdlFile.write('Error = condor_PFNano-Nano_$(Cluster)_$(Process).stderr\n')
                        jdlFile.write('Log = condor_PFNano-Nano_$(Cluster)_$(Process).log\n')
                        if era == 2:
                            jdlFile.write('+REQUIRED_OS = "rhel7"\n')
                        jdlFile.write('Queue 1\n')
                    #End jdl creation
                #End jobN
            #End dataset
        #End process
    #End year

    #print("Ensure that the following directory paths exist fully:")
    #for dir in dirsToMake:
    #    print(dir)

#-------------------------------------------------------------------------------------------------------------------------------------------

#Makes a cmsRun config file using base files from btvnano-prod, customizing them to use the desired filenames for input/output .root files
def makeConfigFile(subDataset, year, jobN, fileN, inpFile):
    with open("baseConf_" + year + ".py", "r") as baseConfFile:
        baseConf = baseConfFile.read()

    newConf = copy.deepcopy(baseConf)

    nameBase = subDataset + year + "_" + str(jobN) + "_" + str(fileN)

    newConf = newConf.replace("REPLACE_INPUT_REPLACE", inpFile)
    newConf = newConf.replace("REPLACE_OUTPUT_REPLACE", nameBase + ".root")

    confFileName = "conf_" + nameBase + ".py"
    with open(confFileName, "w+") as confFile:
        confFile.write(newConf)

    return confFileName

#-------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    main(args)
