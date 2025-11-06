#Make histograms of the number of signal and background in each bin (0=signal L-band)

  ###########################################################
  #                      >          <                     + #                      
  #                      >          <                   +   #                       
  #                      >          <       2         +     #                      
#M#                      >          <               +       #                      
#A#          3           >          <             +         #                      
#X#                      >          <           +           #                      
  #                      >          <         +             #                      
  #                      >          <       +               #                      
  # <<<<<<<<<<<<<<<<<<<<<<          <     +                 #                     
  #                            0    <   +                   #                 
  #                                 < +                     #                   
  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                       #                     
  #                               +                         #                    
  #                             +                           #                   
  #                           +                             #                   
  #                         +                               #                    
  #           1           +                                 #                    
  #                     +                                   #                    
  #                   +               NOT                   #                      
  #                 +               POSSIBLE                #                     
  #               +                                         #                     
  #             +                                           #                     
  #           +                                             #                     
  #         +                                               #                    
  #       +                                                 #                 
  #     +                                                   #                
  #   +                                                     #                
  # +                                                       #                      
  ###########################################################
                                                   #MIN
#----------------------------------------------------------------------------------------------------------------------------------------------#

import argparse
import os
import sys
from array import array
from tabulate import tabulate

from ROOT import TFile, TCanvas, TTree, TChain, TH1F, TGraph, TLegend, gStyle, THStack, TMultiGraph, EnableImplicitMT
EnableImplicitMT()  # use all available cores for ROOT internal parallelism

sys.path.append("../Framework/")
from datasets import processes, procToSubProc_run2, procToSubProc_run3, procToSubProc_run3_legacy
from mcWeights import getWeight

#----------------------------------------------------------------------------------------------------------------------------------------------#

#These are the symmetric L-band edges, i.e. mass +/- (halfWidth*mass)
massToLEdges_asymm = {
    "250" : [175.0, 325.0],
    "500" : [350.0, 650.0],
    "750" : [525.0, 975.0],
    "1000" : [700.0, 1300.0],
    "1500" : [1300.0, 2250.0],
    "2000" : [1500.0, 3000.0],
    "2500" : [1500.0, 4500.0],
    "3000" : [1700.0, 5400.0],
    "3500" : [2000.0, 6300.0],
    "4000" : [2250.0, 7200.0],
    "4500" : [2500.0, 8100.0],
    "5000" : [2750.0, 9000.0]
}


#These are the symmetric L-band edges, i.e. mass +/- (halfWidth*mass)
massToLEdges = {
    "250" : [175.0, 325.0],
    "500" : [350.0, 650.0],
    "750" : [525.0, 975.0],
    "1000" : [700.0, 1300.0],
    "1500" : [750.0, 2250.0],
    "2000" : [1000.0, 3000.0],
    "2500" : [500.0, 4500.0],
    "3000" : [600.0, 5400.0],
    "3500" : [700.0, 6300.0],
    "4000" : [800.0, 7200.0],
    "4500" : [900.0, 8100.0],
    "5000" : [1000.0, 9000.0]
}

massToLHalfWidths = {
    "250"  : 0.3,  
    "500"  : 0.3,
    "750"  : 0.3,
    "1000" : 0.3,
    "1500" : 0.5,
    "2000" : 0.5,
    "2500" : 0.8,
    "3000" : 0.8,
    "3500" : 0.8,
    "4000" : 0.8,
    "4500" : 0.8,
    "5000" : 0.8
}

#----------------------------------------------------------------------------------------------------------------------------------------------#

