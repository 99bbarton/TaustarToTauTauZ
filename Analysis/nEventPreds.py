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
from math import sqrt

from ROOT import TFile, TCanvas, TTree, TChain, TH1F, TGraph, TLegend, gStyle, THStack, TMultiGraph, TGraphErrors

sys.path.append("../Framework/")
from datasets import procToSubProc_run2, procToSubProc_run3, procToSubProc_run3_legacy
from datasets import processes as allProcs
from mcWeights import getWeight

#----------------------------------------------------------------------------------------------------------------------------------------------#

#These are the symmetric L-band edges, i.e. mass +/- (halfWidth*mass)
massToLEdges_asymm = {
    "250" : [175.0, 325.0],
    "500" : [350.0, 650.0],
    "750" : [525.0, 975.0],
    "1000" : [700.0, 1300.0],
    "1250" : [1000.0, 1600.0], #TODO optimize this
    "1500" : [1300.0, 2250.0],
    "1750" : [1500.0, 2500.0], #TODO optimize this
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
    "1250" : [875.0, 1625.0],
    "1500" : [750.0, 2250.0],
    "1750" : [875.0, 2625.0],
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
    "1250" : 0.3,
    "1500" : 0.5,
    "1750" : 0.5,
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
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["ALL","SIG_DEF", "SIG_MID", "250","500","750","1000","1250","1500","1750","2000","2500","3000","3500","4000","4500","5000"], default=["ALL"], help = "Which signal masses to use. Default is ALL")
    argparser.add_argument("-p", "--processes", nargs="+", choices=allProcs.extend("ALL"), default="ALL", help="Which bkgd processes to include.")
    argparser.add_argument("-c", "--channels", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use. Default ALL " )
    argparser.add_argument("-b", "--nBins", type=int, choices=[2, 4], default=4, help="Specify 2 to use binning scheme of signal L-band + all rest of plane. 4 to use L-band + 3 bkgd regions" )
    argparser.add_argument("-a", "--asymm", action="store_true", help="If specified, will use assymetric L-bands. Otherwise, symmetric band edges are used.")
    argparser.add_argument("-l", "--log", action="store_true", help="Specify to set the y-axis of plots to log scale.")
    argparser.add_argument("--CR", action="store_true", help="If specified, will perform estim for the same-sign tau control region instead of the signal region")
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
        args.masses = ["250","500","750","1000","1250","1500","1750","2000","2500","3000","3500","4000","4500","5000"]
    elif "SIG_DEF" in args.masses:
        args.masses = ["250", "1000", "3000", "5000"]
    elif "SIG_MID" in args.masses:
        args.masses = ["1000", "1250", "1500", "1750", "2000"]

    if "ALL" in args.processes:
        args.processes = allProcs

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
    baseCutStrs.append("(CHANNEL_isCand && MET_pt > 200 && Z_dauDR<0.55 && Z_pt>300 && ObjCnt_nBTags<2 && ObjCnt_nMuMatch && CHANNEL_CHANNELDR>1.5 && ( (LOW_EDGE<=CHANNEL_minCollM && CHANNEL_minCollM <= HIGH_EDGE ) || (LOW_EDGE<= CHANNEL_maxCollM && CHANNEL_maxCollM <= HIGH_EDGE) ))") #Bin 0, i.e. signal L-band
    #baseCutStrs.append("(CHANNEL_isCand && ( (LOW_EDGE<=CHANNEL_minCollM && CHANNEL_minCollM <= HIGH_EDGE ) || (LOW_EDGE<= CHANNEL_maxCollM && CHANNEL_maxCollM <= HIGH_EDGE) ))") #Bin 0, i.e. signal L-band
    if args.nBins == 4:
        baseCutStrs.append("(CHANNEL_isCand && MET_pt > 200 && Z_dauDR<0.55 && Z_pt>300 && ObjCnt_nBTags<2 && ObjCnt_nMuMatch && CHANNEL_CHANNELDR>1.5 && (CHANNEL_maxCollM < LOW_EDGE) )") #Bin 1
        #baseCutStrs.append("(CHANNEL_isCand && (CHANNEL_maxCollM < LOW_EDGE) )") #Bin 1
        baseCutStrs.append("(CHANNEL_isCand && MET_pt > 200 && Z_dauDR<0.55 && Z_pt>300 && ObjCnt_nBTags<2 && ObjCnt_nMuMatch && CHANNEL_CHANNELDR>1.5 && (CHANNEL_minCollM > HIGH_EDGE) )") #Bin 2
        #baseCutStrs.append("(CHANNEL_isCand && (CHANNEL_minCollM > HIGH_EDGE) )") #Bin 2
        baseCutStrs.append("(CHANNEL_isCand && MET_pt > 200 && Z_dauDR<0.55&&Z_pt>300&& ObjCnt_nBTags<2 && ObjCnt_nMuMatch&&CHANNEL_CHANNELDR>1.5 && (CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE) )") #Bin 3
        #baseCutStrs.append("(CHANNEL_isCand && (CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE) )") #Bin 3
    else:
        baseCutStrs.append("(CHANNEL_isCand && MET_pt > 200 && Z_dauDR<0.55 && Z_pt>300 && ObjCnt_nBTags<2 && ObjCnt_nMuMatch && CHANNEL_CHANNELDR>1.5 && ( (CHANNEL_maxCollM < LOW_EDGE) || (CHANNEL_minCollM > HIGH_EDGE) || ((CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE)) ) )") #Bin 1 (2-bin scheme)
        #baseCutStrs.append("(CHANNEL_isCand && ( (CHANNEL_maxCollM < LOW_EDGE) || (CHANNEL_minCollM > HIGH_EDGE) || ((CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE)) ) )") #Bin 1 (2-bin scheme)
        
    # prepare histograms for each mass
    massBins = array("f", [float(m) for m in args.masses])
    sigHists = {}
    bkgdHists = {}
    sigEvtPerMass = {m: 0 for m in args.masses}
    sigEvtErrPerMass = {m: 0 for m in args.masses}
    bkgdEvtPerMass = {m: 0 for m in args.masses}
    bkgdEvtErrPerMass = {m: 0 for m in args.masses}
    eventsPerProc = {m: {"SIG": 0, "ZZ": 0, "WZ": 0, "WW": 0, "WJets": 0, "DY": 0, "TT": 0, "ST": 0, "QCD": 0} for m in args.masses}
    eventsErrPerProc = {m: {"SIG": 0, "ZZ": 0, "WZ": 0, "WW": 0, "WJets": 0, "DY": 0, "TT": 0, "ST": 0, "QCD": 0} for m in args.masses}

    for mass in args.masses:
        sigHists[mass] = TH1F(f"sig_m{mass}", f"Signal m{mass};Bin;Events", args.nBins, -0.5, -0.5 + args.nBins)
        sigHists[mass].Sumw2()
        bkgdHists[mass] = TH1F(f"bkgd_m{mass}", f"Background m{mass};Bin;Events", args.nBins, -0.5, -0.5 + args.nBins)
        bkgdHists[mass].Sumw2()

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
                    if args.CR:
                        if ch == "ETau":
                            cutStr = "("+cutStr+ "&& ( (Electron_charge[ETau_eIdx]*Tau_charge[ETau_tauIdx]) > 0) )"
                        elif ch == "MuTau":
                            cutStr = "("+cutStr+ "&& ( (Muon_charge[MuTau_muIdx]*Tau_charge[MuTau_tauIdx]) > 0) )"
                        else:
                            cutStr = "("+cutStr+ "&& ( (Tau_charge[TauTau_tau1Idx]*Tau_charge[TauTau_tau2Idx]) > 0) )"
                    else:
                        if ch == "ETau":
                            cutStr = "("+cutStr+ "&& ( (Electron_charge[ETau_eIdx]*Tau_charge[ETau_tauIdx]) < 0) )"
                        elif ch == "MuTau":
                            cutStr = "("+cutStr+ "&& ( (Muon_charge[MuTau_muIdx]*Tau_charge[MuTau_tauIdx]) < 0) )"
                        else:
                            cutStr = "("+cutStr+ "&& ( (Tau_charge[TauTau_tau1Idx]*Tau_charge[TauTau_tau2Idx]) < 0) )"
                    weight = getWeight("M" + mass, year, xs=True)
                    nEvts = sigTree.GetEntries(cutStr)

                    sigHists[mass].Fill(sigHists[mass].GetBinCenter(bin + 1), nEvts * weight)
                    if bin == 0:
                        sigEvtPerMass[mass] += nEvts * weight
                        eventsPerProc[mass]["SIG"] += nEvts * weight
            sigFile.Close()
            sigEvtErrPerMass[mass] = sqrt(sigEvtPerMass[mass])
            eventsErrPerProc[mass]["SIG"] = sqrt(eventsPerProc[mass]["SIG"])

        dirPath = os.environ["ROOTURL"] + os.environ["BKGD_" + year]
        for proc in args.processes:
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
                            if args.CR:
                                if ch == "ETau":
                                    cutStr = "("+cutStr+ "&& ( (Electron_charge[ETau_eIdx]*Tau_charge[ETau_tauIdx]) > 0) )"
                                elif ch == "MuTau":
                                    cutStr = "("+cutStr+ "&& ( (Muon_charge[MuTau_muIdx]*Tau_charge[MuTau_tauIdx]) > 0) )"
                                else:
                                    cutStr = "("+cutStr+ "&& ( (Tau_charge[TauTau_tau1Idx]*Tau_charge[TauTau_tau2Idx]) > 0) )"
                            else:
                                if ch == "ETau":
                                    cutStr = "("+cutStr+ "&& ( (Electron_charge[ETau_eIdx]*Tau_charge[ETau_tauIdx]) < 0) )"
                                elif ch == "MuTau":
                                    cutStr = "("+cutStr+ "&& ( (Muon_charge[MuTau_muIdx]*Tau_charge[MuTau_tauIdx]) < 0) )"
                                else:
                                    cutStr = "("+cutStr+ "&& ( (Tau_charge[TauTau_tau1Idx]*Tau_charge[TauTau_tau2Idx]) < 0) )"

                            weight = getWeight(subProc, year, xs=True)
                            nEvts = bkgdTree.GetEntries(cutStr)

                            bkgdHists[mass].Fill(bkgdHists[mass].GetBinCenter(bin + 1), nEvts * weight)
                            if bin == 0:
                                bkgdEvtPerMass[mass] += nEvts * weight
                                eventsPerProc[mass][proc] += nEvts * weight

                bkgdFile.Close()
                #End MASS
            #eventsErrPerProc[mass][proc] = sqrt( eventsPerProc[mass][proc])
            #print(f"Error for mass={mass}, proc={proc} = {eventsErrPerProc[mass][proc]}")
            
        #bkgdEvtErrPerMass[mass] = sqrt(bkgdEvtPerMass[mass])
        

    for i, mass in enumerate(args.masses):
        bkgdEvtErrPerMass[mass] = sqrt(bkgdEvtPerMass[mass])
        for p in args.processes:
            eventsErrPerProc[mass][proc] = sqrt(eventsPerProc[mass][proc])
        
        sigHist = sigHists[mass]
        #sigHist.Sumw2()
        bkgdHist = bkgdHists[mass]
        #bkgdHist.Sumw2()
        sigHist.SetLineWidth(3)
        sigHist.SetLineColor(sigCol)
        bkgdHist.SetLineColor(bkgdCol)
        bkgdHist.SetLineWidth(3)
        #bkgdHist.SetFillColor(bkgdCol)

        if i == 0:
            leg.AddEntry(sigHist, "Signal", "L")
            leg.AddEntry(bkgdHist, "Background", "L")

        if args.CR:
            stack = THStack(f"stack_m{mass}", f"Events Passing Selection m{mass} in CR;Bin;Events")
        else:
            stack = THStack(f"stack_m{mass}", f"Events Passing Selection m{mass};Bin;Events")
        stack.Add(bkgdHist)
        stack.Add(sigHist)

        canv.cd()
        canv.Clear()
        #if sigHist.GetMaximum() > bkgdHist.GetMaximum():
        #    sigHist.Draw("HIST E1")
        #    bkgdHist.Draw("HIST E1 SAME")
        #else:
        #    bkgdHist.Draw("HIST E1")
        #    sigHist.Draw("HIST E1 SAME")

        stack.Draw("NOSTACK HIST E1")
        if args.log:
            canv.SetLogy(True)
        leg.Draw()
        canv.Update()
        if args.CR:
            canv.SaveAs(f"../Plotting/Plots/EventPreds/nEventPred_m{mass}_CR.png")
        else:
            canv.SaveAs(f"../Plotting/Plots/EventPreds/nEventPred_m{mass}.png")

    canv.cd()
    canv.Clear()
    sigEvtArr = array("f", [sigEvtPerMass[m] for m in args.masses])
    sigEvtErrArr = array("f", [sigEvtErrPerMass[m] for m in args.masses] )
    bkgdEvtArr = array("f", [bkgdEvtPerMass[m] for m in args.masses])
    bkgdEvtErrArr = array("f", [bkgdEvtErrPerMass[m] for m in args.masses])
    xErrs = array("f", [0 for m in args.masses])
    sigGraph = TGraphErrors(len(sigEvtArr), massBins, sigEvtArr, xErrs, sigEvtErrArr)
    bkgdGraph = TGraphErrors(len(bkgdEvtArr), massBins, bkgdEvtArr, xErrs, bkgdEvtErrArr)
    sigGraph.SetMarkerColor(sigCol)
    sigGraph.SetMarkerStyle(8)
    sigGraph.SetMarkerSize(2)
    sigGraph.SetLineColor(sigCol)
    bkgdGraph.SetMarkerColor(bkgdCol)
    bkgdGraph.SetMarkerStyle(8)
    bkgdGraph.SetMarkerSize(2)
    bkgdGraph.SetLineColor(bkgdCol)

    mg = TMultiGraph()
    mg.Add(sigGraph)
    mg.Add(bkgdGraph)
    if args.CR:
        mg.SetTitle("Events per Signal Mass in Control Region L-Band;Signal Mass [GeV];Events")
    else:
        mg.SetTitle("Events per Signal Mass in L-Band;Signal Mass [GeV];Events")
    mg.Draw("AP")
    if args.log:
        canv.SetLogy(True)
    leg.Clear()
    leg.AddEntry(sigGraph, "Expected Signal", "P")
    leg.AddEntry(bkgdGraph, "Expected Background", "P")
    leg.Draw()
    canv.Update()
    if args.CR:
        canv.SaveAs("../Plotting/Plots/EventPreds/nEventPred_allMasses_CR.png")
    else:
        canv.SaveAs("../Plotting/Plots/EventPreds/nEventPred_allMasses.png")

    return [eventsPerProc[m] for m in args.masses], [eventsErrPerProc[m] for m in args.masses]


#----------------------------------------------------------------------------------------------------------------------------------------------#

#Makes a event yields per process and signal mass table
#courtesy of ChatGPT
def printExpEvtsTable(masses, event_dicts, event_err_dicts, latex=False):
    processes = list(event_dicts[0].keys())
    
    total_bkgs = [sum(v for k, v in events.items() if k != "SIG") for events in event_dicts]
    total_bkgs_errs = [sqrt(totBkgd) for totBkgd in total_bkgs]
    
    # Sort background processes by yield at the first mass point (largest first)
    backgrounds = [p for p in processes if p != "SIG"]
    backgrounds.sort(key=lambda p: event_dicts[0][p], reverse=True)
    
    rows = [["Signal"] + [f"{events['SIG']:.3f}+/-{sqrt(events['SIG']):.3f}" for events in event_dicts]]
    
    if not latex:
        rows.append(["-" * 10] + ["-" * 10 for _ in masses])  

    for proc in backgrounds:
        rows.append([proc] + [f"{events[proc]:.3f}+/-{errors[proc]:.3f}" for events, errors in zip(event_dicts, event_err_dicts)])
    
    rows.append(["Total Background"] + [f"{tb:.3f}+/-{tbErr:.3f}" for tb, tbErr in zip(total_bkgs, total_bkgs_errs)])
    
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
        evtsPerProc, evtsErrPerProc = makeEvtPredHists(args)
        printExpEvtsTable(args.masses, evtsPerProc, evtsErrPerProc, args.latex)
