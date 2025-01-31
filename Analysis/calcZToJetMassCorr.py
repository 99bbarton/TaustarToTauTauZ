#Fits the Z_mass vs Z_pt plane for Z->FatJet events to provide a correction equation to compensate for the bias of the mass as a function of Z pt

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TLegend, gStyle, TH2F, TChain, gPad, TH1F, TF1
import ROOT
import sys
import os
import argparse
from array import array

sys.path.append("../Framework/")
from Colors import getColor, getPalettes

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Calculate the width of the L-bin in the 2D collinear mass plane needed to contain a given frac of signal")
    argparser.add_argument("-i", "--inDir", required=True, help="A directory to find the input root files")
    argparser.add_argument("-y", "--years", required=True, nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to use")
    argparser.add_argument("-p", "--processes", required=True, type=str, nargs="+", choices = ["ALL", "SIG_ALL", "SIG_DEF", "M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"], help = "Which signal masses to plot. SIG_DEF=[M250, M1000, M3000, M5000]")
    argparser.add_argument("-m", "--minMax", nargs=2, type=float, default=[200, 1500], help="The min and max pt bin width to consider")
    argparser.add_argument("-t", "--threshold", type=float, default=0.05, help="The fraction away from the nominal Z mass that corrections are allowed to occur")
    argparser.add_argument("-f", "--fixIntercept", action="store_true", help="If specified, will fix the intercept of the fits to the nominal Z mass")
    argparser.add_argument("-c", "--cuts", type=str, help="Cuts to apply. Overrides default cuts" )
    #argparser.add_argument("-u", "--update", action="store_true", help="If specified, will write a variable Z_mCorr to the trees with the corrected mass values")
    argparser.add_argument("--palette",choices=getPalettes(), default="line_cool", help="A palette to use for plotting")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots and writing calculated values")
    argparser.add_argument("--save", action="append", choices = [".pdf", ".png", ".C"], default=[], help="What file types to save plots as. Default not saved.")
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

    if "SIG_DEF" in args.processes:
        args.processes = ["M250", "M1000", "M3000", "M5000"]
    elif "SIG_ALL" in args.processes:
        args.processes = ["M250","M500","M750","M1000","M1500","M2000","M2500","M3000","M3500","M4000","M4500","M5000"]

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):
    fileList = getFileList(args)
    corrFunc = calcCorrectedZMass(args, fileList)
    #if args.update:
    #    updateTrees(args, fileList, corrFunc)


## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def getFileList(args):
    fileList = []
    for proc in args.processes:
        for year in args.years:
            filename = args.inDir
            if proc.startswith("M"):
                filename += "taustarToTauZ_" + proc.lower() + "_" + year + ".root"
            else:
                filename += proc + "_" + year + ".root"
            fileList.append(filename)

    return fileList

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def calcCorrectedZMass(args, fileList):
    canv = TCanvas("canv", "Z Mass vs Z pT Bias Correction", 1200, 1000)
    canv.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)
    canv.cd()

    cuts = "(Gen_isCand && Z_isCand && Z_dm == 0 &(" + str(args.minMax[0]) + "<= Z_pt && Z_pt < " + str(args.minMax[1]) + "))"
    if args.cuts:
        cuts = args.cuts

    chain = TChain("chain", "All Files")
    for filename in fileList:
        chain.Add(filename+"?#Events")

    #Draw an illustrative precorrection 2d hist
    nBins_m = 30
    binMin_m = 60
    binMax_m = 120
    h_bef = TH2F("h_bef", "Before Correction;Z pT [GeV];Reconstructed Z Mass [GeV]", int((args.minMax[1] - args.minMax[0]) / 20), args.minMax[0], args.minMax[1], nBins_m, binMin_m, binMax_m)
    chain.Draw("Z_mass:Z_pt>>+h_bef", cuts)

    #Get Z_mass vs Z_pt as a graph and fit a line to it
    chain.Draw("Z_mass:Z_pt", cuts, "")
    g_bef = gPad.GetPrimitive("Graph").Clone()
    g_bef.SetTitle("Before Correction;Z pT [GeV];Reconstructed Z Mass [GeV]")

    canv.Clear()
    canv.Divide(2, 2)

    canv.cd(1)
    h_bef.Draw("COLZ")

    canv.cd(2)
    g_bef.Draw("AP")

    fitFunc_bef = TF1("fitFunc_bef", "pol1", args.minMax[0], args.minMax[1])
    #fitFunc_bef = TF1("fitFunc_bef", "[0]+[1]*sqrt(x)", args.minMax[0], args.minMax[1])
    if args.fixIntercept:
        fitFunc_bef.SetParameter(0, 91.18) #Fix the intercept at the Z mass
    g_bef.Fit(fitFunc_bef, "S")

    canv.cd(1)
    fitFunc_bef.Draw("SAME")
    canv.Update()

    #Now apply the correction to a new set of histogram + graph
    canv.cd(4)
    chain.Draw("Z_mass:Z_pt", cuts)
    g_aft = gPad.GetPrimitive("Graph").Clone()
    g_aft.SetTitle("After Correction;Z pT [GeV];Reconstructed Z Mass [GeV]")
    g_aft.Draw("AP")
    h_aft = TH2F("h_aft", "After Correction;Z pT [GeV];Reconstructed Z Mass [GeV]", int((args.minMax[1] - args.minMax[0]) / 20), args.minMax[0], args.minMax[1], nBins_m, binMin_m, binMax_m)

    for point in range(g_aft.GetN()):
        pt = g_aft.GetPointX(point)
        m = g_aft.GetPointY(point)

        corrSize = fitFunc_bef(pt) - 91.18
        if (m - corrSize) > (91.18*(1-args.threshold)) and m > 91.18*(1+args.threshold):
            m_corr = m - corrSize
        else:
            m_corr = m

        g_aft.SetPoint(point, pt, m_corr)
        h_aft.Fill(pt, m_corr)

    #Draw the corrected hist/graph nad re-fit
    canv.cd(4)
    g_aft.Draw("AP")
    fitFunc_aft = TF1("fitFunc_aft", "pol1", args.minMax[0], args.minMax[1])
    if args.fixIntercept:
        fitFunc_aft.SetParameter(0, 91.18) #Fix the intercept at the Z mass
    g_aft.Fit(fitFunc_aft, "S")
    canv.cd(3)
    h_aft.Draw("COLZ")
    fitFunc_aft.Draw("SAME")
    canv.Update()

    #Now make a 1D comparison of the corrected and uncorrected masses
    canv1d = TCanvas("canv1d", "Mass vs Corrected Mass Comparison", 800, 600)
    canv1d.cd()
    leg = TLegend(0.1, 0.7, 0.4, 0.9, "Mass Type")

    h_m = TH1F("h_m", ";m_{Z} [GeV];Events", nBins_m, binMin_m, binMax_m)
    chain.Draw("Z_mass>>h_m", cuts)
    h_m.SetLineColor(getColor(args.palette, 0))
    h_m.SetLineWidth(3)
    leg.AddEntry(h_m, "Jet Mass", "L")
    h_m.Draw("HIST")

    h_mCorr = h_aft.ProjectionY("h_mCorr") 
    h_mCorr.SetLineColor(getColor(args.palette, 1))
    h_mCorr.SetLineWidth(3)
    leg.AddEntry(h_mCorr, "Corrected Mass", "L")
    h_mCorr.Draw("HIST SAME")

    h_m.SetMaximum(1.1 * max(h_m.GetMaximum(), h_mCorr.GetMaximum()))
    leg.Draw()
    canv1d.Update()

    if not args.nP:
        wait = input("waiting...")

    if args.save:
        for ext in args.save:
            canv.SaveAs("zMassVsPt_preVsPostCorr" + ext)
            canv1d.SaveAs("zMass_preVsPostCorr"  + ext)

    return fitFunc_bef

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#This does update trees but is painfully slow
def updateTrees(args, fileList, corrFunc):

    for filename in fileList:
        print("Updating tree in " + filename.split("/")[-1])
        inputFile = ROOT.TFile(filename, "UPDATE")
        tree = inputFile.Get("Events")

        tree.SetBranchStatus("*", 0)
        tree.SetBranchStatus("Z_pt", 1)
        tree.SetBranchStatus("Z_dm", 1)
        tree.SetBranchStatus("Z_mass", 1)

        Z_mCorr = ROOT.vector('float')()
    
        #tree.SetBranchAddress("Z_pt", Z_pt)
        #tree.SetBranchAddress("Z_dm", Z_dm)
        #tree.SetBranchAddress("Z_mass", Z_mass)
        tree.Branch("Z_mCorr", Z_mCorr)
        for entry in tree:

            Z_mCorr.clear()
            Z_pt =  entry.Z_pt
            Z_dm =  entry.Z_dm
            Z_mass =  entry.Z_mass

            if Z_dm != 0:
                continue


            corr = corrFunc(Z_pt)

            if Z_dm == 0 and (Z_mass- corr) > (91.18 * ( 1 - args.threshold)) and Z_mass > 91.18 * (1 + args.threshold):
                Z_mCorr.push_back(Z_mass - corr)
            else:
                Z_mCorr.push_back(Z_mass)
            tree.Fill()

        tree.SetBranchStatus("*", 1)
        inputFile.Write("", ROOT.TObject.kOverwrite)
        inputFile.Close()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
