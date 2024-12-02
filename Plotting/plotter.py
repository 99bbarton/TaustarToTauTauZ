#Script to make a variety of plots

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
    #"SIG_M"     : ["", "#M_{#tau*} [GeV]", 12, 0, 5500], #TODO
    "Z_PT"      : ["Z_pt", "Z_{pT} [GeV]", 100, 0, 1000],
    "Z_ETA"     : ["Z_eta", "#eta_Z", 10, -2.5, 2.5],
    "Z_DAUDR"   : ["Z_dauDR", "#DeltaR(Z_d1, Z_d2)", 80, 0, 4.0],
    "Z_M"       : ["Z_mass", "Reco Z Mass [GeV]", 30, 75, 105],
    "Z_JETR"    : ["Z_jetR", "Best jet R", 3, 3, 9],
    "Z_AK4M"    : ["Jet_mass[Z_jetIdxAK4]", "Rec AK4 Jet Mass [GeV]", 30, 60, 120],
    "Z_AK8M"    : ["FatJet_mass[Z_jetIdxAK8]", "Rec AK8 Jet Mass [GeV]", 30, 60, 120],
    "Z_AK8MSD"  : ["FatJet_msoftdrop[Z_jetIdxAK8]", "Rec AK8 Jet Soft Drop Mass [GeV]", 30, 60, 120],
    "Z_AK4IDX"  : ["Z_jetIdxAK4", "Rec AK4 Jet Idx", 5, -0.5, 5.5],
    "Z_AK8IDX"  : ["Z_jetIdxAK8", "Rec AK8 Jet Idx", 5, -0.5, 5.5],
    "GEN_ZAK4IDX" : ["Gen_z_DATATIER_AK4Idx", "GEN Matched _DATATIER_ AK4 Idx", 5, -0.5, 5.5],
    "GEN_ZAK8IDX" : ["Gen_z_DATATIER_AK8Idx", "GEN Matched _DATATIER_ AK8 Idx", 5, -0.5, 5.5],
    "GEN_ZAK8_M" : ["GenJetAK8_mass[Gen_zGenAK8Idx]", "AK8 Jet Mass of GEN Particles [GeV]", 100, 0, 200],
    "GEN_ZAK4_M" : ["GenJet_mass[Gen_zGenAK4Idx]", "AK4 Jet Mass of Gen Particles [GeV]", 70, 0, 140],
    #"Z_AK4M_GEN"    : ["Jet_mass[Gen_zRecAK4Idx]", "Rec AK4 Jet Mass of GEN-Matched Jet [GeV]", 30, 60, 120], # Redundant with Z_AK*M with cut requiring match
    #"Z_AK8M_GEN"    : ["FatJet_mass[Gen_zRecAK8Idx]", "Rec AK8 Jet Mass of GEN-Matched Jet [GeV]", 30, 60, 120],
    "Z_PN_SCORE": ["FatJet_particleNetWithMass_ZvsQCD[Z_jetIdxPN]", "Particle Net ZvsQCD Score", 20, 0.9, 1.0],
    #"N_Z"       : [""], #TODO
    "VIS_M"     : ["CHANNEL_visM", "Visible Mass [GeV]", 106, 200, 5500], 
    "MIN_COL_M" : ["CHANNEL_minCollM", "Min Collinear Mass [GeV]", 116, 200, 6000], #50 GeV/bin default
    "MAX_COL_M" : ["CHANNEL_maxCollM", "Max Collinear Mass [GeV]", 116, 200, 6000],
    #    "DPHI"      : ["CHANNEL_CHANNELdPhi", "#Delta#phi", 63, 0, 6.3]  #TODO, update dPhi to not have second info, make it cos^@(dphi) maybe?
}

