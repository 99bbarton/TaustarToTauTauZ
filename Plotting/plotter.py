#Script to make mass plots 

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gPad, TH2F
import os
import sys
import argparse
from math import pi
from array import array

sys.path.append("../Framework/")
from Colors import getColor, getPalettes
from Cuts import getCuts

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

# Map of variable options to [plotting string, histogram axis title string, nBins, bins min, bins max]
varToPlotParams = { 
    "SIG_M"     : ["", "#M_{#tau*} [GeV]", 12, 0, 5500],
    "Z_PT"      : ["Z_pt", "Z_{pT} [GeV]", 100, 0, 1000],
    "Z_ETA"     : ["Z_eta", "#eta_Z", 10, -2.5, 2.5],
    "Z_DAUDR"   : ["Z_dauDR", "#DeltaR(Z_d1, Z_d2)", 80, 0, 4.0],
    "Z_M"       : ["Z_mass", "Reco Z Mass [GeV]", 30, 60, 120],
    "VIS_M"     : ["CHANNEL_visM", "Visible Mass [GeV]", 530, 200, 5500], 
    "MIN_COL_M" : ["CHANNEL_minCollM", "Min Collinear Mass [GeV]", 212, 200, 5500], #25 GeV/bin default
    "MAX_COL_M" : ["CHANNEL_maxCollM", "Max Collinear Mass [GeV]", 212, 200, 5500]
}

