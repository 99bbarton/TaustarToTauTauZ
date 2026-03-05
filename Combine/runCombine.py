
#Script to run Combine on the datacards in ./Datacards/



import os
import sys
import argparse

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def parseArgs():
    argparser = argparse.ArgumentParser(description="Utility to script to run Combine")
    #General options
    argparser.add_argument("-i", "--inDir", default="./", help="A path to the directory containing datacards")
    argparser.add_argument("-f", "--files", nargs="+", default=[],help="A specific datacard file to run over. It should be in the path specified by --inDir")
    argparser.add_argument("-t", "--toys", type=int, default=100, help="The number of toys to use")
    argparser.add_argument("-n", "--nameTag", type=str, default="", help="A specific naming tag (will be present in output .root file)")
    argparser.add_argument("-o", "--outDir", default="./", help="A directory path for produced output files")
    #Action specific options
    argparser.add_argument("-l", "--limits", action="store_true", help="If specified, runs AsymptoticLimits method")
    argparser.add_argument("-s", "--shapify", action="store_true", help="If specified, will make fake shape-analysis datacards out of the input cards. Prereq for --fitDiag")
    argparser.add_argument("-d", "--fitDiag", action="store_true", help="If specified, runs FitDiagnostics method. --shapify must also be specified OR have been previously run")
    argparser.add_argument("-p", "--plots", action="store_true", help="If specified, will run FitDiagnostics with --plots option")
    argparser.add_argument("-m", "--impacts", action="store_true", help="If specified, will make Impact plots")
    
    args = argparser.parse_args()
    
    if len(args.files) == 0:
        args.files = os.listdir(args.inDir)

    if not os.path.exists(args.outDir):
        os.system(f"mkdir {args.outDir}")

    return args

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def limits(args):
    for dc in args.files:
        if not dc.endswith(".txt"):
            continue

        mass = dc.split("_")[-1][:-4]
        print("\n\n =================================== Running Asymptotic Limits for M" + mass + "  ===================================== \n\n")
        command = f"combine -M AsymptoticLimits {args.inDir}{dc} -t {args.toys} -m {mass}"
        if len(args.nameTag) > 0:
            command += " -n " + args.nameTag
        os.system(command)

        if args.outDir != "./":
            os.system(f"mv higgsCombine*.AsymptoticLimits.mH{mass}.*.root {args.outDir}/")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def fitDiagnostics(args):
    if args.shapify:
        if not os.path.exists(f"{args.inDir}/FakeShapes/"):
            os.system(f"mkdir {args.inDir}/FakeShapes/")
        for dc in args.files:
            if dc.startswith("datacard") and dc.endswith(".txt"):
                os.system(f"combineCards.py {args.inDir}{dc} -S > {args.inDir}/FakeShapes/{dc[:-4]}_fakeShape.txt")
    
    for dc in args.files:
        if not dc.endswith(".txt"):
            continue
        
        dc = dc[:-4] + "_fakeShape.txt"
        mass = dc.split("_")[-2]
        print("\n\n =================================== Running FitDiagnostics for M" + mass + "  ===================================== \n\n")
        if args.shapify:
            command = f"combine -M FitDiagnostics {args.inDir}/FakeShapes/{dc} -m {mass} -t {args.toys} --forceRecreateNLL"
        else:
            command = f"combine -M FitDiagnostics {args.inDir}{dc} -m {mass} -t {args.toys} --forceRecreateNLL"
        if len(args.nameTag) > 0:
            command += " -n " + args.nameTag
        if args.plots:
            command += " --plots"
        os.system(command)

        #Move output files
        os.system(f"mv fitDiagnosticsTest.root {args.outDir}/fitDiagnosticsTest_{mass}.root")
        os.system(f"mv higgsCombine*.FitDiagnostics.mH{mass}.*.root {args.outDir}/")
        if args.plots:
            for fil in os.listdir("./"): # WARNING: This will move and rename any .png in the CWD 
                if fil.endswith(".png"):
                    os.system(f"mv {fil} {args.outDir}/{fil[:-4]}_{mass}.png")


        #Run diff nuissances to record nuissance parameter values and pulls
        os.system(f"python3 test/diffNuisances.py {args.outDir}/fitDiagnosticsTest_{mass}.root --all --abs > {args.outDir}/diffNuissOut_{mass}.txt")
        os.system(f"python3 test/diffNuisances.py {args.outDir}/fitDiagnosticsTest_{mass}.root --all --pullDef unconstPullAsym >> {args.outDir}/diffNuissOut_{mass}.txt")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def impacts(args):
    for dc in args.files:
        if not dc.endswith(".txt"):
            continue

        mass = dc.split("_")[-1][:-4]
        print("\n\n =================================== Making Impact Plots for M" + mass + "  ===================================== \n\n")
        os.system(f"text2workspace.py {args.inDir}/{dc} -m {mass}")
        os.system(f"combineTool.py -M Impacts -d {dc[:-4]}.root -m {mass} --robustFit 1 --doInitialFit")
        os.system(f"combineTool.py -M Impacts -d {dc[:-4]}.root -m {mass} --robustFit 1 --doFits")
        os.system(f"combineTool.py -M Impacts -d {dc[:-4]}.root -m {mass} -o impacts.json")
        os.system(f"plotImpacts.py -i impacts.json -o impacts_{mass} --label-size 0.06 --left-margin 0.2")

        if args.outDir != "./":
            os.system(f"mv impacts_{mass}.* {args.outDir}/")

        os.system(f"rm {dc[:-4]}.root")
        os.system("rm impacts.json")
        os.system("rm higgsCombine_initialFit_*.root")
        os.system("rm higgsCombine_paramFit*.root")
        

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
if __name__ == "__main__":
    args = parseArgs()
    
    if args.limits:
        limits(args)
    if args.fitDiag:
        fitDiagnostics(args)
    if args.impacts:
        impacts(args)
