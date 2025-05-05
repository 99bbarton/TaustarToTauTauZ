
import subprocess
import argparse 

processes =  ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
sub_processes = {
    "ZZ" : ["ZZto2L2Nu", "ZZto2L2Q", "ZZto2Nu2Q", "ZZto4L"],
    "WZ" : ["WZto2L2Q", "WZto3LNu", "WZtoLNu2Q"],
    "WW" : ["WWto2L2Nu", "WWto4Q", "WWtoLNu2Q"],
    "WJets" : ["WtoLNu-4Jets"],
    "DY" : ["DYto2L-2Jets_MLL-10to50", "DYto2L-2Jets_MLL-50"],
    "TT" : ["TTto2L2Nu", "TTto4Q", "TTtoLNu2Q"], 
    "ST" : ["TBbarQ_t-channel_4FS", "TWminusto2L2Nu", "TWminusto2L2Nu", "TbarBQ_t-channel_4FS", "TbarWplusto2L2Nu", "TbarWplusto2L2Nu", "TbarWplustoLNu2Q"],
    "QCD" : [],
}

#-------------------------------------------------------------------------------------------------------------------------------------------

def haddFiles():
    argparser = argparse.ArgumentParser(description="Tool to hadd the outputs of the Condor jobs together")
    argparser.add_argument("-d", "--date", required=True, type=str, help="The date in the form e.g. 1Apr2025 that the jobs were created on")
    argparser.add_argument("-y", "--year", required=True, choices=["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"], help="What year the jobs correspond to")
    argparser.add_argument("-p", "--processes", required=True, nargs="+", choices=["ALL", "ALLnoQCD", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"], help="Which samples to process")
    argparser.add_argument("-v", "--version", required=True, type=str, help="A unique string to denote the new file area on EOS.")
    args = argparser.parse_args()

    if "ALL" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
    elif "ALLnoQCD" in args.processes:
        args.processes = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST"]

    IN_DIR_BASE = "/store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/JobOutputs/" + args.date + "/"
    OUT_DIR_BASE = "/store/user/bbarton/TaustarToTauTauZ//BackgroundMC/PFNano/"

    
    inDir = IN_DIR_BASE + args.year + "/"
    outDir = OUT_DIR_BASE + args.year + "/" + args.version + "/"

    print("Making output directory: " + outDir) 
    command  = "eosmkdir " + outDir
    stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    for proc in args.processes:
        inDir += proc + "/"

        print("Starting " + args.year + " " + proc +  " samples...")
        for subproc in sub_processes[proc]:
            print("\thadd'ing " + subproc + " samples")
            command = "hadd root://cmseos.fnal.gov/" + outDir + subproc + "_" + args.year + ".root `xrdfsls -u " + inDir + " | grep " + subproc + "`"
            stdout, stderr  = subprocess.Popen(command, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

#-------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    haddFiles()