def parseArgs():
    argparser = argparse.ArgumentParser(description="Make plots of the number of signal and background events in each of the 2D collinear mass bins")
    argparser.add_argument("-y", "--years", nargs="+", choices=["ALL", "2016","2016post", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to use")
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["ALL","SIG_DEF", "250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], default=["ALL"], help = "Which signal masses to use. Default is ALL")
    argparser.add_argument("-c", "--channels", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use. Default ALL " )
    argparser.add_argument("-b", "--nBins", type=int, choices=[2, 4], default=4, help="Specify 2 to use binning scheme of signal L-band + all rest of plane. 4 to use L-band + 3 bkgd regions" )
    argparser.add_argument("-a", "--asymm", action="store_true", help="If specified, will use assymetric L-bands. Otherwise, symmetric band edges are used.")
    argparser.add_argument("-l", "--log", action="store_true", help="Specify to set the y-axis of plots to log scale.")
    argparser.add_argument("--printLEdges", action="store_true", help="If specified, will printe the L-bin edges corresponding to the L half-widths")
    argparser.add_argument("--latex", action="store_true", help="If specified, will print a the predicted events table in LaTeX format")
    argparser.add_argument("--legacy", action="store_true", help="If specified, will use legacy Run3 process-to-subprocess translation (for V0 processing)")
    args = argparser.parse_args()  

    if "ALL" in args.years:
        args.years = ["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"]
    elif "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]
    elif "RUN2" in args.years:
        args.years = ["2016","2016post", "2017", "2018"]
    
    if "ALL" in args.masses:
        args.masses = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"]
    elif "SIG_DEF" in args.masses:
        args.masses = ["250", "1000", "3000", "5000"]

    if "ALL" in args.channels:
        args.channels = ["ETau", "MuTau", "TauTau"]

    return args

#----------------------------------------------------------------------------------------------------------------------------------------------#

#Reworked version of original function to change loop ordering for improved file I/O efficiency
def makeEvtPredHists(args):
    canv = TCanvas("canv_binScheme", "N Events in 2D Collinear Mass Bins", 1200, 800)
    leg = TLegend(0.7, 0.7, 0.9, 0.9)
    gStyle.SetOptStat(0)
    sigCol = 603
    bkgdCol = 921

    baseCutStrs = []
    baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && ( (LOW_EDGE<=CHANNEL_minCollM && CHANNEL_minCollM <= HIGH_EDGE ) || (LOW_EDGE<= CHANNEL_maxCollM && CHANNEL_maxCollM <= HIGH_EDGE) ))")
    if args.nBins == 4:
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_maxCollM < LOW_EDGE) )")
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_minCollM > HIGH_EDGE) )")
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE) )")
    else:
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && ( (CHANNEL_maxCollM < LOW_EDGE) || (CHANNEL_minCollM > HIGH_EDGE) || ((CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE)) ) )")

    # prepare histograms for each mass
    massBins = array("f", [float(m) for m in args.masses])
    sigHists = {}
    bkgdHists = {}
    sigEvtPerMass = {m: 0 for m in args.masses}
    bkgdEvtPerMass = {m: 0 for m in args.masses}
    eventsPerProc = {m: {"SIG": 0, "ZZ": 0, "WZ": 0, "WW": 0, "WJets": 0, "DY": 0, "TT": 0, "ST": 0, "QCD": 0} for m in args.masses}

    for mass in args.masses:
        sigHists[mass] = TH1F(f"sig_m{mass}", f"Signal m{mass};Bin;Events", args.nBins, -0.5, -0.5 + args.nBins)
        bkgdHists[mass] = TH1F(f"bkgd_m{mass}", f"Background m{mass};Bin;Events", args.nBins, -0.5, -0.5 + args.nBins)

    for year in args.years:
        print(f"Processing year = {year}")

        for mass in args.masses:
            print(f"\tProcessing mass = {mass}")
            filePath = os.environ["ROOTURL"] + os.environ["SIG_" + year] + f"taustarToTauZ_m{mass}_{year}.root"
            sigFile = TFile.Open(filePath, "r")
            sigTree = sigFile.Get("Events")

            if args.asymm:
                lBinEdges = massToLEdges_asymm[mass]
            else:
                lBinEdges = massToLEdges[mass]

            for ch in args.channels:
                for bin in range(args.nBins):
                    cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                    cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                    cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))
                    weight = getWeight("M" + mass, year, xs=True)
                    nEvts = sigTree.GetEntries(cutStr)

                    sigHists[mass].Fill(sigHists[mass].GetBinCenter(bin + 1), nEvts * weight)
                    if bin == 0:
                        sigEvtPerMass[mass] += nEvts * weight
                        eventsPerProc[mass]["SIG"] += nEvts * weight
            sigFile.Close()

        dirPath = os.environ["ROOTURL"] + os.environ["BKGD_" + year]
        for proc in processes:
            print(f"\tProcessing proc = {proc}")
            if year in ["2022", "2022post", "2023", "2023post"]:
                subProcs = procToSubProc_run3_legacy[proc] if args.legacy else procToSubProc_run3[proc]
            else:
                subProcs = procToSubProc_run2[proc]

            for subProc in subProcs:
                filePath = dirPath + subProc + "_" + year + ".root"
                bkgdFile = TFile.Open(filePath, "r")
                try:
                    bkgdTree = bkgdFile.Get("Events")
                    if not bkgdTree or bkgdTree.GetEntries() == 0:
                        print("Warning: empty or missing Events tree:", filePath)
                        bkgdFile.Close()
                        continue
                except:
                    print("Warning: could not read tree in", filePath)
                    bkgdFile.Close()
                    continue

                for mass in args.masses:
                    if args.asymm:
                        lBinEdges = massToLEdges_asymm[mass]
                    else:
                        lBinEdges = massToLEdges[mass]

                    for ch in args.channels:
                        for bin in range(args.nBins):
                            cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                            cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                            cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))

                            weight = getWeight(subProc, year, xs=True)
                            nEvts = bkgdTree.GetEntries(cutStr)

                            bkgdHists[mass].Fill(bkgdHists[mass].GetBinCenter(bin + 1), nEvts * weight)
                            if bin == 0:
                                bkgdEvtPerMass[mass] += nEvts * weight
                                eventsPerProc[mass][proc] += nEvts * weight

                bkgdFile.Close()

    for i, mass in enumerate(args.masses):
        sigHist = sigHists[mass]
        bkgdHist = bkgdHists[mass]
        sigHist.SetLineWidth(3)
        sigHist.SetLineColor(sigCol)
        bkgdHist.SetLineColor(bkgdCol)
        bkgdHist.SetFillColor(bkgdCol)

        if i == 0:
            leg.AddEntry(sigHist, "Signal", "L")
            leg.AddEntry(bkgdHist, "Background", "F")

        stack = THStack(f"stack_m{mass}", f"Events Passing Selection m{mass};Bin;Events")
        stack.Add(bkgdHist)
        stack.Add(sigHist)

        canv.cd()
        canv.Clear()
        stack.Draw("NOSTACK HIST")
        if args.log:
            canv.SetLogy(True)
        leg.Draw()
        canv.Update()
        canv.SaveAs(f"../Plotting/Plots/EventPreds/nEventPred_m{mass}.png")

    canv.cd()
    canv.Clear()
    sigEvtArr = array("f", [sigEvtPerMass[m] for m in args.masses])
    bkgdEvtArr = array("f", [bkgdEvtPerMass[m] for m in args.masses])
    sigGraph = TGraph(len(sigEvtArr), massBins, sigEvtArr)
    bkgdGraph = TGraph(len(bkgdEvtArr), massBins, bkgdEvtArr)
    sigGraph.SetMarkerColor(sigCol)
    sigGraph.SetMarkerStyle(8)
    sigGraph.SetMarkerSize(2)
    bkgdGraph.SetMarkerColor(bkgdCol)
    bkgdGraph.SetMarkerStyle(8)
    bkgdGraph.SetMarkerSize(2)

    mg = TMultiGraph()
    mg.Add(sigGraph)
    mg.Add(bkgdGraph)
    mg.SetTitle("Events per Signal Mass in L-Band;Signal Mass [GeV];Events")
    mg.Draw("AP")
    if args.log:
        canv.SetLogy(True)
    leg.Clear()
    leg.AddEntry(sigGraph, "Expected Signal", "P")
    leg.AddEntry(bkgdGraph, "Expected Background", "P")
    leg.Draw()
    canv.Update()
    canv.SaveAs("../Plotting/Plots/EventPreds/nEventPred_allMasses.png")

    return [eventsPerProc[m] for m in args.masses]


