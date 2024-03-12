#Plotting of tau related distributions


from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gROOT, TGraph, PyConfig
PyConfig.IgnoreCommandLineOptions = True
import os
import sys
import argparse

sys.path.append("../Framework/")
import Colors as cols

# -----------------------------------------------------------------------------------------------------------------------------

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot tau related variables")
    argparser.add_argument("-i", "--inFile", required=True, action="store", help="A path/filename to plot data from. If does not end with .root assumes the path is a directory from which all files should be plotted" )
    argparser.add_argument("-n", "--nTaus", action="store_true", help="Specify to plot the number of taus passing selection criteria per event")
    argparser.add_argument("-k", "--kinematics", action="store_true", help="Specify to plot tau kinematic distributions")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")

    args = argparser.parse_args()

    if args.inFile.endswith(".root"):
        args.inFile = [args.inFile]
    else:
        if os.path.exists(args.inFile):
            filenames = os.listdir(args.inFile)
            inFiles = []
            for filename in filenames:
                if filename.endswith(".root"):
                    inFiles.append(args.inFile + filename)
            args.inFile = inFiles
        else:
            print("ERROR: Could not extract a valid inFile list from inFile argument of : " + args.inFile)
            exit(1)

    return args

# -----------------------------------------------------------------------------------------------------------------------------

def main(args):
    if args.nTaus:
        plotNTaus(args)
    if args.kinematics:
        plotTauKinematics(args)

# -----------------------------------------------------------------------------------------------------------------------------

#Plot the number of taus/event passing selection criteria for each year and mass
def plotNTaus(args):
    print("Plotting n selected taus per event")

    cuts =""

    gStyle.SetOptStat(11)
    canv = TCanvas("canv_nTaus", "Number of Selected Taus", 800, 600)
    canv.SetLeftMargin(0.15)

    for filename in args.inFile:
        inFile = TFile.Open(filename,"READ")
        tree = inFile.Get("Events")
        
        hist = TH1F("h_nTaus", "Taus Passing Selection Criteria;N taus / event;Events", 5, -0.5, 4.5)

        tree.Draw("SelTaus_n>>+h_nTaus", cuts)

        hist.SetLineWidth(3)

        canv.cd()
        hist.Draw("hist")
        canv.SaveAs("Plots/Taus/nTaus_" + filename.split("/")[-1][0:-5] + ".png")
        del hist

# -----------------------------------------------------------------------------------------------------------------------------


def plotTauKinematics(args):
    print("Plotting kinematic distributions for selected taus")

    if args.palette:
        palette = args.palette
    else:
        palette = "line"
    
    if len(args.inFile) > 1:
        gStyle.SetOptStat(0)
    canv = TCanvas("canv_kinematics", "Tau Kinematics Plots", 1200, 600)

    hs_pt = THStack("hs_pt", "Selected Taus: pT;pT [GeV];Events")
    hs_eta = THStack("hs_eta", "Selected Taus: #eta; #eta;Events")

    for filename in args.inFile:
        inFile = TFile.Open(filename,"READ")
        tree = inFile.Get("Events")
        
        h_pt = TH1F("h_pt", "Selected Taus: pT; pT [GeV]; Event", 120, 0, 3000)
        h_eta = TH1F("h_eta", "Selected Taus: #eta; #eta; Events", 24, -2.4, 2.4)

        #TODO Need to add kinematics for each tau (leading, subleading, etc??)


# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    main(args)
