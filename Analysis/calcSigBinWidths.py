#Calculates the fraction of events contained within an L-band in the 2D collinear mass plane for a range of fractional bin half widths
#Currently only implemented for signal but can be adapted for background easily in the future

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TFile, TLegend, gStyle, TMultiGraph, TGraph, TGraphErrors
import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("../Framework/")
from Colors import getColor, getPalettes, getPalette
from mcWeights import getWeight
from datasets import procToSubProc

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Calculate the width of the L-bin in the 2D collinear mass plane needed to contain a given frac of signal")
    argparser.add_argument("-i", "--inDir", required=True, help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to use")
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["ALL","SIG_DEF", "250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], default=["ALL"], help = "Which signal masses to use. Default is ALL")
    argparser.add_argument("-c", "--channel", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use. Default ALL " )
    argparser.add_argument("-f", "--sigFrac", type=float, help="The target fraction of signal in each bin")
    argparser.add_argument("--minMax", nargs=2, type=float, default=[0.02, 1.0], help="The min and max fractional bin width to consider")
    argparser.add_argument("--cuts", type=str, help="Cuts to apply. Overrides default cuts" )
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots and writing calculated values")
    argparser.add_argument("--save", action="append", choices = [".pdf", ".png", ".C"], default=[], help="What file types to save plots as. Default not saved.")

    #Below args are for sig / bkgd ratio plots
    argparser.add_argument("-b", "--backgrounds", nargs = "+", choices=["ALL", "ALLnoQCD", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"], help="Which background procsses to consider")
    argparser.add_argument("--bkgdDir", type=str, help="The directory to find the background samples")
    argparser.add_argument("--denFunc", choices=["B","S+B","SQRT(B)","SQRT(S+B)", "1"], default="S+B", help="Sets the denominator function to divide signal by in 2D scan of bin widths")
    argparser.add_argument("--stepSize", default=0.1, type=float, help="Granularity of fractional L-band half widths to scan")
    
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

    if "ALL" in args.backgrounds:
        args.backgrounds = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
    elif "ALLnoQCD" in args.backgrounds:
        args.backgrounds = ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST"]

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):
    if args.backgrounds:
        plotSigVsBkgdInL(args)
    else:
        binCntrs, binCounts, targHalfWidths = calcBinWidths(args)
        plotFracContained(args, binCntrs, binCounts)
        if args.sigFrac:
            plotSigLBandWidths(args, targHalfWidths)
    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#Calculate the fraction of signal events contained within the L-band for a range of bin widths 
def calcBinWidths(args):
    
    binCntrs = np.linspace(args.minMax[0], args.minMax[1], int((args.minMax[1] - args.minMax[0])*100))
    binCounts = np.zeros((len(args.masses), len(binCntrs)) )

    if args.cuts:
        cuts = args.cuts
    else:
        cuts = "Gen_isCand && Z_isCand && CHANNEL_isCand"
    
    targHalfWidths = np.zeros(len(args.masses))

    for mN, mass in enumerate(args.masses):
        massFlt = float(mass)
        foundFrac = False

        print("Processing m = "+ mass)

        for year in args.years:
            filename = args.inDir + "taustarToTauZ_m" + mass + "_" + year + ".root"
            inFile = TFile.Open(filename, "r")
            tree = inFile.Get("Events")

            for fN, frac in enumerate(binCntrs):
                halfWidth = frac * massFlt / 2.0
                reqStr = "((" + str(massFlt - halfWidth) + "<= CHANNEL_minCollM && CHANNEL_minCollM <= " +  str(massFlt + halfWidth) + " ) || "
                reqStr += "(" + str(massFlt - halfWidth) + "<= CHANNEL_maxCollM && CHANNEL_maxCollM <= " +  str(massFlt + halfWidth) + " ))"

                numEvts = 0
                denomEvts = 0
                for ch in args.channel:
                    cuts = cuts.replace("CHANNEL", ch)
                    reqStr = reqStr.replace("CHANNEL", ch)

                    numEvts += tree.GetEntries(reqStr + " && (" + cuts +")")
                    denomEvts += tree.GetEntries(cuts)
                    
                    binCounts[mN][fN] = numEvts / denomEvts

                    if args.sigFrac and not foundFrac:
                        if (numEvts / denomEvts) >= args.sigFrac:
                            mAdj  = mass
                            if len(mAdj) == 3:
                                mAdj = " " + mAdj
                            print("For taustar mass " + mAdj + " bin halfWidth containing " + str(args.sigFrac*100) + "% of signal is " + str(halfWidth.round(2)) + " GeV or " + str(frac.round(3)*100) + "%")
                            targHalfWidths[mN] = frac
                            foundFrac = True

    if args.sigFrac:
        print("\n" + str(targHalfWidths.tolist()) + "\n")

    return binCntrs, binCounts, targHalfWidths

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotFracContained(args, binCntrs, binCounts):
    
    canv = TCanvas("canv", "Fraction of Events in Signal L-Band", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)
    leg = TLegend(0.7, 0.3, 0.9, 0.7, "Signal Mass")
    palLen = len(getPalette(args.palette))
    
    nBins = len(binCntrs)
    multiG = TMultiGraph()
    multiG.SetTitle("L-Band Widths for Signal;Fractional L-Band Width;Fraction of Events in L-Band")
    for mN, mass in enumerate(args.masses):
        graph = TGraph(nBins, binCntrs, binCounts[mN])
        graph.SetTitle("L-Band Widths for Signal;Fractional L-Band Width;Fraction of Events in L-Band")
        if mN >= palLen:
            colN = mN - palLen
            graph.SetLineStyle(10)
        else:
            colN = mN
        graph.SetLineColor(getColor(args.palette, colN))
        graph.SetFillColor(getColor(args.palette, colN))
        graph.SetLineWidth(3)
            
        graph.SetMarkerColor(getColor(args.palette, colN))
        graph.SetMarkerStyle(5)
        graph.SetMarkerSize(2)

        multiG.Add(graph)
        leg.AddEntry(graph, mass, "L")

    canv.cd()
    multiG.Draw("AL")
    leg.Draw()
    canv.Update()

    if not args.nP:
        wait = input("Hit ENTER to close plot and save (if specified)")

    if args.save:
        for fileType in args.save:
            canv.SaveAs("../Plotting/Plots/fracEvtsInLBand" + fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotSigLBandWidths(args, targHalfWidths):
    canv = TCanvas("canv2", "Fraction of Events in Signal L-Band", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)

    nMasses = len(args.masses)
    masses = np.zeros(nMasses)
    for mN, massStr in enumerate(args.masses):
        masses[mN] = float(massStr)
    
    fracWidths = targHalfWidths * 2
    widths = np.multiply(masses, fracWidths)
    xWidths = np.zeros(nMasses)

    graph = TGraphErrors(nMasses, masses, masses, xWidths, widths)
    graph.SetTitle("Signal L-Band Widths: " + str(args.sigFrac*100) + "% Contained;#tau* Hypothesis Mass [GeV];Signal Bin Mass Coverage [GeV]")
    graph.SetMarkerStyle(5)
    graph.SetMarkerSize(2)

    canv.cd()
    graph.Draw("AP")
    canv.Update()

    if not args.nP:
        wait = input("Hit ENTER to close plot and save (if specified)")

    if args.save:
        for fileType in args.save:
            canv.SaveAs("../Plotting/Plots/sigLBandWidths"+ fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotSigVsBkgdInL(args):
    np.set_printoptions(suppress=True)

    nSigInBand = np.zeros((len(args.masses), int(1.0 / args.stepSize)), dtype=np.float64)
    nBkgdInBand = np.zeros((len(args.masses), int(1.0 / args.stepSize)), dtype=np.float64)
    intMasses = []
    halfFracs = []
    for fN in range(1, int(1.0 / args.stepSize) + 1):
        frac = fN * args.stepSize
        halfFracs.append(frac)

    print("Processing signal...")
    for year in args.years:
        print(" year :", year)
        for massN, mass in enumerate(args.masses):
            binCent = float(mass)
            intMasses.append(int(mass))

            sigFile = TFile.Open(args.inDir + "taustarToTauZ_m" + mass + "_" + year + ".root", "r")
            tree =  sigFile.Get("Events")

            mcWeight = float(getWeight("M" + mass, year, xs=False))
            
            for ch in args.channel:
                for fN, frac in enumerate(halfFracs):
                    halfWidth = binCent * frac
                    reqStr = "(("+ch+"_isCand)&&"
                    reqStr += "((" + str(binCent - halfWidth) + "<= "+ch+"_minCollM && "+ch+"_minCollM <= " +  str(binCent + halfWidth) + " ) || "
                    reqStr += "(" + str(binCent - halfWidth) + "<= "+ch+"_maxCollM && "+ch+"_maxCollM <= " +  str(binCent + halfWidth) + " )))"
                    nSigInBand[massN][fN] += tree.GetEntries(reqStr) * mcWeight
            
            sigFile.Close()

    print("Processing backgrounds...")
    for bkgd in args.backgrounds:
        print("\tProcess :", bkgd)
        for subProc in procToSubProc[bkgd]:
            for year in args.years:
                bkgdFile = TFile.Open("root://cmsxrootd.fnal.gov//store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/"+year+"/"+args.bkgdDir+"/"+subProc+"_"+year+".root")
                tree = bkgdFile.Get("Events")

                mcWeight = float(getWeight(subProc, year, xs=True))

                for massN, mass in enumerate(args.masses):
                    binCent = float(mass)
                    for ch in args.channel:
                        for fN, frac in enumerate(halfFracs):
                            halfWidth = binCent * frac
                            reqStr = "(("+ch+"_isCand)&&"
                            reqStr += "((" + str(binCent - halfWidth) + "<= "+ch+"_minCollM && "+ch+"_minCollM <= " +  str(binCent + halfWidth) + " ) || "
                            reqStr += "(" + str(binCent - halfWidth) + "<= "+ch+"_maxCollM && "+ch+"_maxCollM <= " +  str(binCent + halfWidth) + " )))"
                            nBkgdInBand[massN][fN] += tree.GetEntries(reqStr) * mcWeight

                bkgdFile.Close()
    
    print("\nDone retrieving data")
    
    ratio = np.full_like(nSigInBand, 0, dtype=np.float64)
    
    if args.denFunc == "S+B":
        denom = nSigInBand + nBkgdInBand
        thresh = denom > 1e-4
        ratio[thresh] = nSigInBand[thresh] / denom[thresh]
        title = "S/(S+B) per Sig. Mass & Bin Width"
        pltFlExt = "SpB"
    elif args.denFunc == "B":
        thresh = nBkgdInBin > 1e-4
        ratio[thresh] = nSigInBand[thresh] / nBkgdInBand[thresh]
        title = "S/B per Sig. Mass & Bin Width"
        pltFlExt = "B"
    elif args.denFunc == "SQRT(B)":
        denom = np.sqrt(nBkgdInBand)
        thresh = denom > 1e-4
        ratio[thresh] = nSigInBand[thresh] / denom[thresh]
        title = "S/sqrt(B) per Sig. Mass & Bin Width"
        pltFlExt = "SqrtB"
    elif args.denFunc == "SQRT(S+B)":
        denom = np.sqrt(nSigInBand + nBkgdInBand)
        thresh = denom > 1e-4
        ratio[thresh] = nSigInBand[thresh] / denom[thresh]
        title = "S/sqrt(S+B) per Sig. Mass & Bin Width"
        pltFlExt = "SqrtSpB"
    elif args.denFunc == "1":
        ratio = nSigInBand
        title = "N Signal Events in L-Band per Sig. Mass & Bin Width"
        pltFlExt= ""


    fig, ax = plt.subplots(figsize=(12,8))
    plot = ax.imshow(ratio.T)
    fig.colorbar(plot, label="Ratio")
    ax.set_title(title)
    ax.set_xticks(range(len(args.masses)))
    ax.set_xticklabels(args.masses)
    ax.set_yticks(range(len(halfFracs)))
    ax.set_yticklabels(halfFracs)
    ax.set_xlabel("Signal Mass [GeV]")
    ax.set_ylabel("L-Band Fractional Half Width")

    plt.tight_layout()
    plt.savefig("../Plotting/Plots/LBandPlots/sigOver"+ pltFlExt +"inLperMassWidth.png")

    fig, ax = plt.subplots(figsize=(12,8))
    for mN, mass in enumerate(args.masses):
        plot = ax.plot(ratio[mN], label="m"+mass)
    ax.set_xticks(range(len(halfFracs)))
    ax.set_xticklabels(halfFracs)
    ax.set_xlabel("L-Band Fractional Half Width")
    ax.set_ylabel("Ratio")
    ax.legend()
    #plt.savefig("../Plotting/Plots/LBandPlots/sigOver"+ pltFlExt +"inLvsWidth_m"+mass+".png")
    plt.savefig("../Plotting/Plots/LBandPlots/sigOver"+ pltFlExt +"inLvsWidthAllMasses.png")
    
## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