#----------------------------------------------------------------------------------------------------------------------------------------------#

#Makes a event yields per process and signal mass table
#courtesy of ChatGPT
def printExpEvtsTable(masses, event_dicts, latex=False):
    processes = list(event_dicts[0].keys())
    
    total_bkgs = [sum(v for k, v in events.items() if k != "SIG") for events in event_dicts]
    
    # Sort background processes by yield at the first mass point (largest first)
    backgrounds = [p for p in processes if p != "SIG"]
    backgrounds.sort(key=lambda p: event_dicts[0][p], reverse=True)
    
    rows = [["Signal"] + [f"{events['SIG']:.2f}" for events in event_dicts]]
    
    if not latex:
        rows.append(["-" * 10] + ["-" * 10 for _ in masses])  

    for proc in backgrounds:
        rows.append([proc] + [f"{events[proc]:.2f}" for events in event_dicts])
    
    rows.append(["Total Background"] + [f"{tb:.2f}" for tb in total_bkgs])
    
    headers = ["Process"] + masses
    
    if latex:
        latex_table = tabulate(rows, headers=headers, tablefmt="latex_booktabs")
        latex_table = latex_table.replace("---------- & ---------- & ---------- & ---------- & ---------- \\\\", "\\midrule")
        print(latex_table)
    else:
        print(tabulate(rows, headers=headers, tablefmt="grid"))



#----------------------------------------------------------------------------------------------------------------------------------------------#


#Utility function to aid updating massToLEdges dict from massToLHalfWidths
def printLEdges():
    global massToLHalfWidths
    for m in massToLHalfWidths.keys():
        mass = float(m)
        halfWidth = massToLHalfWidths[m]*mass
        print('"'+m+'"' + " : [" + str(mass-halfWidth) + ", " + str(mass+halfWidth) + "],")

#----------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    args = parseArgs()
    if args.printLEdges:
        printLEdges
    else:
        evtsPerProc = makeEvtPredHists(args)
        printExpEvtsTable(args.masses, evtsPerProc, args.latex)
