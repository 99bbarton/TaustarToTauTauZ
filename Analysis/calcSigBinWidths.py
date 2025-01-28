#Calculates the fraction of events contained within an L-band in the 2D collinear mass plane for a range of fractional bin half widths
#Currently only implemented for signal but can be adapted for background easily in the future

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TFile, TLegend, gStyle, TMultiGraph, TGraph, TGraphErrors
import sys
import os
import argparse
import numpy as np

sys.path.append("../Framework/")
from Colors import getColor, getPalettes

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Calculate the width of the L-bin in the 2D collinear mass plane needed to contain a given frac of signal")
    argparser.add_argument("-i", "--inDir", required=True, help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to use")
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["ALL","SIG_DEF", "250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], default=["ALL"], help = "Which signal masses to use. Default is ALL")
    argparser.add_argument("-c", "--channel", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use" )
    argparser.add_argument("-f", "--sigFrac", type=float, help="The target fraction of signal in each bin")
    argparser.add_argument("--minMax", nargs="2", type=float, default=[2, 100], help="The min and max fractional bin width to consider")
    argparser.add_argument("--cuts", type=str, help="Cuts to apply. Overrides default cuts" )
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots and writing calculated values")
    argparser.add_argument("--save", action="append", choices = [".pdf", ".png", ".C", "ALL"], default=[], help="What file types to save plots as. Default not saved.")
    
    args = argparser.parse_args()  

    if args.inDir.startswith("/store"):
        args.inDir = os.environ["ROOTURL"] + args.inDir
    if args.inDir[-1] != "/":
        args.inDir += "/"

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

    if "ALL" in args.channel:
        args.channel = ["ETau", "MuTau", "TauTau"]

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):
    binCntrs, binCounts, targHalfWidths = calcBinWidths(args)
    plotFracContained(args, binCntrs, binCounts)
    if args.sigFrac:
        plotSigLBandWidths(args, targHalfWidths)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#Calculate the fraction of signal events contained within the L-band for a range of bin widths 
def calcBinWidths(args):
    
    binCntrs = np.linspace(args.minMax[0], args.minMax[1])
    binCounts = np.zeros((len(args.masses), len(binCntrs)) )

    if args.cuts:
        cuts = args.cuts
    else:
        cuts = "Gen_isCand && Z_isCand && CHANNEL_isCand"
    
    if args.sigFrac:
        targHalfWidths = np.zeros(len(args.masses))

    for mN, mass in enumerate(args.masses):
        massFlt = float(mass)
        foundFrac = False

        for year in args.years:
            filename = args.inDir + "taustarToTauZ_m" + mass + "_" + year + ".root"
            inFile = TFile.Open(filename, "r")
            tree = inFile.Get("Events")

            for fN, frac in enumerate(binCntrs):
                halfWidth = frac * massFlt / 2.0
                reqStr = "((" + str(massFlt - halfWidth) + "<= CHANNEL_minColM && CHANNEL_minColM <= " +  str(massFlt + halfWidth) + " ) || "
                reqStr += "(" + str(massFlt - halfWidth) + "<= CHANNEL_maxColM && CHANNEL_maxColM <= " +  str(massFlt + halfWidth) + " ))"

                numEvts = 0
                denomEvts = 0
                for ch in args.channels:
                    cuts.replace("CHANNEL", ch)
                    reqStr.replace("CHANNEL", ch)

                    numEvts += tree.GetEntries(reqStr + " && (" + cuts +")")
                    denomEvts += tree.GetEntries(cuts)
                    
                    binCounts[mN][fN] = numEvts / denomEvts

                    if args.sigFrac and not foundFrac:
                        if (numEvts / denomEvts) >= args.sigFrac:
                            print("For taustar mass " + mass + " bin halfWidth containing " + str(args.sigFrac*100) + "\% of signal is " + str(halfWidth))
                            targHalfWidths[mN] = halfWidth 

    if args.sigFrac:
        print("\n" + str(targHalfWidths) + "\n")

    return binCntrs, binCounts, targHalfWidths

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotFracContained(args, binCntrs, binCounts):
    
    canv = TCanvas("canv", "Fraction of Events in Signal L-Band", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)
    leg = TLegend(0.7, 0.3, 0.9, 0.7, "Signal Mass")

    nBins = len(binCntrs)
    multiG = TMultiGraph()
    for mN, mass in enumerate(args.masses):
        graph = TGraph(nBins, binCntrs, binCounts[mN])
        graph.SetTitle(";Frac of Events in L-Band;Frac L-Band Width")
        graph.SetLineColor(getColor(args.palette, mN))
        graph.SetMarkerColor(getColor(args.palette, mN))
        graph.SetMarkerStyle(5)
        graph.SetMarkerSize(2)

        multiG.Add(graph)
        leg.add(graph, getColor(args.palette, mN))

    canv.cd()
    multiG.Draw("ALP")
    leg.Draw()
    canv.Update()

    if not args.nP:
        wait = input("Hit ENTER to close plot and save (if specified)")

    if args.save:
        for fileType in args.save:
            canv.SaveAs("../Plots/fracEvtsInLBand" + fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotSigLBandWidths(args, targHalfWidths):
    canv = TCanvas("canv", "Fraction of Events in Signal L-Band", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)

    nMasses = len(args.masses)
    masses = np.zeros()
    for mN, massStr in enumerate(args.masses):
        masses[mN] = float(massStr)
    
    fracWidths = targHalfWidths * 2
    widths = np.multiply(masses, fracWidths)
    xWidths = np.zeros(nMasses)

    graph = TGraphErrors(nMasses, masses, masses, xWidths)
    graph.SetTitle("Signal L-Band Widths;#tau* Hypothesis Mass [GeV];Signal Bin Mass Coverage [GeV]")
    graph.SetMarkerStyle(5)
    graph.SetMarkerSize(2)

    canv.cd()
    graph.Draw("AP")
    canv.Update()

    if not args.nP:
        wait = input("Hit ENTER to close plot and save (if specified)")

    if args.save:
        for fileType in args.save:
            canv.SaveAs("../Plots/sigLBandWidths"+ fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##