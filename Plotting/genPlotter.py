#Generator level plotting


from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend
import os
import sys
import argparse

sys.path.append("../Framework/")
import Colors as cols

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-r","--deltaR", action="store_true", help="Plot DeltaR between GEN particles")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], action="append", help = "Which signal masses to plot")
    

    args = argparser.parse_args()

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):

    if args.deltaR:
        plotDR(args)

    return 0

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotDR(args):
    print("Plotting DeltaR of interesting GEN particles...")

    if args.palette:
        palette = args.palette
    else:
        palette = "line"


    #What to plot
    masses = []
    if args.masses:
        masses = args.masses
    else:
        masses = ["1000", "3000", "5000"]
    years = ["2018"]

    #Graphics/plotting params
    gStyle.SetOptStat(0)
    canv = TCanvas("drCanv", "DeltaR Plots", 1200, 1000)
    leg = None
    if len(masses) < 4:
        leg = TLegend(0.7, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
    else:
        leg = TLegend(0.7, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
    nBins = 25
    binLowEdge = 0
    binHighEdge = 5
    
    #Lists to collect histograms of each mass
    hs_dr_tsTauTau = []
    hs_dr_tsTauZ = []
    hs_dr_tauZ = []
    hs_dr_zDaus = []
    
    for massN, mass in enumerate(masses):
        hs_dr_tsTauTau.append(TH1F("h_dr_tsTauTau_"+mass,"GEN: #DeltaR(#tau_{#tau*} , #tau);#DeltaR;", nBins,binLowEdge, binHighEdge))
        hs_dr_tsTauZ.append(TH1F("h_dr_tsTauZ_"+mass,"GEN: #DeltaR(#tau_{#tau*} , Z);#DeltaR;",nBins, binLowEdge, binHighEdge))
        hs_dr_tauZ.append(TH1F("h_dr_tauZ_"+mass,"GEN: #DeltaR(#tau , Z);#DeltaR;", nBins, binLowEdge, binHighEdge))
        hs_dr_zDaus.append(TH1F("h_dr_zDaus_"+mass,"GEN: #DeltaR(Z_{d1} , Z_{d2});#DeltaR;", nBins, binLowEdge, binHighEdge))

        for year in years:
            
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+"_Skim.root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+"_Skim.root")
                continue
            tree = inFile.Get("Events")
            
            h_dr_tsTauTau_yr = TH1F("h_dr_tsTauTau_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, #tau);#DeltaR;", nBins,binLowEdge, binHighEdge)
            h_dr_tsTauZ_yr = TH1F("h_dr_tsTauZ_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, Z);#DeltaR;",nBins, binLowEdge, binHighEdge)
            h_dr_tauZ_yr = TH1F("h_dr_tauZ_"+mass+"_"+year,"GEN: #DeltaR(#tau, Z);#DeltaR;", nBins, binLowEdge, binHighEdge)
            h_dr_zDaus_yr = TH1F("h_dr_zDaus_"+mass+"_"+year,"GEN: #DeltaR(#Z_d1, #Z_d2);#DeltaR;", nBins, binLowEdge, binHighEdge)

            tree.Draw("Gen_dr_tsTauTau>>+h_dr_tsTauTau_"+mass+"_"+year)
            tree.Draw("Gen_dr_tsTauZ>>+h_dr_tsTauZ_"+mass+"_"+year)
            tree.Draw("Gen_dr_tauZ>>+h_dr_tauZ_"+mass+"_"+year)
            tree.Draw("Gen_dr_zDaus>>+h_dr_zDaus_"+mass+"_"+year)

            hs_dr_tsTauTau[massN].Add(h_dr_tsTauTau_yr)
            hs_dr_tsTauZ[massN].Add(h_dr_tsTauZ_yr)
            hs_dr_tauZ[massN].Add(h_dr_tauZ_yr)
            hs_dr_zDaus[massN].Add(h_dr_zDaus_yr)

            inFile.Close()
            #END year loop
        
        hs_dr_tsTauTau[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_tsTauZ[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_tauZ[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_zDaus[massN].SetLineColor(cols.getColor(palette, massN))

        hs_dr_tsTauTau[massN].SetLineWidth(3)
        hs_dr_tsTauZ[massN].SetLineWidth(3)
        hs_dr_tauZ[massN].SetLineWidth(3)
        hs_dr_zDaus[massN].SetLineWidth(3)
        #END mass loop
    
    #Make the plots
    maxs = [0, 0, 0, 0]
    canv.Divide(2, 2)
    for i in range(len(masses)):
        maxs[0] = max(maxs[0], hs_dr_tsTauTau[i].GetMaximum())
        maxs[1] = max(maxs[1], hs_dr_tsTauZ[i].GetMaximum())
        maxs[2] = max(maxs[2], hs_dr_tauZ[i].GetMaximum())
        maxs[3] = max(maxs[3], hs_dr_zDaus[i].GetMaximum())

        if i == 0:
            canv.cd(1)
            hs_dr_tsTauTau[0].Draw("HIST")
            canv.cd(2)
            hs_dr_tsTauZ[0].Draw("HIST")
            canv.cd(3)
            hs_dr_tauZ[0].Draw("HIST")
            canv.cd(4)
            hs_dr_zDaus[0].Draw("HIST")
        else:
            canv.cd(1)
            hs_dr_tsTauTau[i].Draw("HIST SAME")
            canv.cd(2)
            hs_dr_tsTauZ[i].Draw("HIST SAME")
            canv.cd(3)
            hs_dr_tauZ[i].Draw("HIST SAME")
            canv.cd(4)
            hs_dr_zDaus[i].Draw("HIST SAME")

        leg.AddEntry(hs_dr_tsTauTau[i], masses[i], "L")
        
    canv.cd(1)
    hs_dr_tsTauTau[0].SetMaximum(maxs[0] * 1.1)
    leg.Draw()
    canv.cd(2)
    hs_dr_tsTauZ[0].SetMaximum(maxs[1] * 1.1)
    leg.Draw()
    canv.cd(3)
    hs_dr_tauZ[0].SetMaximum(maxs[2] * 1.1)
    leg.Draw()
    canv.cd(4)
    hs_dr_zDaus[0].SetMaximum(maxs[3] * 1.1)
    leg.Draw()
    canv.Update()

    resp = raw_input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/deltaR.png")

    print("... done plotting DeltaR")
    #END plotDR()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##