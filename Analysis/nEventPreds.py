#Make histograms of the number of signal and background in each bin (0=signal L-band)

###########################################################
#                      >          <                     + #                      
#                      >          <                   +   #                      
#                      >          <       2         +     #                      
#                      >          <               +       #                      
#          NOT         >          <             +         #                      
#       POSSIBLE       >          <           +           #                      
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

#----------------------------------------------------------------------------------------------------------------------------------------------#

import argparse
import os
import sys
from array import array
from ROOT import TFile, TCanvas, TTree, TChain, TH1F, TGraph, TLegend, gStyle, THStack, TMultiGraph

sys.path.append("../Framework/")
from datasets import processes, procToSubProc
from mcWeights import getWeight

#----------------------------------------------------------------------------------------------------------------------------------------------#

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
    argparser.add_argument("-y", "--years", nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to use")
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["ALL","SIG_DEF", "250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], default=["ALL"], help = "Which signal masses to use. Default is ALL")
    argparser.add_argument("-c", "--channels", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use. Default ALL " )
    argparser.add_argument("-b", "--nBins", type=int, choices=[2, 3], default=3, help="Specify 2 to use binning scheme of signal L-band + all rest of plane. 3 to use L-band + 2 bkgd regions" )
    argparser.add_argument("--printLEdges", action="store_true", help="If specified, will printe the L-bin edges corresponding to the L half-widths")

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
    baseCutStrs.append("(CHANNEL_isCand && ( (LOW_EDGE<=CHANNEL_minCollM && CHANNEL_minCollM <= HIGH_EDGE ) || (LOW_EDGE<= CHANNEL_maxCollM && CHANNEL_maxCollM <= HIGH_EDGE) ))")# * WEIGHT") #Bin 0 is L
    if args.nBins == 3:
        baseCutStrs.append("(CHANNEL_isCand && (CHANNEL_minCollM < LOW_EDGE) )")# * WEIGHT") #Bin 1 is low corner in 3-bin scheme
        baseCutStrs.append("(CHANNEL_isCand && (CHANNEL_maxCollM > HIGH_EDGE) )")# * WEIGHT") #Bin 2 is upper corner in 2-bin scheme
    else:
        baseCutStrs.append("(CHANNEL_isCand && ( (CHANNEL_minCollM < LOW_EDGE) || (CHANNEL_maxCollM > HIGH_EDGE) ) )")# * WEIGHT") #Any region outside L is background in 2 bin scheme

    massBins = array("f", [float(m) for m in args.masses])
    sigEvtPerMass = []
    bkgdEvtPerMass = []

    for mN, mass in enumerate(args.masses):
        print("Processing mass =", mass)
        sigHist = TH1F("sig_m"+mass, "Events Passing Selection: m"+mass+" Binning;2D Collinear Mass Plane Bin Number; Events", args.nBins, -0.5, -0.5 + args.nBins)
        bkgdHist = TH1F("bkgds_m"+mass, "Events Passing Selection: m"+mass+" Binning;2D Collinear Mass Plane Bin Number; Events", args.nBins, -0.5, -0.5 + args.nBins)

        lBinEdges = massToLEdges[mass]

        sigEvtPerMass.append(0)
        bkgdEvtPerMass.append(0)
        
        for year in args.years:
            print("\t\tProcessing year =", year)
            #First do signal
            if year in ["2022", "2022post", "2023", "2023post"]:
                filePath = os.environ["ROOTURL"] + os.environ["SIG_R3"] + "taustarToTauZ_m" + mass + "_" + year + ".root"
            else:
                filePath = os.environ["ROOTURL"] + os.environ["SIG_R2"] + "taustarToTauZ_m" + mass + "_" + year + ".root"
            sigFile = TFile.Open(filePath, "r")
            sigTree = sigFile.Get("Events")

            for ch in args.channels:
                for bin in range(args.nBins):
                    cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                    cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                    cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))
                    #cutStr = cutStr.replace("WEIGHT", str(getWeight("M"+mass, year, xs=True)))
                    weight = getWeight("M"+mass, year, xs=True)
                    
                    nEvts = sigTree.GetEntries(cutStr)
                    #sigHist.SetBinContent(bin+1, sigHist.GetBinContent(bin+1) + nEvts, weight )
                    sigHist.Fill(sigHist.GetBinCenter(bin+1), nEvts*weight)
                    if bin == 0:
                        sigEvtPerMass[-1] += nEvts*weight

            sigFile.Close()

            #Now do backgrounds
            dirPath = os.environ["ROOTURL"] + os.environ["BKGD_" + year]
            for proc in processes:
                for subProc in procToSubProc[proc]:
                    bkgdFile = TFile.Open(dirPath + subProc + "_" + year + ".root", "r")
                    bkgdTree = bkgdFile.Get("Events")
                    
                    for ch in args.channels:
                        for bin in range(args.nBins):
                            cutStr = baseCutStrs[bin].replace("CHANNEL", ch)
                            cutStr = cutStr.replace("LOW_EDGE", str(lBinEdges[0]))
                            cutStr = cutStr.replace("HIGH_EDGE", str(lBinEdges[1]))
                            #cutStr = cutStr.replace("WEIGHT", str(getWeight(subProc, year, xs=True)))
                            weight = getWeight(subProc, year, xs=True)
                            nEvts = bkgdTree.GetEntries(cutStr)
                            #bkgdHist.SetBinContent(bin+1, bkgdHist.GetBinContent(bin+1) + nEvts, weight)
                            bkgdHist.Fill(bkgdHist.GetBinCenter(bin+1), nEvts*weight)
                            if bin == 0:
                                bkgdEvtPerMass[-1] += nEvts*weight
                                
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
    
    
    leg.Clear()
    leg.AddEntry(sigGraph, "Expected Signal", "P")
    leg.AddEntry(bkgdGraph, "Expected Background", "P")
    leg.Draw()
    canv.Update()
    wait = input("Hit ENTER to save and close plot")
    canv.SaveAs("../Plotting/Plots/EventPreds/nEventPred_allMasses.png")

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
        makeEvtPredHists(args)
