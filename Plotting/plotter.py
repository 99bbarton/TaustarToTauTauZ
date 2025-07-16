#Script to make a variety of plots

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, TH2F, TMultiGraph, THStack, gPad
import os
import sys
import argparse
from math import pi
from array import array

sys.path.append("../Framework/")
from Colors import getColor, getPalettes, getPalette
from Cuts import getCuts
from mcWeights import getWeight
from datasets import procToSubProc

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

# Map of variable options to [plotting string, histogram axis title string, nBins, bins min, bins max]
varToPlotParams = { 
    "SIG_M"     : ["", "#M_{#tau*} [GeV]", 12, 0, 5500], #TODO
    "Z_PT"      : ["Z_pt", "Z pT [GeV]", 60, 0, 3000],
    "Z_ETA"     : ["Z_eta", "#eta_Z", 10, -2.5, 2.5],
    "Z_DAUDR"   : ["Z_dauDR", "#DeltaR(Z_{d1}, Z_{d2})", 20, 0, 1.0],
    "Z_M"       : ["Z_mass", "Reco Z Mass [GeV]", 60, 60, 120],
    "Z_DM"      : ["Z_dm", "Decay Mode of Z", 3, -0.5, 2.5],
    "Z_JETR"    : ["Z_jetR", "Best jet R", 3, 3, 9],
    "Z_AK4M"    : ["Jet_mass[Z_jetIdxAK4]", "Rec AK4 Jet Mass [GeV]", 30, 60, 120],
    "Z_AK8M"    : ["FatJet_mass[Z_jetIdxAK8]", "Rec AK8 Jet Mass [GeV]", 30, 60, 120],
    "Z_AK8RAWPT": ["FatJet_pt[Z_jetIdxAK8]*FatJet[Z_jetIdxAK8]_rawFactor", "Raw pT of Z AK8 Jet [GeV]", 60, 0, 3000], 
    "Z_AK8SDM"  : ["FatJet_msoftdrop[Z_jetIdxAK8]", "Rec AK8 Jet Soft Drop Mass [GeV]", 30, 60, 120],
    "Z_AK4IDX"  : ["Z_jetIdxAK4", "Rec AK4 Jet Idx", 5, -0.5, 5.5],
    "Z_AK8IDX"  : ["Z_jetIdxAK8", "Rec AK8 Jet Idx", 5, -0.5, 5.5],
    "Z_AK8BTAG" : ["FatJet_btagDeepB[Z_jetIdxAK8]", "FatJet deepB b-tag score", 20, 0, 1],
    #"TAU_PT"    : [["Tau_pt[CHANNEL_tauIdx]", "Tau_pt[CHANNEL_tau1Idx]", "Tau_pt[CHANNEL_tau1Idx]"], "tau pT [GeV]", 80, 0, 4000], #NB, must use cut CHANNEL_havePair/haveTrip/isCand
    "TAU_PT"    : ["Tau_pt[CHANNEL_tauIdx]", "tau pT [GeV]", 50, 0, 2500], #Only includes ETau, MuTau
    "GEN_ZAK4IDX" : ["Gen_z_DATATIER_AK4Idx", "GEN Matched _DATATIER_ AK4 Idx", 5, -0.5, 5.5],
    "GEN_ZAK8IDX" : ["Gen_z_DATATIER_AK8Idx", "GEN Matched _DATATIER_ AK8 Idx", 5, -0.5, 5.5],
    "GEN_ZAK8_M" : ["GenJetAK8_mass[Gen_zGenAK8Idx]", "AK8 Jet Mass of GEN Particles [GeV]", 100, 0, 200],
    "GEN_ZAK4_M" : ["GenJet_mass[Gen_zGenAK4Idx]", "AK4 Jet Mass of Gen Particles [GeV]", 70, 0, 140],
    "GEN_ZDAUDR" : ["Gen_dr_zDaus", "GEN #DeltaR(Z_{d1}, Z_{d2})", 20, 0, 2],
    "GEN_Z_PT"   : ["GenPart_pt[Gen_zIdx]", "GEN Z pT [GeV]", 60, 0, 3000],
    "GEN_TSTAU_PT" : ["GenPart_pt[Gen_tsTauIdx]", "GEN #tau_{#tau*} pT [GeV]", 60, 0, 3000],
    "GEN_TAU_PT" : ["GenPart_pt[Gen_tauIdx]", "GEN #tau_{spec} pT [GeV]", 60, 0, 3000],
    "TAU_VISINVDR": ["Gen_tau_visInvDR", "#DeltaR(tau_vis, tau_inv)]", 10, 0, 0.2],
    "TSTAU_VISINVDR": ["Gen_tsTau_visInvDR", "#DeltaR(tsTau_vis, tsTau_inv)]", 10, 0, 0.2],
    "VISINVDR"      : [["Gen_tau_visInvDR", "Gen_tsTau_visInvDR"], "#DeltaR(#tau_{vis}, #tau_{inv})", 10, 0, 0.1],      
    #"Z_AK4M_GEN"    : ["Jet_mass[Gen_zRecAK4Idx]", "Rec AK4 Jet Mass of GEN-Matched Jet [GeV]", 30, 60, 120], # Redundant with Z_AK*M with cut requiring match
    #"Z_AK8M_GEN"    : ["FatJet_mass[Gen_zRecAK8Idx]", "Rec AK8 Jet Mass of GEN-Matched Jet [GeV]", 30, 60, 120],
    "Z_PN_SCORE": ["FatJet_particleNetWithMass_ZvsQCD[Z_jetIdxPN]", "Particle Net ZvsQCD Score", 20, 0.9, 1.0],
    #"N_Z"       : [""], #TODO
    "VIS_M"     : ["CHANNEL_visM", "Visible Mass [GeV]", 106, 200, 5500], 
    "MIN_COL_M" : ["CHANNEL_minCollM", "Min Collinear Mass [GeV]", 116, 200, 6000], #50 GeV/bin default
    "MAX_COL_M" : ["CHANNEL_maxCollM", "Max Collinear Mass [GeV]", 116, 200, 6000],
    "COS2DPHI"  : ["cos(CHANNEL_CHANNELDPhi)*cos(CHANNEL_CHANNELDPhi)", "cos^2(#Delta#phi)", 63, 0, 6.3],
    "COSDPHI"      : ["cos(CHANNEL_CHANNELDPhi)","cos(#Delta#phi)", 20, -1, 1],
    "SINDPHI"      : ["sin(CHANNEL_CHANNELDPhi)","sin(#Delta#phi)", 20, -1, 1],
    "DPHI"      : ["CHANNEL_CHANNELDPhi","#Delta#phi", 32, 0, 6.4 ],
    "TAUSDR"    : ["CHANNEL_CHANNELDR", "#DeltaR(#tau_{1},#tau_{2}))", 50, 0, 5],
    "BOOST_DR"  : ["Boost_dR", "#DeltaR(Z_{subJet1},Z_{subJet2})", 50, 0, 5],
    "BOOST_DPHI"  : ["Boost_dPhi", "#Delta#phi(Z_{subJet1},Z_{subJet2})", 16, 0, 6.4],
    "BOOST_PT" : ["Boost_pt[SJIDX]", "SubJet pT in Z Ref. Frame [GeV]", 60, 0, 60],
    "BOOST_PHI" : ["Boost_phi[SJIDX]", "SubJet #phi in Z Ref. Frame", 10, -3.14, 3.14],
    "BOOST_ETA" : ["Boost_eta[SJIDX]", "SubJet #eta in Z Ref. Frame [GeV]", 10, -2.5, 2.5],
    "RECL_M"    : ["ZReClJ_mass", "Re-clustered Z Jet Mass [GeV]", 60, 60, 120],
    "RECL_N"    : ["ZReClJ_nSJs", "Number of re-clustered AK4 SubJets", 10, 0.5, 10.5],
    "RECL_PT"   : ["ZReClJ_pt", "Re-clustered Z Jet pT [GeV]]", 60, 0, 3000],
    
}

