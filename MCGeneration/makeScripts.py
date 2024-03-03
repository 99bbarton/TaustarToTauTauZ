# Script to produce the various shell scripts, configuration files, etc necessary to produce signal MC via Condor

import os
from datetime import date
import argparse

##----------------------------------------------------------------------------------------------------------------------------------

stageToCMSSW = {"2017" : ["","CMSSW_10_6_30_patch1","CMSSW_10_6_17_patch1","CMSSW_10_6_17_patch1","CMSSW_9_4_14_UL_patch1","CMSSW_10_6_17_patch1","CMSSW_10_6_20","CMSSW_10_6_26"] ,"2018" : ["","CMSSW_10_6_30_patch1","CMSSW_10_6_17_patch1","CMSSW_10_6_17_patch1","CMSSW_10_2_16_UL","CMSSW_10_6_17_patch1","CMSSW_10_6_20","CMSSW_10_6_26"]}
months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

##----------------------------------------------------------------------------------------------------------------------------------

def makeScripts(args, dateStr):

    outDir = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/" + dateStr + "/S" + str(args.stage) + "/" + args.outDir

    os.system("mkdir CondorScripts/" + dateStr)
    os.system("mkdir CondorScripts/" + dateStr + "/S" + str(args.stage))
    if len(args.outDir) > 1:
        os.system("mkdir CondorScripts/" + dateStr + "/S" + str(args.stage) + "/" + args.outDir)

    cmssw = stageToCMSSW[args.year][args.stage]

    inDir = ""
    if args.stage != 1:
        inDir = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/" + args.inDir

    print("\nThe following directory path must exist completely for the produced scripts to successfully execute:")
    print(outDir)
    print("The following CMSSW version .tgz must be available at /store/user/bbarton/ for the produced scripts to successfully execute:")
    print(cmssw + "\n")

    decay = ""
    if args.decay == "Z":
        decay = "TauZ"
    else:
        decay = "WNu"

    for jobN in range(1, args.nJobs+1):

        filebase = "m" + args.mass + "_s" + str(args.stage) + "_" + str(jobN)
        inFile = inDir + "/taustarToTau"+decay+"_m"+args.mass+"_s" + str(args.stage - 1) + "_" + str(jobN) + ".root"
        filename = "taustarToTau"+decay+"_" + filebase

        command = buildCommand(args, jobN)

        #Executable .sh scripts
        with open("CondorScripts/" + dateStr + "/S" + str(args.stage) + "/" + args.outDir + "run_" + filebase + ".sh", "w+") as outFile:
            outFile.write("#!/bin/bash\n")
            outFile.write("set -x\n")
            outFile.write("OUTDIR="+ outDir + "\n")
            outFile.write("export HOME=$_CONDOR_SCRATCH_DIR \n") # Needed for dasgoclient to be able to access dasMaps for DAS dataet access in S3
            outFile.write('echo "HOME = " $HOME \n')

            outFile.write('echo "Starting job on " `date` #Date/time of start of job\n')
            outFile.write('echo "Running on: `uname -a`" #Condor job is running on this node\n')
            outFile.write('echo "System software: `cat /etc/redhat-release`" #Operating System on that node\n')

            outFile.write("xrdcp root://cmseos.fnal.gov//store/user/bbarton/"+ cmssw + ".tgz .\n")
            outFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
            outFile.write("tar -xf " + cmssw + ".tgz\n")
            outFile.write("rm " + cmssw + ".tgz\n")
            outFile.write("cd " + cmssw + "/src/\n")
            outFile.write("scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile\n")
            outFile.write("eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers\n")

            if args.stage != 1:
                outFile.write("xrdcp root://cmseos.fnal.gov//" + inFile + " .\n")

            outFile.write(command + "\n") 
            outFile.write("cmsRun " + filename + ".py\n")

            outFile.write("#Copy files to eos area\n")

            outFile.write('echo "*******************************************"\n')
            outFile.write('echo "xrdcp output for condor to "\n')
            outFile.write("echo $OUTDIR\n")

            outFile.write("xrdcp -f " + filename + ".root " + "root://cmseos.fnal.gov/${OUTDIR}\n")
            outFile.write("XRDEXIT=$?\n")
            outFile.write("if [[ $XRDEXIT -ne 0 ]]; then\n")
            outFile.write('echo "exit code $XRDEXIT, failure in xrdcp"\n')
            outFile.write("exit $XRDEXIT\n")
            outFile.write("fi\n")

            outFile.write("hostname\n")
            outFile.write("date\n")

        #Job configuration files
        with open("CondorScripts/" + dateStr+"/S" + str(args.stage) + "/" + args.outDir + "jobConfig_" + filebase + ".jdl", "w") as jdlFile:
            jdlFile.write('universe = vanilla\n')
            jdlFile.write("Executable = run_" + filebase + ".sh\n")
            if args.memory:
                jdlFile.write('request_memory = ' + args.memory +'\n')
            jdlFile.write('should_transfer_files = YES\n')
            jdlFile.write('when_to_transfer_output = ON_EXIT\n')
            jdlFile.write('Output = condor_MCGen_s' + str(args.stage) + '_$(Cluster)_$(Process).stdout\n')
            jdlFile.write('Error = condor_MCGen_s' + str(args.stage) + '_$(Cluster)_$(Process).stderr\n')
            jdlFile.write('Log = condor_MCGen_s' + str(args.stage) + '_$(Cluster)_$(Process).log\n')
            jdlFile.write('Queue 1\n')

    return command
