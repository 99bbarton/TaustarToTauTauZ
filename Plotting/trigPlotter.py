from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gROOT, TGraph, PyConfig
PyConfig.IgnoreCommandLineOptions = True
import os
import sys
import argparse
from array import array

sys.path.append("../Framework/")
import Colors as cols

#Take in command line arguments and return a dictionary of settings to use for calculations/plotting
def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-t", "--triggers", required=True, action="append", help="A trigger string to test")
    #argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], action="append", help = "Which signal masses to plot")
    argparser.add_argument("-y", "--years", choices=["ALL", "2018"], type=str, default=["ALL"], action="append")

    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"]

    if "ALL" in args.years:
        args.years = ["2018"] #TODO Update this as more years are processed

    return args

# -----------------------------------------------------------------------------------------------------------------------------

#Main driving function, calls calculation/plotting functions based on args
def main(args):
    trigEffsPerMass(args)

# -----------------------------------------------------------------------------------------------------------------------------

def trigEffsPerMass(args):

    canv = TCanvas("canv", "Trigger Efficiencies Per Taustar Mass", 800, 800)
    gStyle.SetOptStat(0)

    #For now, base cuts use gen info and just require z->ee/mumu/had + etau/mutau/tautau
    baseCuts = "(Gen_zDM > 0 && Gen_zDM < 3) && (Gen_tsTauDM == 0 || Gen_tauDM == 0)"

    for trigger in args.triggers:
        for year in args.years:
            intMasses = []
            efficienies = []
            for mass in args.masses:
                intMasses.append(int(mass))

                inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
                if inFile == "None":
                    print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                    continue
                tree = inFile.Get("Events")
                denEvents = tree.GetEntries(baseCuts)
                efficienies.append(tree.GetEntries(baseCuts + trigger))
                efficienies[-1] /= float(denEvents)

                inFile.Close()
            
            graph = TGraph(len(intMasses), array("f", intMasses), array("f", efficienies))
            graph.SetTitle(trigger + ";Taustar Mass [GeV]; Overall Efficiency")
            graph.GetYaxis().SetMaximum(1.0)
            graph.SetMarkerStyle(5)

            canv.cd()
            graph.Draw("ALP")
            wait = input("Hit ENTER to continue...")
            canv.SaveAs("Plots/TrigPlots/effPerMass_"+ year + "_" + trigger + ".png")
            

# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    main(args)