plotEachToLeg = {
    "PROC"   : "Process",
    "SP" : "Process",
    "YEAR"   : "Year",
    "CH"     : "Channel",
    "MASS"   : "#tau* Mass [GeV]",
    "DM"     : "Z Decay Mode",
    "SJ"     : "Z SubJet",
    "NA"   : ""
}



## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    global varToPlotParams, plotEachToLeg
    argparser = argparse.ArgumentParser(description="Make a large variety of plots corresponding to provided parameters. ")
    argparser.add_argument("vars", nargs='+', choices=varToPlotParams.keys(), help="What to plot. If one argument is provided, a 1D hist of that variable will be produced. If a second argument is also provided, the first arg will be plotted on the x-axis and the second, the y-axis.")
    argparser.add_argument("-i", "--inDir", default="DEF", help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to plot")
    argparser.add_argument("-p", "--processes", required=True, type=str, nargs="+", choices = ["ALL", "SIG_ALL", "SIG_DEF", "M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000", "BKGD", "BKGDnoQCD", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"], help = "Which signal masses to plot. SIG_DEF=[M250, M1000, M3000, M5000]")
    argparser.add_argument("-c", "--channel", nargs="+", choices=["ALL", "ETau", "MuTau", "TauTau"], default=["ALL"], help="What tau decay channels to use" )
    argparser.add_argument("-e", "--plotEach", choices=plotEachToLeg.keys(), default="NA", help="If specified, will make a hist/graph per channel/proc/year rather than combining them into a single hist")
    #argparser.add_argument("-g", "--graph", action="store_true", help="Requries 2 vars. If specified, will make a graph of the passed vars rather than a 2D hist" )
    argparser.add_argument("-d", "--dataTier", choices=["Gen", "Rec","Gen_Rec"], default="Rec",help="What data tier to use. If len(vars)==2, GEN_RECO will user var1:GEN and var2:reco")
    argparser.add_argument("-b", "--modifyBins", nargs='+', help="Modifying the binning of the produced hists. [1, 6] args allowed in order: nBinsD1, minBinD1, maxBinD1, nBinsD2, minBinD2, maxBinD2" )
    argparser.add_argument("-l", "--logScale", nargs="+", choices=["X","Y","Z"], help="Axis to make log scale")
    argparser.add_argument("-n", "--normalize", action="store_true", help="If specified, will normalize distributions to unit area (1D hists only)")
    argparser.add_argument("-w", "--weights", choices=["ALL", "XS", "NONE"], default="NONE", help="Spefify which weights to apply to MC samples")
    argparser.add_argument("--cuts", type=str, help="Cuts to apply. Overrides default cuts" )
    argparser.add_argument("-a", "--addCuts", type=str, help="A cut to add to those returned by Cuts::getCuts")
    argparser.add_argument("--effCut", type=str, help="If provided, will make an effiency plot by requiring the specified additional cut for the numerator and the cuts from '--cuts' for both numerator and denominator" )
    argparser.add_argument("-s", "--stack", action="store_true", help="If specified, background samples will be stacked")
    argparser.add_argument("--sumBkgd", action="store_true", help="If specified, background samples will be combined into a single 'background' category.")
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    argparser.add_argument("--sPalette", choices=getPalettes(), default="sydney", help="If --stack, what palette to use for the background MC stack")
    argparser.add_argument("--drawStyle", help="A ROOT drawstyle to use for the plot.'SAME' + multiple vars will plot all the vars on the same 1D hist")
    argparser.add_argument("--nEvents", action="store_true", help="If specified, the number of events will be added to the legend entry for each hist")
    argparser.add_argument("--nS", action="store_true", help="If specified, will disabled the stat box on 1D hists")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots")
    argparser.add_argument("--save", action="append", choices = [".pdf", ".png", ".C", "ALL"], default=[], help="What file types to save plots as. Default not saved.")
    argparser.add_argument("--plotName", action="store", type=str, help="A filename for the saved output")
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
    if len(args.vars) > 2:
        print("WARNING: Only the first two arguments will be used unless '--drawStyle SAME' is passed!")
    #if len(args.vars) != 2 and args.graph:
    #    print("ERROR: Graphs can only be made from 2 specified variables!")
    #    exit(1)


    if args.inDir.startswith("/store"):
        args.inDir = os.environ["ROOTURL"] + args.inDir
    if args.inDir[-1] != "/" and args.inDir != "DEF":
        args.inDir += "/"

    if "ALL" in args.years:
        args.years = ["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"]
    elif "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]
    elif "RUN2" in args.years:
        args.years = ["2016","2016post", "2017", "2018"]

    processes = []
    if "SIG_DEF" in args.processes:
        processes.extend(["M250", "M1000", "M3000", "M5000"])
    elif "SIG_ALL" in args.processes:
        processes.extend(["M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"])
    if "BKGD" in args.processes:
        processes.extend(["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"])
    elif "BKGDnoQCD" in args.processes:
        processes.extend(["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST"])
    for proc in args.processes:
        if proc in ["SIG_DEF", "SIG_ALL", "BKGD", "BKGDnoQCD"]:
            continue
        processes.append(proc)
    args.processes = processes

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

    weights = {}
    weights["XS"] = args.weights == "ALL" or args.weights == "XS"
    args.weights = weights

    if args.logScale:
        if "Z" in args.logScale and len(args.vars) != 2:
            print("WARNING: Ignoring request for Z-axis to be log scaled. There were not two variables specified.")

    if args.effCut and not args.cuts:
        print("WARNING: Efficiency cut was specified but not a denominator cut (i.e. you need both --effCut and --cuts)")
    if args.effCut and args.normalize:
        print("ERROR: Efficiency plotting and normalization were both specified. These are incompatible!")
        exit(1)
    if args.effCut and args.stack:
        print("ERROR: Efficiency plotting and background stacking were both specified. These are incompatible!")
        exit(1)
    if args.sumBkgd and args.stack:
        print("ERROR: Cannot both sum background together and plot it as a stack. Choose one or the other")
        exit(1)

    if "ALL" in args.save:
        args.save = [".png", ".pdf", ".C"]

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):

    filelist = getFileList(args)

    
    if len(args.vars) == 1:
        plot1D(filelist, args)
    elif args.drawStyle:
        if args.drawStyle == "SAME":
            print("SAME feature not yet implemented!") #TODO
            return 1
        else:
            plot2D_hists(filelist, args)
    else:
        #if args.graph:
        #    plot2D_graph(filelist, args)
        #else:
        plot2D_hists(filelist, args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def getFileList(args):
    filelist = {}

    if args.plotEach in ["NA", "CH", "DM", "SJ"]:
        filelist["ALL"] = []
        for proc in args.processes:
            for year in args.years:
                filename = args.inDir
                if proc.startswith("M"):
                    if args.inDir == "DEF":
                        filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["SIG_R" + yearToEra(year)])
                    filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
                    filelist["ALL"].append(filename)
                elif proc in procToSubProc.keys():
                    for subProc in procToSubProc[proc]:
                        if args.inDir == "DEF":
                            filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["BKGD_" + year])
                        else:
                            filename = args.inDir
                        filename += subProc + "_" + year + ".root"
                        filelist["ALL"].append(filename)
                
    elif args.plotEach == "YEAR":
        for year in args.years:
            filelist[year] = []
            for proc in args.processes:
                filename = args.inDir
                if proc.startswith("M"):
                    if args.inDir == "DEF":
                        filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["SIG_R" + yearToEra(year)])
                    filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
                    filelist[year].append(filename)
                elif proc in procToSubProc.keys():
                    for subProc in procToSubProc[proc]:
                        if args.inDir == "DEF":
                            filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["BKGD_" + year])
                        else:
                            filename = args.inDir
                        filename += subProc + "_"
                        filelist[year].append(filename + year + ".root")
    elif args.plotEach == "PROC":
        if args.sumBkgd:
            filelist["Backgrounds"] = []
        for proc in args.processes:
            filelist[proc] = []
            for year in args.years:

                if proc.startswith("M"):
                    if args.inDir == "DEF":
                        filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["SIG_R" + yearToEra(year)])
                    else:
                        filename = args.inDir
                    filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
                    filelist[proc].append(filename)
                elif proc in procToSubProc.keys():
                    for subProc in procToSubProc[proc]:
                        if args.inDir == "DEF":
                            filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["BKGD_" + year])
                        else:
                            filename = args.inDir
                        filename += subProc + "_"
                        if args.sumBkgd:
                            filelist["Backgrounds"].append(filename + year + ".root")
                        else:
                            filelist[proc].append(filename + year + ".root")

            if len(filelist[proc]) == 0: #If we summedBkgd, per-process lists are left empty for non-signal processes
                del filelist[proc]
    elif args.plotEach == "MASS": #Really just a special case of PROC above but convenient for e.g. legend making for sig only plotting
        for proc in args.processes:
            mass = proc[1:]
            filelist[mass] = []
            for year in args.years:
                if args.inDir == "DEF":
                    filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["SIG_R" + yearToEra(year)])
                else:
                    filename = args.inDir
                filename += "taustarToTauZ_m" + mass + "_"
                filelist[mass].append(filename + year + ".root")
    elif args.plotEach == "SP":
        for proc in args.processes:
            for subProc in procToSubProc[proc]:
                filelist[subProc] = []
                for year in args.years:
                    if args.inDir == "DEF":
                        filename = "root://cmsxrootd.fnal.gov/" + str(os.environ["BKGD_" + year])
                    else:
                        filename = args.inDir
                    filename += subProc + "_" + year + ".root"
                    filelist[subProc].append(filename)

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
        legTitle = plotEachToLeg[args.plotEach]
        if args.nEvents:
            legTitle += ": nEvents"
        leg = TLegend(0.7, 0.7, 0.9, 0.9, legTitle)

    plotParams = varToPlotParams[args.vars[0]]
    if type(plotParams[0]) is str:
        plotParams[0] = plotParams[0].replace("_DATATIER_", args.dataTier[0])
    elif type(plotParams[0]) is list:
        for i, varVer in enumerate(plotParams[0]):
            plotParams[0][i] = varVer.replace("_DATATIER_", args.dataTier[0])
    plotParams[1] = plotParams[1].replace("_DATATIER_", args.dataTier[0])

    titleStr = ";" + plotParams[1] + ";"
    if args.normalize:
        titleStr += "Fraction of Events"
    else:
        titleStr += "Events"
    
    hists = []
    if args.effCut:
        numHists = []
    maxVal = 0

    bkgdStack = THStack("bkgds", titleStr)
    bHistNums = []
    bHistEntries = []
    bHistNames = []
    
    hNameList = []
    if args.plotEach == "CH":
        hNameList = args.channel
    elif args.plotEach == "DM":
        hNameList = ["ee", "mumu", "had"]
        dmFromName = {"ee" : 1, "mumu" : 2, "had" : 0}
    elif args.plotEach == "SJ":
        hNameList = ["LeadingSubJet", "SubLeadingSubJet"]
        sjIdxFromName ={"LeadingSubJet":"1", "SubLeadingSubJet":"2"}
    else:
        hNameList = filelist.keys()
        fileNames = []

    palColN = 0
    for hNum, hName in enumerate(hNameList):
        print("Plotting", hName)
        hists.append(TH1F(hName, titleStr, plotParams[2], plotParams[3], plotParams[4]))
        if args.effCut:
            numHists.append(TH1F(hName+"_num", titleStr, plotParams[2], plotParams[3], plotParams[4]))
        
        if args.plotEach in ["CH", "DM", "SJ"]:
            fileNames = filelist["ALL"]
        else:
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
                    
                if args.plotEach == "DM":
                    cutStr += " && Z_dm==" + str(dmFromName[hName])
                if args.addCuts:
                    cutStr += " && " + args.addCuts
                cutStr = cutStr.replace("CHANNEL", ch)

                fileAlone = filename.split("/")[-1]
                nameYearSepIdx = fileAlone.rfind("_")
                subProc = fileAlone[:nameYearSepIdx]
                if "taustar" in subProc:
                    subProc = subProc.split("_")[-1].upper()
                year = fileAlone[nameYearSepIdx + 1:].split(".")[0]
                weight = str(getWeight(subProc, year, xs=args.weights["XS"]))

                hTemp = TH1F("h_"+hName+"_temp", titleStr, plotParams[2], plotParams[3], plotParams[4])

                if type(plotParams[0]) is str:
                    plotStr = plotParams[0].replace("CHANNEL", ch)  
                    if args.plotEach == "SJ":
                        plotStr = plotStr.replace("SJIDX", sjIdxFromName[hName])   

                    tree.Draw(plotStr + ">>+h_"+hName+"_temp", "(" + cutStr + ")*" + weight)

                    hists[-1].Add(hTemp)
                    del hTemp

                    if args.effCut:
                        hTemp_num = TH1F("h_"+hName+"_temp_num", titleStr, plotParams[2], plotParams[3], plotParams[4])
                        cutStr += " && " + args.effCut
                        tree.Draw(plotStr + ">>+h_"+hName+"_temp_num", "(" + cutStr + ")*" + weight)
                        numHists[-1].Add(hTemp_num)
                        del hTemp_num
                elif type(plotParams[0] is list):
                    for i, varVer in enumerate(plotParams[0]):
                        if i > 0:
                            hTemp = TH1F("h_"+hName+"_temp", titleStr, plotParams[2], plotParams[3], plotParams[4])
                            
                        plotStr = varVer.replace("CHANNEL", ch)
                        tree.Draw(plotStr + ">>+h_"+hName+"_temp", "(" + cutStr + ")*" + weight)

                        hists[-1].Add(hTemp)
                        del hTemp

                        if args.effCut:
                            hTemp_num = TH1F("h_"+hName+"_temp_num", titleStr, plotParams[2], plotParams[3], plotParams[4])
                            cutStr += " && " + args.effCut
                            tree.Draw(plotStr + ">>+h_"+hName+"_temp_num", "(" + cutStr + ")*" + weight)
                            numHists[-1].Add(hTemp_num)
                            del hTemp_num
            #END CHANNEL
            inFile.Close()
        #END FILE
        
        if isBkgdMC(hName) and args.stack:
            bHistNums.append(hNum)
            bHistEntries.append(hists[hNum].Integral())
            bHistNames.append(hName)
        else:
            hists[hNum].SetLineColor(getColor(args.palette, palColN))
            hists[hNum].SetLineWidth(3)
            if hName == "Backgrounds":
                hists[hNum].SetFillColor(getColor(args.palette, palColN))
            
            if args.effCut:
                numHists[hNum].SetLineColor(getColor(args.palette, palColN))
                numHists[hNum].SetLineWidth(3)

            if args.normalize:
                hists[hNum].Scale(1.0 / hists[hNum].GetEntries())

            if makeLegend:
                if hName[0]=="M":
                    name = "m_{#tau*}=" + hName[1:]
                else:
                    name = hName
                if args.nEvents:
                    name += f": {hists[hNum].Integral():.2f}"
                
                leg.AddEntry(hists[hNum], name, "L")
            palColN += 1

        if hists[hNum].GetMaximum() > maxVal:
            maxVal = hists[hNum].GetMaximum()
    #END HIST

    canv.Clear()    
    
    if args.stack:
        stackPalette = getPalette(args.sPalette)
        
        #Add hists to stack in order from least to greatest number of entries so the stack renders in log scales
        ordBkgdHNums = [i[0] for i in sorted(enumerate(bHistEntries), key=lambda x:x[1])]
        for num, idx in enumerate(ordBkgdHNums):
            hists[idx].SetLineColor(stackPalette[num])
            hists[idx].SetFillColor(stackPalette[num])
            bkgdStack.Add(hists[bHistNums[idx]])
            if args.nEvents:
                leg.AddEntry(hists[bHistNums[idx]], bHistNames[idx]+ f": {bHistEntries[idx]:.2f}", "F")
            else:
                leg.AddEntry(hists[bHistNums[idx]], bHistNames[idx], "F")
            
        maxVal = max(maxVal, bkgdStack.GetMaximum())
        maxVal = maxVal * 1.2

        gStyle.SetPalette(len(stackPalette), array('i', stackPalette))
        bkgdStack.SetMaximum(maxVal)
        bkgdStack.Draw("HIST PFC PLC")
    elif args.effCut: #NB, can't have both effcut and stack arguments
        for hN, hist in enumerate(hists):
            hist.Sumw2()
            numHists[hN].Sumw2()
            numHists[hN].Divide(hist)
            maxVal = 1.1
            numHists[hN].SetMaximum(maxVal)
            if  hN == 0:
                numHists[hN].Draw("HIST")
            else:
                numHists[hN].Draw("HIST SAME")

        
    if not args.effCut:
        maxVal = max(maxVal, bkgdStack.GetMaximum()*1.2)
        for hN, hist in enumerate(hists):
            if hN in bHistNums:
                continue
            
            hist.SetMaximum(maxVal)
            if not args.stack and hN == 0:
                hist.Draw("HIST")
            else:
                hist.Draw("HIST SAME")
                
    if makeLegend:
        if len(hists) > 5 and not args.nEvents:
            leg.SetNColumns(2)
        leg.Draw()
        
    if args.logScale:
        if "X" in args.logScale:
            canv.SetLogx(True)
        if "Y" in args.logScale:
            canv.SetLogy(True)

    canv.Update()

    if not args.nP:
        wait = input("Hit ENTER to close plot... ")
    
    if args.plotName:
        plotname = args.plotName
    else:
        plotname = "Plots/" + args.vars[0].lower()
    if args.plotEach != "NA":
        plotname += "_per_" + args.plotEach.lower()
    for fileType in args.save:
        canv.SaveAs(plotname + fileType)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plot2D_hists(filelist, args):
    global varToPlotParams, plotEachToLeg

    canv = TCanvas("canv", "2D Hists", 1200, 1000)
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.15)
    gStyle.SetOptStat(0)

    makeLegend = len(filelist.keys()) > 1 or args.plotEach == "CH" or args.plotEach == "DM"
    if makeLegend:
        gStyle.SetOptStat(0)
        legTitle = plotEachToLeg[args.plotEach]
        if args.nEvents:
            legTitle += ": nEvents"
        leg = TLegend(0.65, 0.45, 0.85, 0.65, legTitle)

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

    hists = []
    hNameList = []
    if args.plotEach == "CH":
        hNameList = args.channel
    elif args.plotEach == "DM":
        hNameList = ["ee", "mumu", "had"]
        dmFromName = {"ee" : 1, "mumu" : 2, "had" : 0}
    else:
        hNameList = filelist.keys()

    for hNum, hName in enumerate(hNameList):
        print("Plotting", hName)
        histToFill = "h_"+args.vars[0] + "_vs_"+args.vars[1]+"_"+hName
        hists.append(TH2F(histToFill, ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4]))
        
        if args.plotEach in ["CH", "DM"]:
            fileNames = filelist["ALL"]
        else:
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
                    cutStrD1 = getCuts(args.vars[0], ch, args.dataTier[0])
                    cutStrD2 = getCuts(args.vars[1], ch, args.dataTier[1])
                    cutStr = "(" + cutStrD1 + ") && (" + cutStrD2 + ")"
                if args.plotEach == "DM":
                    cutStr += " && Z_dm==" + str(dmFromName[hName])
                if args.addCuts:
                    cutStr += " && " + args.addCuts
                cutStr = cutStr.replace("CHANNEL", ch)


                fileAlone = filename.split("/")[-1]
                nameYearSepIdx = fileAlone.rfind("_")
                subProc = fileAlone[:nameYearSepIdx]
                if "taustar" in subProc:
                    subProc = subProc.split("_")[-1].upper()
                year = fileAlone[nameYearSepIdx + 1:].split(".")[0]
                weight = str(getWeight(subProc, year, xs=args.weights["XS"]))

                hTemp = TH2F("h_temp_2d", ";"+plotParamsD1[1]+";"+plotParamsD2[1], plotParamsD1[2], plotParamsD1[3], plotParamsD1[4], plotParamsD2[2], plotParamsD2[3], plotParamsD2[4])

                plotStr = plotParamsD2[0].replace("CHANNEL", ch) + ":" + plotParamsD1[0].replace("CHANNEL", ch)
                if plotStr.find("dPhi") > 0:
                    plotStr = ch + "_" + ch[0].lower() + ch[1:] + "dPhi"
                
                tree.Draw(plotStr + ">>+h_temp_2d", "(" + cutStr + ")*" + weight)

                hTemp.SetLineColor(getColor(args.palette, hNum))
                hTemp.SetMarkerColor(getColor(args.palette, hNum))
                hists[-1].Add(hTemp)
                
                del hTemp

            inFile.Close()
        
        if args.plotEach != "NA":
            hists[hNum].SetLineColor(getColor(args.palette, hNum))
            hists[hNum].SetMarkerColor(getColor(args.palette, hNum))
            
            if args.drawStyle:
                drawStyle = args.drawStyle
            else:
                drawStyle = "SCAT" #This has to be forced in the latest root distributions
            if drawStyle.find("CANDLE") < 0:        
                hists[hNum].SetFillColor(getColor(args.palette, hNum))

            name = hName
            if args.nEvents:
                name += f": {hists[hNum].Integral():.2e}"
            leg.AddEntry(hists[hNum], name, "F")
        else:
            if args.drawStyle:
                drawStyle = args.drawStyle
            else:
                drawStyle = "COLZ"
    
    for hN, hist in enumerate(hists):
        
        if hN == 0:
            hist.Draw(drawStyle)
        else:
            hist.Draw(drawStyle + " SAME")
    
    if args.plotEach != "NA":
        leg.Draw()

    if args.logScale:
        if "X" in args.logScale:
            canv.SetLogx(True)
        if "Y" in args.logScale:
            canv.SetLogy(True)
        if "Z" in args.logScale:
            canv.SetLogz(True)   
    
    canv.Update()
    if not args.nP:
        wait = input("Hit ENTER to save plot and end... ")
    if args.plotName:
        plotname = args.plotName
    else:
        plotname = "Plots/" + args.vars[0].lower() + "_vs_" + args.vars[1].lower()
    for fileType in args.save:
        canv.SaveAs(plotname + fileType)
    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#TODO