##----------------------------------------------------------------------------------------------------------------------------------

def buildCommand(args, jobN):
    command = ""

    decay = ""
    if args.decay == "Z":
        decay = "TauZ"
    else:
        decay = "WNu"

    if args.stage == 1:
        if args.year == "2017":
            command = "cmsDriver.py Configuration/GenProduction/python/taustarToTau"+decay+"_m"+ args.mass + ".py --python_filename taustarToTau"+decay+"_m"+ args.mass+"_s1_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s1_"+str(jobN)+".root --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --geometry DB:Extended --era Run2_2017 --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py Configuration/GenProduction/python/taustarToTau"+decay+"_m"+ args.mass + ".py --python_filename taustarToTau"+decay+"_m"+ args.mass+"_s1_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s1_"+str(jobN)+".root --conditions 106X_upgrade2018_realistic_v4 --beamspot Realistic25ns13TeVEarly2018Collision --step GEN --geometry DB:Extended --era Run2_2018 --no_exec --mc -n " + str(args.nEvents)
    elif args.stage == 2:
        if args.year == "2017":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s2_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s2_"+str(jobN)+".root --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step SIM --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s1_"+str(jobN)+".root --era Run2_2017 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s2_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s2_"+str(jobN)+".root --conditions 106X_upgrade2018_realistic_v11_L1v1 --beamspot Realistic25ns13TeVEarly2018Collision --step SIM --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s1_"+str(jobN)+".root --era Run2_2018 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
    elif args.stage == 3:
        if args.year == "2017":
            command = 'cmsDriver.py --python_filename taustarToTau'+decay+'_m'+args.mass+'_s3_'+str(jobN)+'.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-DIGI --fileout file:taustarToTau'+decay+'_m'+args.mass+'_s3_'+str(jobN)+'.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX" --conditions 106X_mc2017_realistic_v6 --step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --geometry DB:Extended --filein file:taustarToTau'+decay+'_m'+args.mass+'_s2_'+str(jobN)+'.root --datamix PreMix --era Run2_2017 --runUnscheduled --no_exec --mc -n ' + str(args.nEvents)
        elif args.year == "2018":
            command = 'cmsDriver.py --python_filename taustarToTau'+decay+'_m'+args.mass+'_s3_'+str(jobN)+'.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-DIGI --fileout file:taustarToTau'+decay+'_m'+args.mass+'_s3_'+str(jobN)+'.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX" --conditions 106X_upgrade2018_realistic_v11_L1v1 --step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --geometry DB:Extended --filein file:taustarToTau'+decay+'_m'+args.mass+'_s2_'+str(jobN)+'.root --datamix PreMix --era Run2_2018 --runUnscheduled --no_exec --mc -n ' + str(args.nEvents)
    elif args.stage == 4:
        if args.year == "2017":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".root --conditions 94X_mc2017_realistic_v15 --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' --step HLT:2e34v40 --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s3_"+str(jobN)+".root --era Run2_2017 --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".root --conditions 102X_upgrade2018_realistic_v15 --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' --step HLT:2018v32 --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s3_"+str(jobN)+".root --era Run2_2018 --no_exec --mc -n " + str(args.nEvents)
    elif args.stage == 5:
        if args.year == "2017":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".py --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".root --conditions 106X_mc2017_realistic_v6 --step RAW2DIGI,L1Reco,RECO,RECOSIM,EI --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".root --era Run2_2017 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".py --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".root --conditions 106X_upgrade2018_realistic_v11_L1v1 --step RAW2DIGI,L1Reco,RECO,RECOSIM,EI --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s4_"+str(jobN)+".root --era Run2_2018 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
    elif args.stage == 6:
        if args.year == "2017":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".root --conditions 106X_mc2017_realistic_v9 --step PAT --procModifiers run2_miniAOD_UL --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".root --era Run2_2017 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".root --conditions 106X_upgrade2018_realistic_v16_L1v1 --step PAT --procModifiers run2_miniAOD_UL --geometry DB:Extended --filein file:taustarToTau"+decay+"_m"+args.mass+"_s5_"+str(jobN)+".root --era Run2_2018 --runUnscheduled --no_exec --mc -n " + str(args.nEvents)
    elif args.stage == 7:
        if args.year == "2017":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s7_"+str(jobN)+".py --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s7_"+str(jobN)+".root --conditions 106X_mc2017_realistic_v9 --step NANO --filein file:taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec --mc -n " + str(args.nEvents)
        elif args.year == "2018":
            command = "cmsDriver.py --python_filename taustarToTau"+decay+"_m"+args.mass+"_s7_"+str(jobN)+".py --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:taustarToTau"+decay+"_m"+args.mass+"_s7_"+str(jobN)+".root --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --filein file:taustarToTau"+decay+"_m"+args.mass+"_s6_"+str(jobN)+".root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec --mc -n " + str(args.nEvents)

    return command

