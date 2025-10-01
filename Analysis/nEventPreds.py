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
from ROOT import TFile, TCanvas, TTree, TChain, TH1F, TGraph, TLegend, gStyle, THStack, TMultiGraph

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

def makeEvtPredHists(args):      
    
    canv = TCanvas("canv_binScheme", "N Events in 2D Collinear Mass Bins", 1200, 800)
    leg = TLegend(0.7, 0.7, 0.9, 0.9)
    gStyle.SetOptStat(0)
    sigCol = 603
    bkgdCol = 921

    baseCutStrs = []
    baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && ( (LOW_EDGE<=CHANNEL_minCollM && CHANNEL_minCollM <= HIGH_EDGE ) || (LOW_EDGE<= CHANNEL_maxCollM && CHANNEL_maxCollM <= HIGH_EDGE) ))")# * WEIGHT") #Bin 0 is L
    if args.nBins == 4:
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_maxCollM < LOW_EDGE) )") #Bin 1 is low corner in 4-bin scheme
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_minCollM > HIGH_EDGE) )") #Bin 2 is upper right triangle in 4-bin scheme
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && (CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE) )") #Bin 3 is upper left square in 4-bin scheme
    else:
        baseCutStrs.append("(CHANNEL_isCand && Z_dauDR<0.55 && Z_pt>300 && CHANNEL_CHANNELDR>1.5 && ZReClJ_nSJs<4 && ( (CHANNEL_maxCollM < LOW_EDGE) || (CHANNEL_minCollM > HIGH_EDGE) || ((CHANNEL_maxCollM > HIGH_EDGE) && (CHANNEL_minCollM < LOW_EDGE)) ) )")# * WEIGHT") #Any region outside L is background in 2 bin scheme

    massBins = array("f", [float(m) for m in args.masses])
    sigEvtPerMass = []
    bkgdEvtPerMass = []

    eventsPerProc = []
    
    for mN, mass in enumerate(args.masses):
        print("Processing mass =", mass)
        sigHist = TH1F("sig_m"+mass, "Events Passing Selection: m"+mass+" Binning;2D Collinear Mass Plane Bin Number; Events", args.nBins, -0.5, -0.5 + args.nBins)
        bkgdHist = TH1F("bkgds_m"+mass, "Events Passing Selection: m"+mass+" Binning;2D Collinear Mass Plane Bin Number; Events", args.nBins, -0.5, -0.5 + args.nBins)

        if args.asymm:
            lBinEdges = massToLEdges_asymm[mass]
        else:
            lBinEdges = massToLEdges[mass]

        sigEvtPerMass.append(0)
        bkgdEvtPerMass.append(0)
        
        eventsPerProc.append({"SIG":0,"ZZ":0, "WZ":0, "WW":0, "WJets":0, "DY":0, "TT":0, "ST":0, "QCD":0})
        
        for year in args.years:
            print("\t\tProcessing year =", year)
            #First do signal
            filePath = os.environ["ROOTURL"] + os.environ["SIG_"+year] + "taustarToTauZ_m" + mass + "_" + year + ".root"
            sigFile = TFile.Open(filePath, "r")
            sigTree = sigFile.Get("Events")

            for ch in args.channels:
                for bin in range(args.nBins):
                    cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                    cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                    cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))

                    weight = getWeight("M"+mass, year, xs=True)
                    nEvts = sigTree.GetEntries(cutStr)
                    
                    sigHist.Fill(sigHist.GetBinCenter(bin+1), nEvts*weight)
                    if bin == 0:
                        sigEvtPerMass[-1] += nEvts*weight
                        eventsPerProc[-1]["SIG"] += nEvts*weight

            sigFile.Close()

            #Now do backgrounds
            dirPath = os.environ["ROOTURL"] + os.environ["BKGD_" + year]
            for proc in processes:
                if year in ["2022", "2022post", "2023", "2023post"]:
                    if args.legacy:
                        subProcs = procToSubProc_run3_legacy[proc]
                    else:
                        subProcs = procToSubProc_run3[proc]
                else:
                    subProcs = procToSubProc_run2[proc]
                for subProc in subProcs:
                    bkgdFile = TFile.Open(dirPath + subProc + "_" + year + ".root", "r")
                    bkgdTree = bkgdFile.Get("Events")
                    
                    for ch in args.channels:
                        for bin in range(args.nBins):
                            cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                            cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                            cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))
                            
                            weight = getWeight(subProc, year, xs=True)
                            nEvts = bkgdTree.GetEntries(cutStr)
                            
                            bkgdHist.Fill(bkgdHist.GetBinCenter(bin+1), nEvts*weight)
                            if bin == 0:
                                bkgdEvtPerMass[-1] += nEvts*weight
                                eventsPerProc[-1][proc] += nEvts*weight
                    bkgdFile.Close()
        #END YEAR

        #Done retrieving data for this year, now plot and save histograms
        sigHist.SetLineWidth(3)
        sigHist.SetLineColor(sigCol)

        bkgdHist.SetLineColor(bkgdCol)
        bkgdHist.SetFillColor(bkgdCol)

        if mN == 0:
            leg.AddEntry(sigHist, "Signal", "L")
            leg.AddEntry(bkgdHist, "Background", "F")

        stack = THStack("stack","Events Passing Selection: m"+mass+" Binning;2D Collinear Mass Plane Bin Number; Events")
        stack.Add(bkgdHist)
        stack.Add(sigHist)
        
        canv.cd()
        canv.Clear()
        stack.Draw("NOSTACK HIST")
        if args.log:
            canv.SetLogy(True)
        leg.Draw()
        canv.Update()
        canv.SaveAs("../Plotting/Plots/EventPreds/nEventPred_m"+ mass + ".png")
    
        #END MASS
    
    #Now cumulative graphs (events in L per signal mass)
    canv.cd()
    canv.Clear()

    sigEvtPerMass = array("f", sigEvtPerMass)
    bkgdEvtPerMass = array("f", bkgdEvtPerMass)
    sigGraph = TGraph(len(sigEvtPerMass), massBins, sigEvtPerMass)
    bkgdGraph = TGraph(len(bkgdEvtPerMass), massBins, bkgdEvtPerMass)
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
    
    return eventsPerProc

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