def plot2D_graph(filelist, args):
    global varToPlotParams, plotEachToLeg

    canv = TCanvas("canv", "2D Graphs", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)

    makeLegend = len(filelist.keys()) > 1 or args.plotEach == "CH" or args.plotEach == "DM"
    if makeLegend:
        gStyle.SetOptStat(0)
        leg = TLegend(0.7, 0.2, 0.9, 0.4, plotEachToLeg[args.plotEach])
    
    plotParamsD1 = varToPlotParams[args.vars[0]]
    plotParamsD2 = varToPlotParams[args.vars[1]]
    
    plotParamsD1[0] = plotParamsD1[0].replace("_DATATIER_", args.dataTier[0])
    plotParamsD1[1] = plotParamsD1[1].replace("_DATATIER_", args.dataTier[0])
    plotParamsD2[0] = plotParamsD2[0].replace("_DATATIER_", args.dataTier[1])
    plotParamsD2[1] = plotParamsD2[1].replace("_DATATIER_", args.dataTier[1])

    graphs = TMultiGraph()
    gNameList = []
    if args.plotEach == "CH":
        gNameList = args.channels
    elif args.plotEach == "DM":
        gNameList = ["ee", "mumu", "had"]
        dmFromName = {"ee" : 1, "mumu" : 2, "had" : 0}
    else:
        gNameList = filelist.keys()

    yVals = {}
    for gNum, gName in enumerate(gNameList):
        yVals
        
        if args.plotEach in ["CH", "DM"]:
            fileNames = filelist["ALL"]
        else:
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
                if args.plotEach == "DM":
                    cutStr += " && Z_dm==" + str(dmFromName[hName])
                if args.addCuts:
                    cutStr += " && " + args.addCuts
                cutStr = cutStr.replace("CHANNEL", ch)

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

def yearToEra(year):
    if year in ["2016", "2016post", "2017", "2018"]:
        return "2"
    elif year in ["2022", "2022post", "2023", "2023post"]:
        return "3"
    else:
        return ""

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def isBkgdMC(name):
    global procToSubProc
    subProcesses = ["ZZto2L2Nu", "ZZto2L2Q", "ZZto2Nu2Q", "ZZto4L", "WZto2L2Q", "WZto3LNu", "WZtoLNu2Q", "WWto2L2Nu", "WWto4Q", "WWtoLNu2Q", "WtoLNu-4Jets", "DYto2L-2Jets_MLL-10to50", "DYto2L-2Jets_MLL-50", "TTto2L2Nu", "TTto4Q", "TTtoLNu2Q", "TBbarQ_t-channel_4FS", "TWminusto2L2Nu", "TWminusto2L2Nu", "TbarBQ_t-channel_4FS", "TbarWplusto2L2Nu", "TbarWplusto2L2Nu", "TbarWplustoLNu2Q"]

    return (name in procToSubProc.keys()) or name in subProcesses


## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