##----------------------------------------------------------------------------------------------------------------------------------

def parseArgs():
    argparser = argparse.ArgumentParser(description="Tool to make the .sh and .jdl scripts necessary to produce Taustar->TauTauZ signal MC via Condor")
    argparser.add_argument("-s","--stage", required=True, choices=[1,2,3,4,5,6,7], type=int, help="Which stage of generation to produce scripts for")
    argparser.add_argument("-y", "--year", required=True, choices=["2015","2016","2017","2018"], type=str, help="The year to produce MC for")
    argparser.add_argument("-m", "--mass", required=True, choices=["250", "500", "750", "1000", "1250", "1500", "1750", "2000", "2250", "2500", "2750", "3000", "3250", "3500", "3750", "4000", "4250", "4500", "4750", "5000", "5250", "5500", "5750", "6000"], help="The taustar mass to produce scripts for")
    argparser.add_argument("-d","--decay", required=True, choices=["Z", "W"], help="Whether the sample being produced is a taustar->tau+Z decay or taustar->W+nu decay")
    argparser.add_argument("-i","--inDir", type=str, help="A directory in /store/user/bbarton/TaustarToTauTauZ/SignalMC/ to find input files. Required if stage > 1")
    argparser.add_argument("-n","--nEvents", type=int, default=100, help="How many events per job to process")
    argparser.add_argument("-j", "--nJobs", type=int, default=1, help="How many jobs to create scripts for" )
    argparser.add_argument("-o", "--outDir", type=str, default="./", help="A directory within the stage# directory to put output scripts and eventual job output rootfiles")
    argparser.add_argument("--memory", help="The amount of RAM to request per job in MB (condor default is 2100). Larger requests will get lower queue priority")

    args = argparser.parse_args()

    if args.stage > 1 and not args.inDir:
        print("If stage > 1, a directory containing input files must be passed via the -i/--inDir argument")
        exit(-1)

    if not args.outDir.endswith("/"):
        args.outDir = args.outDir + "/"

    return args

##----------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()

    tod = date.today()
    dateStr = str(tod.day) + months[tod.month] + str(tod.year)
    with open("./scriptCreation.log", "a+") as logFile:
        logFile.write("Creating job configs and excecution scripts in directory " + dateStr + "/S" + str(args.stage) + "/" + args.outDir + "\n")
        logFile.write("paseArgs returned the following parameters: " + str(args) + "\n")
    
        command = makeScripts(args, dateStr)
        logFile.write("The cmsDriver command of the last job was: \n")
        logFile.write(command + "\n\n")

##----------------------------------------------------------------------------------------------------------------------------------