plotEachToLeg = {
    "PROC" : "Process",
    "YEAR" : "Year",
    "CH"   : "Channel",
    "MASS" : "#tau^* Mass [GeV]",
    "NA"   : ""
}

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to make various mass plots")
    argparser.add_argument("vars", nargs='+', choices=["SIG_M", "Z_PT", "Z_ETA", "Z_DAUDR", "Z_M", "VIS_M", "MIN_COL_M", "MAX_COL_M"], help="What to plot. If one argument is provided, a 1D hist of that variable will be produced. If a second argument is also provided, the first arg will be plotted on the x-axis and the second, the y-axis and sim for 3 args.")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, action= "append", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to plot")
    argparser.add_argument("-p", "--processes", required=True, type=str, choices = ["ALL", "SIG_ALL", "SIG_DEF", "M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"], action="append", help = "Which signal masses to plot. SIG_DEF=[M250, M1000, M3000, M5000]")
    argparser.add_argument("-c", "--channel", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use" )
    argparser.add_argument("-e","--plotEach", choices=["PROC", "YEAR", "CH", "MASS"], default="NA", help="If specified, will make a hist per channel/proc/year rather than combining them into a single hist")
    argparser.add_argument("-d", "--dataTier", choices=["GEN", "RECO","GEN_RECO"], default="RECO",help="What data tier to use. If len(vars)==2, GEN_RECO will user var1:GEN and var2:reco")
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    args = argparser.parse_args()  

    if len(args.vars) == 1 and args.vars[0] == "SIG_M":
        print("ERROR: SIG_M can only be plotted as the independent variable (with another variable)")
        exit(1)

    if args.inDir.startswith("/store"):
        args.inDir = os.environ["ROOTURL"] + args.inDir
    if args.inDir[-1] != "/":
        args.inDir += "/"

    if "ALL" in args.years:
        args.years = ["2018", "2022", "2022post", "2023", "2023post"]
    elif "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]
    elif "RUN2" in args.years:
        args.years = ["2016","2016post", "2017", "2018"]

    if "SIG_DEF" in args.processes:
        args.processes = ["M250", "M1000", "M3000", "M5000"]
    elif "SIG" in args.processes:
        args.processes = ["M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"]

    if "ALL" in args.channel:
        args.channel = ["ETau", "MuTau", "TauTau"]

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):

    filelist = getFileList(args)

    if len(args.vars) == 1:
        plot1D(filelist, args)
    elif len(args.vars) == 2:
        plot2D_hists(filelist, args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def getFileList(args):
    filelist = {}

    if args.plotEach == "NA" or args.plotEach == "CH":
        filelist["ALL"] = []
        for proc in args.processes:
            for year in args.years:
                filename = args.inDir
                if proc.startswith("M"):
                    filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
                else:
                    filename += proc + "_" + year + ".root"
                filelist["ALL"].append(filename)
    elif args.plotEach == "YEAR":
        for year in args.years:
            filelist[year] = []
            for proc in args.processes:
                filename = args.inDir
                if proc.startswith("M"):
                    filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
                else:
                    filename += proc + "_" + year + ".root"
                filelist[year].append(filename)
    elif args.plotEach == "PROC":
        for proc in args.processes:
            filelist[proc] = []
            for year in args.years:
                
                if proc.startswith("M"):
                    filename = args.inDir + "taustarToTauZ_" + proc.lower() + "_"
                else:
                    filename = args.inDir + proc + "_"
                filelist[proc].append(filename + year + ".root")
    elif args.plotEach == "MASS": #Really just a special case of PROC above but convenient for e.g. legend making for sig only plotting
        for proc in args.processes:
            mass = proc[1:]
            filelist[mass] = []
            for year in args.years:
                filename = args.inDir + "taustarToTauZ_m" + mass + "_"
                filelist[mass].append(filename + year + ".root")

    return filelist
## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plot1D(filelist, args):
    global varToPlotParams, plotEachToLeg

    canv = TCanvas("canv", "Mass Plotting", 800, 600)
    makeLegend = args.plotEach != "NA"
    if makeLegend:
        gStyle.SetOptStat(0)
        leg = TLegend(0.7, 0.7, 0.9, 0.9, plotEachToLeg[args.plotEach])

    plotParams = varToPlotParams[args.vars[0]]

    hists = []
    maxVal = 0

    hNameList = []
    if args.plotEach == "CH":
        hNameList = args.channels
        fileNames = filelist["ALL"]
    else:
        hNameList = filelist.keys()
        fileNames = []  

    for hNum, hName in enumerate(hNameList):
        hists.append(TH1F("h_"+hName, ";"+plotParams[1]+";Events", plotParams[2], plotParams[3], plotParams[4]))
        
        if args.plotEach == "NA":
            fileNames = filelist.keys()[hNum]

        for filename in fileNames:
            inFile = TFile.Open(filename, "r")
            if inFile == "None":
                print("ERROR: Could not read file " + inFile)
                continue
            tree = inFile.Get("Events")

            for ch in args.channel:
                if args.plotEach == "CH" and ch != hName:
                    continue

                cutStr = getCuts(args.vars[0], ch, args.dataTier)
                hTemp = TH1F("h_"+hName+"_temp", ";"+plotParams[1]+";Events", plotParams[2], plotParams[3], plotParams[4])
            
                plotStr = plotParams[0].replace("CHANNEL", ch)
                tree.Draw(plotStr + ">>+h_"+hName+"_temp", cutStr)
            
                hists[-1].Add(hTemp)
                del hTemp

            inFile.Close()
        
        hists[hNum].SetLineColor(getColor(args.palette, hNum))
        hists[hNum].SetLineWidth(3)

        if hists[hNum].GetMaximum() > maxVal:
            maxVal = hists[hNum].GetMaximum()

        if makeLegend:
            leg.AddEntry(hists[hNum], hName, "L")

    canv.Clear()
    maxVal = maxVal * 1.1
    
    for hN, hist in enumerate(hists):
        hist.SetMaximum(maxVal)
        if hN == 0:
            hist.Draw("HIST")
        else:
            hist.Draw("HIST SAME")
    
    if makeLegend:
        leg.Draw()

    canv.Update()
    
    wait = input("Hit ENTER to save plot and end... ")
    plotname = "Plots/" + args.vars[0].lower()
    if args.plotEach != "NA":
        plotname += "_per_" + args.plotEach.lower()
    canv.SaveAs(plotname + ".png")

## ------------------------------------------------------------------------------------------------------------------------------------------------- #

def plot2D_hists(filelist, args):
    global varToPlotParams, plotEachToLeg

    canv = TCanvas("canv", "Mass Plotting", 800, 600)
    gStyle.SetOptStat(0)

    makeLegend = len(filelist.keys()) > 1 or args.plotEach == "CH"
    if makeLegend:
        gStyle.SetOptStat(0)
        leg = TLegend(0.7, 0.7, 0.9, 0.9, plotEachToLeg[args.plotEach])


    plotParamsD1 = varToPlotParams[args.vars[0]]
    plotParamsD2 = varToPlotParams[args.vars[1]]

    #Reduce to 5 GeV/bin for max_vs_min coll mass plots to avoid visible binning effects
    if args.vars[1] == "MAX_COL_M" and args.vars[0] == "MIN_COL_M":
        plotParamsD1[2] = (plotParamsD1[4] - plotParamsD1[3]) / 5 
        plotParamsD2[2] = (plotParamsD2[4] - plotParamsD2[3]) / 5

    if args.dataTier == "GEN_RECO":
        dataTier1 = "GEN"
        dataTier2 = "RECO"
    else:
        dataTier1 = dataTier2 = args.dataTier

    hists = []
    hNameList = []
    if args.plotEach == "CH":
        hNameList = args.channels
        fileNames = filelist["ALL"]
    else:
        hNameList = filelist.keys()
        fileNames = []  

    for hNum, hName in enumerate(hNameList):
        hists.append(TH2F("h_"+args.vars[0] + "_vs_"+args.vars[1]+"_"+hName, ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4]))
        
        if args.plotEach == "NA":
            fileNames = filelist.keys()[hNum]

        for filename in fileNames:
            inFile = TFile.Open(filename, "r")
            if inFile == "None":
                print("ERROR: Could not read file " + inFile)
                continue
            tree = inFile.Get("Events")

            for ch in args.channel:
                if args.plotEach == "CH" and ch != hName:
                    continue

                cutStrD1 = getCuts(args.vars[0], ch, dataTier1)
                cutStrD2 = getCuts(args.vars[1], ch, dataTier2)
                cutStr = "(" + cutStrD1 + ") && (" + cutStrD2 + ")"

                hTemp = TH2F("h_temp_2d", ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4])

                plotStr = plotParamsD2[0].replace("CHANNEL", ch) + ":" + plotParamsD1[0].replace("CHANNEL", ch)
                tree.Draw(plotStr + ">>+h_temp_2d", cutStr)

                hists[-1].add(hTemp)
                del hTemp

            inFile.Close()
        
        if args.plotEach != "NA":
            hists[hNum].SetLineColor(getColor(args.palette, hNum))
            hists[hNum].SetMarkerColor(getColor(args.palette, hNum))
            drawStyle = ""
            leg.AddEntry(hists[hNum], hName, "L")
        else:
            drawStyle = "COLZ"
    
    for hN, hist in enumerate(hists):
        if hN == 0:
            hist.Draw(drawStyle)
        else:
            hist.Draw(drawStyle + " SAME")
    
    if args.plotEach != "NA":
        leg.Draw()
    
    canv.Update()
    wait = input("Hit ENTER to save plot and end... ")
    plotname = "Plots/" + args.vars[0].lower() + "_vs_" + args.vars[1].lower()
    canv.SaveAs(plotname + ".png")

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#TODO
def plot2D_graphs(filelist, args):
    print("ERROR: NOT YET IMLEMENTED")

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
