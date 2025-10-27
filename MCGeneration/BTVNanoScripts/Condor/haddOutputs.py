
import subprocess
import argparse 

import sys
sys.path.append("../../../Framework/")
from datasets import processes, procToSubProc_run2, procToSubProc_run3, procToSubProc_run3_legacy

#-------------------------------------------------------------------------------------------------------------------------------------------

def haddFiles():
    argparser = argparse.ArgumentParser(description="Tool to hadd the outputs of the Condor jobs together")
    argparser.add_argument("-d", "--date", required=True, type=str, help="The date in the form e.g. 1Apr2025 that the jobs were created on")
    argparser.add_argument("-y", "--year", required=True, choices=["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"], help="What year the jobs correspond to")
    argparser.add_argument("-p", "--processes", required=True, nargs="+", choices=["SIG", "BKGD", "BKDGDnoQCD", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD", "M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"], help="Which samples to process")
    argparser.add_argument("-v", "--version", required=True, type=str, help="A unique string to denote the new file area on EOS.")
    argparser.add_argument("-l", "--legacy", required=False, action="store_true", help="If specified, uses old version of procToSubProc for Run3")
    args = argparser.parse_args()

    if "BKGD" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
        inDirBase = "/store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/JobOutputs/" + args.date + "/"
        outDirBase = "/store/user/bbarton/TaustarToTauTauZ//BackgroundMC/PFNano/"
    elif "BKGDnoQCD" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST"]
        inDirBase = "/store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/JobOutputs/" + args.date + "/"
        outDirBase = "/store/user/bbarton/TaustarToTauTauZ//BackgroundMC/PFNano/"
    elif "SIG" in args.processes:
        args.processes = ["M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"]
        inDirBase = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/JobOutputs/" + args.date + "/"
        outDirBase = "/store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/"
    
    inDirBase = inDirBase + args.year + "/"
    outDir = outDirBase + args.year + "/" + args.version + "/"

    print("Making output directory: " + outDir) 
    command  = "eosmkdir " + outDir
    stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


    if args.year in ["2016", "2016post", "2017", "2018"]:
        procToSubProc = procToSubProc_run2
    elif args.year in ["2022", "2022post", "2023", "2023post"]:
        if args.legacy:
            procToSubProc = procToSubProc_run3_legacy
        else:
            procToSubProc = procToSubProc_run3
    
    
    for proc in args.processes:
        if not proc.startswith("M"):
            inDir = inDirBase + proc + "/"
        else:
            inDir = inDirBase

        print("Starting " + args.year + " " + proc +  " samples...")
        
        if proc.startswith("M"):
            print("\thadd'ing " + proc + " samples")
            command = "hadd -f9 root://cmseos.fnal.gov/" + outDir + "/taustarToTauZ_" + proc.lower() + "_" + args.year + ".root `xrdfsls -u " + inDir + " | grep " + proc.lower() + "_`"
            stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print(stdout)
            if len(stderr) > 0:
                print("STDERR ", stderr)
        else:
            for subproc in procToSubProc[proc]:
                print("\thadd'ing " + subproc + " samples")
                command = "hadd -f9 root://cmseos.fnal.gov/" + outDir + subproc + "_" + args.year + ".root `xrdfsls -u " + inDir + " | grep " + subproc + "`"
                stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(stdout)
                if len(stderr) > 0:
                    print("STDERR ", stderr)
            

#-------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    haddFiles()
