#Generator level plotting


from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gPad
import os
import sys
import argparse
from math import pi

sys.path.append("../Framework/")
import Colors as cols

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-g", "--genVar", choices=["pt", "eta", "phi"], help="A variable in the GenPart collection to plot")
    argparser.add_argument("-r","--deltaR", action="store_true", help="Plot DeltaR between GEN particles")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], action="append", help = "Which signal masses to plot")

    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250", "1000", "3000", "5000"]


    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):

    if args.deltaR:
        plotDR(args)
    if args.genVar:
        plotGenPartVar(args)
    return 0

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotDR(args):
    print("Plotting DeltaR of interesting GEN particles...")

    if args.palette:
        palette = args.palette
    else:
        palette = "line"


    #What to plot
    masses = args.masses
    years = ["2018"]

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    canv = TCanvas("drCanv", "DeltaR Plots", 1200, 1000)
    leg = None
    if len(masses) < 4:
        leg = TLegend(0.7, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
    else:
        leg = TLegend(0.7, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
    leg.SetTextSize(0.04)

    nBins = 25
    binLowEdge = 0
    binHighEdge = 5
    
    #Lists to collect histograms of each mass
    hs_dr_tsTauTau = []
    hs_dr_tsTauZ = []
    hs_dr_tauZ = []
    hs_dr_zDaus = []
    
    for massN, mass in enumerate(masses):
        hs_dr_tsTauTau.append(TH1F("h_dr_tsTauTau_"+mass,"GEN: #DeltaR(#tau_{#tau*} , #tau);#DeltaR;Events", nBins,binLowEdge, binHighEdge))
        hs_dr_tsTauZ.append(TH1F("h_dr_tsTauZ_"+mass,"GEN: #DeltaR(#tau_{#tau*} , Z);#DeltaR;Events",nBins, binLowEdge, binHighEdge))
        hs_dr_tauZ.append(TH1F("h_dr_tauZ_"+mass,"GEN: #DeltaR(#tau , Z);#DeltaR;Events", nBins, binLowEdge, binHighEdge))
        hs_dr_zDaus.append(TH1F("h_dr_zDaus_"+mass,"GEN: #DeltaR(Z_{d1} , Z_{d2});#DeltaR;Events", nBins, binLowEdge, binHighEdge))

        for year in years:
            
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")
            
            h_dr_tsTauTau_yr = TH1F("h_dr_tsTauTau_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, #tau);#DeltaR;Events", nBins,binLowEdge, binHighEdge)
            h_dr_tsTauZ_yr = TH1F("h_dr_tsTauZ_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, Z);#DeltaR;Events",nBins, binLowEdge, binHighEdge)
            h_dr_tauZ_yr = TH1F("h_dr_tauZ_"+mass+"_"+year,"GEN: #DeltaR(#tau, Z);#DeltaR;Events", nBins, binLowEdge, binHighEdge)
            h_dr_zDaus_yr = TH1F("h_dr_zDaus_"+mass+"_"+year,"GEN: #DeltaR(#Z_d1, #Z_d2);#DeltaR;Events", nBins, binLowEdge, binHighEdge)

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

def plotGenPartVar(args):
    print("Plotting " + args.genVar + " of interesting GEN particles...")

    #What to plot
    masses = args.masses
    years = ["2018"]

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    if args.palette:
        palette = args.palette
    else:
        palette = "line"
    canv = TCanvas("genCanv", "GEN Plots", 1200, 1000)
    leg = None
    if args.genVar == "phi":
        if len(masses) < 4:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
            leg.SetNColumns(2)
    else:
        if len(masses) < 4:
            leg = TLegend(0.7, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.7, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
    leg.SetTextSize(0.04)

    #Settings per variable
    nBins = 0
    binLowEdge = 0
    binHighEdge = 0
    xLabel = ""
    if args.genVar == "pt":
        nBins = 70
        binLowEdge = 0
        binHighEdge = 3500
        xLabel = "pT [GeV]"
    elif args.genVar == "eta":
        nBins = 25
        binLowEdge = -2.5
        binHighEdge = 2.5
        xLabel = "#eta"
    elif args.genVar == "phi":
        nBins = 16
        binLowEdge = 0
        binHighEdge = pi
        xLabel = "#phi"
    
    #Lists to collect histograms of each mass
    hs_tsTau = THStack("hs_tsTau","GEN: #tau_{#tau*};"+xLabel+";Events")
    hs_tau= THStack("hs_tau","GEN: #tau;"+xLabel+";Events" )
    hs_Z = THStack("hs_Z","GEN: Z;"+xLabel+";Events" )

    for massN, mass in enumerate(masses):
        h_tsTau = TH1F("h_tsTau_"+mass,"GEN: #tau_{#tau*};"+xLabel+";Events", nBins,binLowEdge, binHighEdge)
        h_tau = TH1F("h_tau_"+mass,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
        h_Z = TH1F("h_Z_"+mass,"GEN: Z;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

        for year in years:
            
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            h_tsTau_yr = TH1F("h_tsTau_"+mass+"_"+year,"GEN: #tau_{#tau*};"+xLabel+";Events", nBins,binLowEdge, binHighEdge)
            h_tau_yr = TH1F("h_tau_"+mass+"_"+year,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
            h_Z_yr = TH1F("h_Z_"+mass+"_"+year,"GEN: Z;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

            tree.Draw("GenPart_"+args.genVar+"[Gen_tsTauIdx]>>+h_tsTau_"+mass+"_"+year)
            tree.Draw("GenPart_"+args.genVar+"[Gen_tauIdx]>>+h_tau_"+mass+"_"+year)
            tree.Draw("GenPart_"+args.genVar+"[Gen_zIdx]>>+h_Z_"+mass+"_"+year)

            h_tsTau.Add(h_tsTau_yr)
            h_tau.Add(h_tau_yr)
            h_Z.Add(h_Z_yr)

            inFile.Close()
            #END year loop

        h_tsTau.SetLineColor(cols.getColor(palette, massN))
        h_tau.SetLineColor(cols.getColor(palette, massN))
        h_Z.SetLineColor(cols.getColor(palette, massN))
        
        h_tsTau.SetLineWidth(3)
        h_tau.SetLineWidth(3)
        h_Z.SetLineWidth(3)

        hs_tsTau.Add(h_tsTau)
        hs_tau.Add(h_tau)
        hs_Z.Add(h_Z)

        leg.AddEntry(h_Z, mass, "L")
        #END mass loop
    
    #Make the plots
    canv.Divide(2, 2)
    canv.cd(1)
    hs_tsTau.Draw("NOSTACK")
    hs_tsTau.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(2)
    hs_tau.Draw("NOSTACK")
    hs_tau.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(3)
    hs_Z.Draw("NOSTACK")
    hs_Z.GetXaxis().SetTitleSize(0.04)
    leg.Draw()

    canv.Update()

    resp = raw_input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/"+args.genVar+".png")

    print("... done plotting " + args.genVar)
    #END plotGenPartVar()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##