plotEachToLeg = {
    "PROC" : "Process",
    "YEAR" : "Year",
    "CH"   : "Channel",
    "MASS" : "#tau* Mass [GeV]",
    "NA"   : ""
}

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    global varToPlotParams
    argparser = argparse.ArgumentParser(description="Make a large variety of plots corresponding to provided parameters. ")
    argparser.add_argument("vars", nargs='+', choices=varToPlotParams.keys(), help="What to plot. If one argument is provided, a 1D hist of that variable will be produced. If a second argument is also provided, the first arg will be plotted on the x-axis and the second, the y-axis and sim for 3 args.")
    argparser.add_argument("-i", "--inDir", required=True, help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, action="append", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to plot")
    argparser.add_argument("-p", "--processes", required=True, type=str, choices = ["ALL", "SIG_ALL", "SIG_DEF", "M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"], action="append", help = "Which signal masses to plot. SIG_DEF=[M250, M1000, M3000, M5000]")
    argparser.add_argument("-c", "--channel", action="append", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use" )
    argparser.add_argument("-e","--plotEach", choices=["PROC", "YEAR", "CH", "MASS"], default="NA", help="If specified, will make a hist per channel/proc/year rather than combining them into a single hist")
    argparser.add_argument("-d", "--dataTier", choices=["Gen", "Rec","Gen_Rec"], default="Rec",help="What data tier to use. If len(vars)==2, GEN_RECO will user var1:GEN and var2:reco")
    argparser.add_argument("-b", "--modifyBins", nargs='+', help="Modifying the binning of the produced hists. [1, 6] args allowed in order: nBinsD1, minBinD1, maxBinD1, nBinsD2, minBinD2, maxBinD2" )
    argparser.add_argument("-n", "--normalize", action="store_true", help="If specified, will normalize distributions to unit area (1D plots only)")
    argparser.add_argument("--cuts", type=str, help="Cuts to apply. Overrides default cuts" )
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    argparser.add_argument("--nS", action="store_true", help="If specified, will disabled the stat box on 1D plots")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots")
    argparser.add_argument("--save", action="append", choices = [".pdf", ".png", ".C", "ALL"], default=[], help="What file types to save plots as. Default not saved.")
    argparser.add_argument("--pV", action="store_true", help="If specified, will print the support variables to plot and their associated binnings, etc")
    args = argparser.parse_args()  

    if args.pV:
        printVarOps()
        exit(0)

    if len(args.vars) == 1 and args.vars[0] == "SIG_M":
        print("ERROR: SIG_M can only be plotted as the independent variable (with another variable)")
        exit(1)
    if len(args.vars) == 2 and args.normalize:
        print("WARNING: Normalization not currently supported for 2D plots")

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
    elif "SIG_ALL" in args.processes:
        args.processes = ["M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"]

    if "ALL" in args.channel:
        args.channel = ["ETau", "MuTau", "TauTau"]


    if len(args.vars) == 1:
        args.dataTier = [args.dataTier]
    elif args.dataTier == "Gen_Rec":
        args.dataTier = ["Gen", "Rec"]
    else:
        args.dataTier = [args.dataTier, args.dataTier]
                         
        
        

    if args.modifyBins:
       for i, val in enumerate(args.modifyBins):
           if i > 5:
               print("WARNING: Too many arguments were consumed by -b/--modifyBins. Maxiumum of 6 is allowed.")
               break
           if i == 0:
               varToPlotParams[args.vars[0]][2] = int(val)
           elif i == 1 or i == 2:
               varToPlotParams[args.vars[0]][i+2] = float(val)
           elif i == 3:
               varToPlotParams[args.vars[1]][2] = int(val)
           elif i == 4 or i == 5:
               varToPlotParams[args.vars[1]][i-1] = float(val)

    if "ALL" in args.save:
        args.save = [".png", ".pdf", ".C"]
               
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

    if args.nS:
        gStyle.SetOptStat(False)
    canv = TCanvas("canv", "1D Plotting", 1200, 1000)
    canv.SetLeftMargin(0.15)
    makeLegend = args.plotEach != "NA"
    if makeLegend:
        gStyle.SetOptStat(0)
        leg = TLegend(0.7, 0.7, 0.9, 0.9, plotEachToLeg[args.plotEach])

    plotParams = varToPlotParams[args.vars[0]]
    plotParams[0] = plotParams[0].replace("_DATATIER_", args.dataTier[0])
    plotParams[1] = plotParams[1].replace("_DATATIER_", args.dataTier[0])

    titleStr = ";" + plotParams[1] + ";"
    if args.normalize:
        titleStr += "Fraction of Events"
    else:
        titleStr += "Events"
    
    hists = []
    maxVal = 0

    hNameList = []
    if args.plotEach == "CH":
        hNameList = args.channel
        fileNames = filelist["ALL"]
    else:
        hNameList = filelist.keys()
        fileNames = []

    for hNum, hName in enumerate(hNameList):
        hists.append(TH1F("h_"+hName, titleStr, plotParams[2], plotParams[3], plotParams[4]))
        
        if args.plotEach != "CH":
            fileNames = filelist[hName]

        for filename in fileNames:
            inFile = TFile.Open(filename, "r")
            if inFile == "None":
                print("ERROR: Could not read file " + inFile)
                continue
            tree = inFile.Get("Events")

            for ch in args.channel:
                if args.plotEach == "CH" and ch != hName:
                    continue

                if args.cuts:
                    cutStr = args.cuts
                else:
                    cutStr = getCuts(args.vars[0], ch, args.dataTier)
                cutStr = cutStr.replace("CHANNEL", ch)
                                    
                hTemp = TH1F("h_"+hName+"_temp", titleStr, plotParams[2], plotParams[3], plotParams[4])
            
                plotStr = plotParams[0].replace("CHANNEL", ch)
                    
                tree.Draw(plotStr + ">>+h_"+hName+"_temp", cutStr)
            
                hists[-1].Add(hTemp)
                del hTemp

            inFile.Close()
        
        hists[hNum].SetLineColor(getColor(args.palette, hNum))
        hists[hNum].SetLineWidth(3)

        if args.normalize:
            hists[hNum].Scale(1.0 / hists[hNum].GetEntries())

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

    if not args.nP:
        wait = input("Hit ENTER to save plot and end... ")
        
    plotname = "Plots/" + args.vars[0].lower()
    if args.plotEach != "NA":
        plotname += "_per_" + args.plotEach.lower()
    for fileType in args.save:
        canv.SaveAs(plotname + fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- #

def plot2D_hists(filelist, args):
    global varToPlotParams, plotEachToLeg

    canv = TCanvas("canv", "2D Plotting", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)

    makeLegend = len(filelist.keys()) > 1 or args.plotEach == "CH"
    if makeLegend:
        gStyle.SetOptStat(0)
        leg = TLegend(0.7, 0.5, 0.9, 0.7, plotEachToLeg[args.plotEach])


    plotParamsD1 = varToPlotParams[args.vars[0]]
    plotParamsD2 = varToPlotParams[args.vars[1]]
    plotParamsD1[0] = plotParamsD1[0].replace("_DATATIER_", args.dataTier[0])
    plotParamsD1[1] = plotParamsD1[1].replace("_DATATIER_", args.dataTier[0])
    plotParamsD2[0] = plotParamsD2[0].replace("_DATATIER_", args.dataTier[1])
    plotParamsD2[1] = plotParamsD2[1].replace("_DATATIER_", args.dataTier[1])
    
    #Reduce to 5 GeV/bin for max_vs_min coll mass plots to avoid visible binning effects
    if args.vars[1] == "MAX_COL_M" and args.vars[0] == "MIN_COL_M" and not args.modifyBins:
        plotParamsD1[2] = (plotParamsD1[4] - plotParamsD1[3]) // 5
        plotParamsD2[2] = (plotParamsD2[4] - plotParamsD2[3]) // 5

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
        histToFill = "h_"+args.vars[0] + "_vs_"+args.vars[1]+"_"+hName
        hists.append(TH2F(histToFill, ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4]))
        
        if args.plotEach != "CH":
            fileNames = filelist[hName]

        for filename in fileNames:
            inFile = TFile.Open(filename, "r")
            if inFile == "None":
                print("ERROR: Could not read file " + inFile)
                continue
            tree = inFile.Get("Events")

            for ch in args.channel:
                if args.plotEach == "CH" and ch != hName:
                    continue

                if args.cuts:
                    cutStr = args.cuts
                else:
                    cutStrD1 = getCuts(args.vars[0], ch, dataTier1)
                    cutStrD2 = getCuts(args.vars[1], ch, dataTier2)
                    cutStr = "(" + cutStrD1 + ") && (" + cutStrD2 + ")"
                cutStr = cutStr.replace("CHANNEL", ch)

                hTemp = TH2F("h_temp_2d", ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4])

                plotStr = plotParamsD2[0].replace("CHANNEL", ch) + ":" + plotParamsD1[0].replace("CHANNEL", ch)
                if plotStr.find("dPhi") > 0:
                    plotStr = ch + "_" + ch[0].lower() + ch[1:] + "dPhi"
                
                tree.Draw(plotStr + ">>+h_temp_2d", cutStr)

                hTemp.SetLineColor(getColor(args.palette, hNum))
                hTemp.SetMarkerColor(getColor(args.palette, hNum))
                hists[-1].Add(hTemp)
                
                del hTemp

            inFile.Close()
        
        if args.plotEach != "NA":
            hists[hNum].SetLineColor(getColor(args.palette, hNum))
            hists[hNum].SetMarkerColor(getColor(args.palette, hNum))
            hists[hNum].SetFillColor(getColor(args.palette, hNum))
            drawStyle = "SCAT" #This has to be forced in the latest root distributions
            leg.AddEntry(hists[hNum], hName, "F")
        else:
            drawStyle = "COLZ"
    
    for hN, hist in enumerate(hists):

        hist.SetLineColor(getColor(args.palette, hN))
        hist.SetMarkerColor(getColor(args.palette, hN))
        hist.SetFillColor(getColor(args.palette, hN))
        
        if hN == 0:
            hist.Draw(drawStyle)
        else:
            hist.Draw(drawStyle + " SAME")
    
    if args.plotEach != "NA":
        leg.Draw()
    
    canv.Update()
    if not args.nP:
        wait = input("Hit ENTER to save plot and end... ")
    plotname = "Plots/" + args.vars[0].lower() + "_vs_" + args.vars[1].lower()
    for fileType in args.save:
        canv.SaveAs(plotname + fileType)
    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def printVarOps():
    global varToPlotParams

    print("\nThese are the supported variables to plot and their associated default parameters")
    print("Variable Name : [tree variable, axis title, nBins, binMin, binMax]")
    print("-----------------------------------------------------------------------------------------------------")
    for var in varToPlotParams.keys():
        print(var + " : " + str(varToPlotParams[var]))

    print("-----------------------------------------------------------------------------------------------------\n")
        

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
