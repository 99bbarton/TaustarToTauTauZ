#Make a cut flow table for MC and data


import os
import sys
import argparse
from ROOT import TChain
from tabulate import tabulate

sys.path.append("../Framework/")
from datasets import procToSubProc_run2, procToSubProc_run3, years_run2

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

cuts = {
	"ETau": ["Z_dm >=0 && Z_dm <=2", "Z_mass > 61 && Z_mass < 151", "Z_dauDR < 0.8", "ETau_havePair", "ETau_sign<0", "ETau_ETauDPhi<2.8","(TMath:Cos(ETau_ETauDPhi)*TMath:Cos(ETau_ETauDPhi))<0.99", "ETau_ETauDR>1.5", "ETau_haveTrip", "Trig_tau", "ETau_trigMatchTau", "ETau_minCollM >= ETau_visM", "ETau_isCand",  "ObjCnt_nBTags < 2", "Tau_pt[ETau_tauIdx] > 200", "Electron_pt[ETau_eIdx] > 100"],
	"MuTau" : ["Z_dm >=0 && Z_dm <=2", "Z_mass > 61 && Z_mass < 151", "Z_dauDR < 0.8", "MuTau_havePair", "MuTau_sign<0", "MuTau_MuTauDPhi<2.8","(TMath:Cos(MuTau_MuTauDPhi)*TMath:Cos(MuTau_MuTauDPhi))<0.99", "MuTau_MuTauDR>1.5", "MuTau_haveTrip", "Trig_tau", "MuTau_trigMatchTau", "MuTau_minCollM >= MuTau_visM", "MuTau_isCand", "Tau_pt[MuTau_tauIdx] > 200", "Muon_pt[MuTau_muIdx] > 100"],
	"TauTau" : ["Z_dm >=0 && Z_dm <=2", "Z_mass > 61 && Z_mass < 151", "Z_dauDR < 0.8", "TauTau_havePair", "TauTau_sign<0", "TauTau_TauTauDPhi<2.8","(TMath:Cos(TauTau_TauTauDPhi)*TMath:Cos(TauTau_TauTauDPhi))<0.99", "TauTau_TauTauDR>1.5", "TauTau_haveTrip", "Trig_tau", "TauTau_trigMatchTau", "TauTau_minCollM >= TauTau_visM", "TauTau_isCand", "Tau_pt[TauTau_tau1Idx_TAUES_] > 200", "Tau_pt[TauTau_tau2Idx_TAUES_] > 200"]
}

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

def parseArgs():
    argparser = argparse.ArgumentParser(description="Make a N-1 cutflow table")
    argparser.add_argument("-y", "--years", nargs="+", choices=["2022post", "2022", "2023post", "2023", "RUN3"], default=["RUN3"] help="Which year's data to use")
    argparser.add_argument("-p", "--processes", type=str, nargs="+", choices = ["TT", "ST", "DY", "ZZ", "WZ", "WW", "DATA"], default=["TT", "ST"], help="Which processes to use")
    argparser.add_argument("-c", "--channels", nargs="+", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use" )
    args = argparser.parse_args()


    if "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]

    if "ALL" in args.channels:
        args.channels = ["ETau", "MuTau", "TauTau"]

    return args

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

def makeNm1Cutflow(args):

    results = {}
    
    for proc in args.processes:

        chain = TChain("Events")
        if proc == "DATA":
            basePath = "root://cmsxrootd.fnal.gov/" + str(os.environ["TSTTZDATA"])
            for year in args.years:
                chain.Add(basePath + "data_" + year + ".root")
        else:
            for year in args.years:
                basePath = "root://cmsxrootd.fnal.gov/" + str(os.environ["BKGD_" + year])
                if year in years_run2:
                    subProcs = procToSubProc_run2[proc]
                else:
                    subProcs = procToSubProc_run3[proc]
                for subProc in subProcs:
                    chain.Add(basePath + subProc + "_" + year + ".root")
        
        totEvts = chain.GetEntries()

        for ch in args.channels:
            allCutStr = "("
            for cut in cuts[ch]:
                allCutStr += cut + "&&"
            allCutStr = allCutStr[:-2] + ")"
            nAllCuts = chain.GetEntries(allCutStr)

            for cut in cuts[ch]:
                cutStr = allCutStr.replace(cut, "1>0")
                nNotThisCut = chain.GetEntries(cutStr)
                percRem = (nNotThisCut - nAllCuts) / totEvts * 100


            if cut not in results[ch]:
                results[ch][cut] = {}

            results[ch][cut][proc] = percRem


    for ch in args.channels:
        print("\n")
        print("=" * 80)
        print(f"{ch} Channel")
        print("=" * 80)

        table = []

        headers = ["Cut"] + args.processes

        for cut in cuts[ch]:
            row = [cut]

            for proc in args.processes:
                val = results[ch][cut].get(proc, 0.0)
                row.append(f"{val:.2f}%")

            table.append(row)

        print(tabulate(table, headers=headers, tablefmt="grid"))

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    makeNm1Cutflow(args)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

