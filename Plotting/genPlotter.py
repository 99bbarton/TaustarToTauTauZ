#Generator level plotting

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gPad, TH2F
import os
import sys
import argparse
from math import pi
from array import array

sys.path.append("../Framework/")
import Colors as cols

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-d", "--decay", required=False, choices=["Z", "W"], default="Z", help="Whether to plot WNu or ZTau GEN-level parameters")
    argparser.add_argument("-g", "--genVar", choices=["pt", "eta", "phi"], help="A variable in the GenPart collection to plot")
    argparser.add_argument("-r","--deltaR", action="store_true", help="Plot DeltaR between GEN particles")
    argparser.add_argument("--met", action="store_true", help="Plot MET quantities")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, nargs="+", choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], help = "Which signal masses to plot")
    argparser.add_argument("--dm", type=str, choices=["0", "1", "2", "3", "4"], help="Specify plotting of a single decay mode of the Z/W. 0=hadronic, 1=el, 2=mu, 3=tau, 4=invisible")
    argparser.add_argument("-y", "--years", nargs="+", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], help="Which year's data to plot")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots")
    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250", "1000", "3000", "5000"]

    if "ALL" in args.years:
        args.years = ["2018", "2022", "2022post", "2023", "2023post"]
    if "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]

    if args.inDir.startswith("/store"):
        args.inDir = os.environ["ROOTURL"] + args.inDir

    return args

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def main(args):

    if args.deltaR:
        if args.decay == "Z":
            plotDR_TauZ(args)
        else:
            plotDR_WNu(args)
    if args.genVar:
        if args.decay == "Z":
            plotGenPartVar_TauZ(args)
        else:
            plotGenPartVar_WNu(args)
    if args.met:
        if args.decay == "Z":
            plotMET_TauZ(args)
    
    return 0

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

#Plots gen-level DeltaR and DeltaPhi for TauZ final state
def plotDR_TauZ(args):
    print("Plotting DeltaR of interesting GEN particles...")

    if args.palette:
        palette = args.palette
    else:
        palette = "line_cool"


    #What to plot
    masses = args.masses
    cuts =""
    if args.dm:
        cuts += "Gen_zDM==" + args.dm


    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    canv = TCanvas("drCanv", "DeltaR Plots", 1200, 1000)
    canv_dPhi = TCanvas("canv_dPhi", "DeltaPhi of tsTau and Tau", 800, 600)
    leg = None
    leg_dPhi = None
    if len(masses) < 4:
        leg = TLegend(0.7, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
        leg_dPhi = TLegend(0.4, 0.7, 0.6, 0.9, "#tau* Mass [GeV]")
    else:
        leg = TLegend(0.7, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
        leg_dPhi = TLegend(0.4, 0.6, 0.7, 0.9, "#tau* Mass [GeV]")
        leg_dPhi.SetNColumns(2)
    leg.SetTextSize(0.04)
    leg_dPhi.SetTextSize(0.04)
    
    #DeltaR binning
    nBins = 25
    binLowEdge = 0
    binHighEdge = 5

    #Lists to collect histograms of each mass
    hs_dr_tsTauTau = []
    hs_dr_tsTauZ = []
    hs_dr_tauZ = []
    hs_dr_zDaus = []
    hs_dPhi = []
    
    for massN, mass in enumerate(masses):
        hs_dr_tsTauTau.append(TH1F("h_dr_tsTauTau_"+mass,"GEN: #DeltaR(#tau_{#tau*} , #tau);#DeltaR;Events", nBins,binLowEdge, binHighEdge))
        hs_dr_tsTauZ.append(TH1F("h_dr_tsTauZ_"+mass,"GEN: #DeltaR(#tau_{#tau*} , Z);#DeltaR;Events",nBins, binLowEdge, binHighEdge))
        hs_dr_tauZ.append(TH1F("h_dr_tauZ_"+mass,"GEN: #DeltaR(#tau , Z);#DeltaR;Events", nBins, binLowEdge, binHighEdge))
        hs_dr_zDaus.append(TH1F("h_dr_zDaus_"+mass,"GEN: #DeltaR(Z_{d1} , Z_{d2});#DeltaR;Events", nBins, binLowEdge, binHighEdge))
        hs_dPhi.append(TH1F("h_dPhi_"+mass, "GEN: cos^2(#Delta#phi(#tau_{#tau*} , #tau));cos^2(#Delta#phi);Fraction of Events", 50, 0, 1))


        for year in args.years:
            
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")
            
            h_dr_tsTauTau_yr = TH1F("h_dr_tsTauTau_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, #tau);#DeltaR;Events", nBins,binLowEdge, binHighEdge)
            h_dr_tsTauZ_yr = TH1F("h_dr_tsTauZ_"+mass+"_"+year,"GEN: #DeltaR(#{tau_{tau*}}, Z);#DeltaR;Events",nBins, binLowEdge, binHighEdge)
            h_dr_tauZ_yr = TH1F("h_dr_tauZ_"+mass+"_"+year,"GEN: #DeltaR(#tau, Z);#DeltaR;Events", nBins, binLowEdge, binHighEdge)
            h_dr_zDaus_yr = TH1F("h_dr_zDaus_"+mass+"_"+year,"GEN: #DeltaR(#Z_d1, #Z_d2);#DeltaR;Events", nBins, binLowEdge, binHighEdge)
            h_dPhi_yr = TH1F("h_dPhi_"+mass+"_"+year, "GEN: #Delta#phi(#tau_{#tau*} , #tau);cos^2(#Delta#phi);Fraction of Events", 50, 0, 1)

            tree.Draw("Gen_dr_tsTauTau>>+h_dr_tsTauTau_"+mass+"_"+year, cuts)
            tree.Draw("Gen_dr_tsTauZ>>+h_dr_tsTauZ_"+mass+"_"+year, cuts)
            tree.Draw("Gen_dr_tauZ>>+h_dr_tauZ_"+mass+"_"+year, cuts)
            tree.Draw("Gen_dr_zDaus>>+h_dr_zDaus_"+mass+"_"+year, cuts)
            tree.Draw("TMath::Cos(GenPart_phi[Gen_tsTauIdx]-GenPart_phi[Gen_tauIdx])*TMath::Cos(GenPart_phi[Gen_tsTauIdx]-GenPart_phi[Gen_tauIdx])>>+h_dPhi_"+mass+"_"+year, cuts)

            hs_dr_tsTauTau[massN].Add(h_dr_tsTauTau_yr)
            hs_dr_tsTauZ[massN].Add(h_dr_tsTauZ_yr)
            hs_dr_tauZ[massN].Add(h_dr_tauZ_yr)
            hs_dr_zDaus[massN].Add(h_dr_zDaus_yr)
            hs_dPhi[massN].Add(h_dPhi_yr)

            inFile.Close()
            #END year loop
        
        hs_dr_tsTauTau[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_tsTauZ[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_tauZ[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dr_zDaus[massN].SetLineColor(cols.getColor(palette, massN))
        hs_dPhi[massN].SetLineColor(cols.getColor(palette, massN))

        hs_dr_tsTauTau[massN].SetLineWidth(3)
        hs_dr_tsTauZ[massN].SetLineWidth(3)
        hs_dr_tauZ[massN].SetLineWidth(3)
        hs_dr_zDaus[massN].SetLineWidth(3)
        hs_dPhi[massN].SetLineWidth(3)

        hs_dPhi[massN].Scale(1.0/hs_dPhi[massN].GetEntries())

        #END mass loop
    
    #Make the plots
    maxs = [0, 0, 0, 0, 0]
    canv.Divide(2, 2)
    for i in range(len(masses)):
        maxs[0] = max(maxs[0], hs_dr_tsTauTau[i].GetMaximum())
        maxs[1] = max(maxs[1], hs_dr_tsTauZ[i].GetMaximum())
        maxs[2] = max(maxs[2], hs_dr_tauZ[i].GetMaximum())
        maxs[3] = max(maxs[3], hs_dr_zDaus[i].GetMaximum())
        maxs[4] = max(maxs[4], hs_dPhi[i].GetMaximum())

        if i == 0:
            canv.cd(1)
            hs_dr_tsTauTau[0].Draw("HIST")
            canv.cd(2)
            hs_dr_tsTauZ[0].Draw("HIST")
            canv.cd(3)
            hs_dr_tauZ[0].Draw("HIST")
            canv.cd(4)
            hs_dr_zDaus[0].Draw("HIST")
            canv_dPhi.cd()
            hs_dPhi[0].Draw("HIST")
        else:
            canv.cd(1)
            hs_dr_tsTauTau[i].Draw("HIST SAME")
            canv.cd(2)
            hs_dr_tsTauZ[i].Draw("HIST SAME")
            canv.cd(3)
            hs_dr_tauZ[i].Draw("HIST SAME")
            canv.cd(4)
            hs_dr_zDaus[i].Draw("HIST SAME")
            canv_dPhi.cd()
            hs_dPhi[i].Draw("HIST SAME")

        leg.AddEntry(hs_dr_tsTauTau[i], masses[i], "L")
        leg_dPhi.AddEntry(hs_dPhi[i], masses[i], "L")
        
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

    canv_dPhi.cd()
    hs_dPhi[0].SetMaximum(maxs[4] * 1.1)
    leg_dPhi.Draw()
    canv_dPhi.Update()

    if not args.nP:
        resp = input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/deltaR_TauZ.png")
    canv_dPhi.SaveAs("Plots/GenPlots/deltaPhi_tsTauTau.png")
    

    print("... done plotting DeltaR and DeltaPhi")
    #END plotDR()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##


def plotDR_WNu(args):
    print("Plotting DeltaR of interesting GEN particles...")

    if args.palette:
        palette = args.palette
    else:
        palette = "line"


    #What to plot
    masses = args.masses
    cuts =""
    if args.dm:
        cuts += "Gen_zDM==" + args.dm

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    canv = TCanvas("drCanv", "DeltaR Plots", 800, 600)
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
    hs_dr_tauW = []
    
    for massN, mass in enumerate(masses):
        hs_dr_tauW.append(TH1F("h_dr_tauW_"+mass,"GEN: #DeltaR(#tau , W);#DeltaR;Events", nBins, binLowEdge, binHighEdge))

        for year in args.years:
            
            inFile = TFile.Open(args.inDir + "/taustarToWNu_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToWNu_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")
            
            h_dr_tauW_yr = TH1F("h_dr_tauW_"+mass+"_"+year,"GEN: #DeltaR(#tau, W);#DeltaR;Events", nBins, binLowEdge, binHighEdge)

            tree.Draw("GenW_dr_tauW>>+h_dr_tauW_"+mass+"_"+year, cuts)

            hs_dr_tauW[massN].Add(h_dr_tauW_yr)

            inFile.Close()
            #END year loop
        
        hs_dr_tauW[massN].SetLineColor(cols.getColor(palette, massN))

        hs_dr_tauW[massN].SetLineWidth(3)
        #END mass loop
    
    #Make the plots
    maxs = [0]
    canv.Divide(2, 2)
    for i in range(len(masses)):
        maxs[0] = max(maxs[0], hs_dr_tauW[i].GetMaximum())

        if i == 0:
            hs_dr_tauW[0].Draw("HIST")
        else:
            hs_dr_tauW[i].Draw("HIST SAME")

        leg.AddEntry(hs_dr_tauW[i], masses[i], "L")
        
    hs_dr_tauW[0].SetMaximum(maxs[0] * 1.1)
    leg.Draw()

    canv.Update()

    if not args.nP:
        resp = input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/deltaR_WNu.png")

    print("... done plotting DeltaR")
    #END plotDR()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotGenPartVar_TauZ(args):
    print("Plotting " + args.genVar + " of interesting GEN particles...")

    #What to plot
    masses = args.masses
    cuts = ""
    if args.dm:
        cuts += "Gen_zDM==" + args.dm

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    if args.palette:
        palette = args.palette
    else:
        palette = "line_cool"
    canv = TCanvas("genCanv", "GEN Plots", 1600, 1000)
    leg = None
    if args.genVar == "phi":
        if len(masses) < 4:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
            leg.SetNColumns(2)
    else:
        if len(masses) < 4:
            leg = TLegend(0.6, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.6, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
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
    hs_ts = THStack("hs_ts","GEN: #tau*;"+xLabel+";Events" )
    hs_tau= THStack("hs_tau","GEN: #tau;"+xLabel+";Events" )
    hs_tsTau = THStack("hs_tsTau","GEN: #tau_{#tau*};"+xLabel+";Events")
    hs_Z = THStack("hs_Z","GEN: Z;"+xLabel+";Events" )

    for massN, mass in enumerate(masses):
        h_ts = TH1F("h_ts_"+mass,"GEN: #tau*;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
        h_tsTau = TH1F("h_tsTau_"+mass,"GEN: #tau_{#tau*};"+xLabel+";Events", nBins,binLowEdge, binHighEdge)
        h_tau = TH1F("h_tau_"+mass,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
        h_Z = TH1F("h_Z_"+mass,"GEN: Z;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

        for year in args.years:
            
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            h_ts_yr = TH1F("h_ts_"+mass+"_"+year,"GEN: #tau*;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
            h_tsTau_yr = TH1F("h_tsTau_"+mass+"_"+year,"GEN: #tau_{#tau*};"+xLabel+";Events", nBins,binLowEdge, binHighEdge)
            h_tau_yr = TH1F("h_tau_"+mass+"_"+year,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
            h_Z_yr = TH1F("h_Z_"+mass+"_"+year,"GEN: Z;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

            tree.Draw("GenPart_"+args.genVar+"[Gen_tsIdx]>>+h_ts_"+mass+"_"+year, cuts)
            tree.Draw("GenPart_"+args.genVar+"[Gen_tsTauIdx]>>+h_tsTau_"+mass+"_"+year, cuts)
            tree.Draw("GenPart_"+args.genVar+"[Gen_tauIdx]>>+h_tau_"+mass+"_"+year, cuts)
            tree.Draw("GenPart_"+args.genVar+"[Gen_zIdx]>>+h_Z_"+mass+"_"+year, cuts)

            h_ts.Add(h_ts_yr)
            h_tsTau.Add(h_tsTau_yr)
            h_tau.Add(h_tau_yr)
            h_Z.Add(h_Z_yr)

            inFile.Close()
            #END year loop

        h_ts.SetLineColor(cols.getColor(palette, massN))
        h_tsTau.SetLineColor(cols.getColor(palette, massN))
        h_tau.SetLineColor(cols.getColor(palette, massN))
        h_Z.SetLineColor(cols.getColor(palette, massN))
        
        h_ts.SetLineWidth(3)
        h_tsTau.SetLineWidth(3)
        h_tau.SetLineWidth(3)
        h_Z.SetLineWidth(3)

        hs_ts.Add(h_ts)
        hs_tsTau.Add(h_tsTau)
        hs_tau.Add(h_tau)
        hs_Z.Add(h_Z)

        leg.AddEntry(h_Z, mass, "L")
        #END mass loop
    
    #Make the plots
    canv.Divide(2, 2)
    canv.cd(1)
    hs_ts.Draw("NOSTACK")
    hs_ts.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(2)
    hs_tau.Draw("NOSTACK")
    hs_tau.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(3)
    hs_tsTau.Draw("NOSTACK")
    hs_tsTau.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(4)
    hs_Z.Draw("NOSTACK")
    hs_Z.GetXaxis().SetTitleSize(0.04)
    leg.Draw()

    

    canv.Update()

    if not args.nP:
        resp = input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/"+args.genVar+"_TauZ.png")

    print("... done plotting " + args.genVar)
    #END plotGenPartVar()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotGenPartVar_WNu(args):
    print("Plotting " + args.genVar + " of interesting GEN particles...")

    #What to plot
    masses = args.masses
    cuts = ""
    if args.dm:
        cuts += "Gen_zDM==" + args.dm

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    if args.palette:
        palette = args.palette
    else:
        palette = "line"
    canv = TCanvas("genCanv", "GEN Plots", 1200, 600)
    leg = None
    if args.genVar == "phi":
        if len(masses) < 4:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.5, 0.15, 0.9, 0.35, "#tau* Mass [GeV]")
            leg.SetNColumns(2)
    else:
        if len(masses) < 4:
            leg = TLegend(0.6, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
        else:
            leg = TLegend(0.6, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
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
    hs_tau= THStack("hs_tau","GEN: #tau;"+xLabel+";Events" )
    hs_w = THStack("hs_w","GEN: W;"+xLabel+";Events" )

    for massN, mass in enumerate(masses):
        h_tau = TH1F("h_tau_"+mass,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
        h_w = TH1F("h_w_"+mass,"GEN: W;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

        for year in args.years:
            
            inFile = TFile.Open(args.inDir + "/taustarToWNu_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToWNu_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            h_tau_yr = TH1F("h_tau_"+mass+"_"+year,"GEN: #tau;"+xLabel+";Events",nBins, binLowEdge, binHighEdge)
            h_w_yr = TH1F("h_w_"+mass+"_"+year,"GEN: W;"+xLabel+";Events", nBins, binLowEdge, binHighEdge)

            tree.Draw("GenPart_"+args.genVar+"[GenW_tauIdx]>>+h_tau_"+mass+"_"+year, cuts)
            tree.Draw("GenPart_"+args.genVar+"[GenW_wIdx]>>+h_w_"+mass+"_"+year, cuts)

            h_tau.Add(h_tau_yr)
            h_w.Add(h_w_yr)

            inFile.Close()
            #END year loop

        h_tau.SetLineColor(cols.getColor(palette, massN))
        h_w.SetLineColor(cols.getColor(palette, massN))
        
        h_tau.SetLineWidth(3)
        h_w.SetLineWidth(3)

        hs_tau.Add(h_tau)
        hs_w.Add(h_w)

        leg.AddEntry(h_w, mass, "L")
        #END mass loop
    
    #Make the plots
    canv.Divide(2, 1)
    canv.cd(1)
    hs_tau.Draw("NOSTACK")
    hs_tau.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(2)
    hs_w.Draw("NOSTACK")
    hs_w.GetXaxis().SetTitleSize(0.04)
    leg.Draw()

    canv.Update()

    if not args.nP:
        resp = input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/"+args.genVar+"_WNu.png")

    print("... done plotting " + args.genVar)
    #END plotGenPartVar()

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

def plotMET_TauZ(args):
    print("Plotting MET parameters of interesting GEN particles...")

    #What to plot
    masses = args.masses
    cuts = ""
    if args.dm:
        cuts += "Gen_zDM==" + args.dm

    #Graphics/plotting params
    if len(masses) > 1:
        gStyle.SetOptStat(0)
    if args.palette:
        palette = args.palette
    else:
        palette = "line"

    leg = None
    phiLeg = None
    if len(masses) < 4:
        leg = TLegend(0.67, 0.7, 0.9, 0.9, "#tau* Mass [GeV]")
        phiLeg = TLegend(0.67, 0.2, 0.9, 0.5, "#tau* Mass [GeV]")
    else:
        leg = TLegend(0.67, 0.5, 0.9, 0.9, "#tau* Mass [GeV]")
        phiLeg = TLegend(0.5, 0.15, 0.9, 0.4, "#tau* Mass [GeV]")
        phiLeg.SetNColumns(2)
    leg.SetTextSize(0.04)
    phiLeg.SetTextSize(0.04)

    canv = TCanvas("metCanv_tauZ","GEN-Level MET Plots: TauZ", 1600, 1000)

    hs_tausMET_pt = THStack("hs_tausMET_pt", "MET from Taus: pT; pT [GeV];Events")
    hs_tausMET_eta = THStack("hs_tausMET_eta", "MET from Taus: #eta; #eta;Events")
    hS_tausMET_phi = THStack("hs_tausMET_phi", "MET from Taus: #phi; #phi;Events")
    hs_totMET_pt = THStack("hs_totMET_pt", "Total MET from Taus + Z: pT; pT [GeV];Events")
    hs_totMET_eta = THStack("hs_totMET_eta", "Total MET from Taus + Z: #eta; #eta;Events")
    hS_totMET_phi = THStack("hs_totMET_phi", "Total MET from Taus + Z: #phi; #phi;Events")


    for massN, mass in enumerate(masses):
        h_tausMET_pt = TH1F("h_tausMET_pt_" + mass, "MET from Taus: pT; pT [GeV];Events;", 40, 0, 2000 )
        h_tausMET_eta = TH1F("h_tausMET_eta_" + mass, "MET from Taus: #eta; #eta;Events;", 25,-2.5, 2.5)
        h_tausMET_phi = TH1F("h_tausMET_phi_" + mass, "MET from Taus: #phi; #phi;Events;", 8, 0, pi)
        h_totMET_pt = TH1F("h_totMET_pt_" + mass, "Total MET from Taus + Z: pT; pT [GeV];Events;", 40, 0, 2000 )
        h_totMET_eta = TH1F("h_totMET_eta_" + mass, "Total MET from Taus + Z: #eta; #eta;Events;", 25,-2.5, 2.5)
        h_totMET_phi = TH1F("h_totMET_phi_" + mass, "Total MET from Taus + Z: #phi; #phi;Events;", 8, 0, pi)

        for year in args.years:

            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            h_tausMET_pt_yr = TH1F("h_tausMET_pt_"+mass+"_"+year, "MET from Taus: pT; pT [GeV];Events;", 40, 0, 2000 )
            h_tausMET_eta_yr = TH1F("h_tausMET_eta_"+mass+"_"+year, "MET from Taus: #eta; #eta;Events;", 25,-2.5, 2.5)
            h_tausMET_phi_yr = TH1F("h_tausMET_phi_"+mass+"_"+year, "MET from Taus: #phi; #phi;Events;", 8, 0, pi)
            h_totMET_pt_yr = TH1F("h_totMET_pt_"+mass+"_"+year, "Total MET from Taus + Z: pT; pT [GeV];Events;", 40, 0, 2000 )
            h_totMET_eta_yr = TH1F("h_totMET_eta_"+mass+"_"+year, "Total MET from Taus + Z: #eta; #eta;Events;", 25,-2.5, 2.5)
            h_totMET_phi_yr = TH1F("h_totMET_phi_"+mass+"_"+year, "Total MET from Taus + Z: #phi; #phi;Events;", 8, 0, pi)

            tree.Draw("Gen_tausMET_pt>>+h_tausMET_pt_"+mass+"_"+year, cuts)
            tree.Draw("Gen_tausMET_eta>>+h_tausMET_eta_"+mass+"_"+year, cuts)
            tree.Draw("Gen_tausMET_phi>>+h_tausMET_phi_"+mass+"_"+year, cuts)
            tree.Draw("Gen_totMET_pt>>+h_totMET_pt_"+mass+"_"+year, cuts)
            tree.Draw("Gen_totMET_eta>>+h_totMET_eta_"+mass+"_"+year, cuts)
            tree.Draw("Gen_totMET_phi>>+h_totMET_phi_"+mass+"_"+year, cuts)

            h_tausMET_pt.Add(h_tausMET_pt_yr)
            h_tausMET_eta.Add(h_tausMET_eta_yr)
            h_tausMET_phi.Add(h_tausMET_phi_yr)
            h_totMET_pt.Add(h_totMET_pt_yr)
            h_totMET_eta.Add(h_totMET_eta_yr)
            h_totMET_phi.Add(h_totMET_phi_yr)

            del h_tausMET_pt_yr
            del h_tausMET_eta_yr
            del h_tausMET_phi_yr
            del h_totMET_pt_yr
            del h_totMET_eta_yr
            del h_totMET_phi_yr

            inFile.Close()
            #END year loop

        h_tausMET_pt.SetLineColor(cols.getColor(palette, massN))
        h_tausMET_eta.SetLineColor(cols.getColor(palette, massN))
        h_tausMET_phi.SetLineColor(cols.getColor(palette, massN))
        h_totMET_pt.SetLineColor(cols.getColor(palette, massN))
        h_totMET_eta.SetLineColor(cols.getColor(palette, massN))
        h_totMET_phi.SetLineColor(cols.getColor(palette, massN))

        h_tausMET_pt.SetLineWidth(3)
        h_tausMET_eta.SetLineWidth(3)
        h_tausMET_phi.SetLineWidth(3)
        h_totMET_pt.SetLineWidth(3)
        h_totMET_eta.SetLineWidth(3)
        h_totMET_phi.SetLineWidth(3)

        hs_tausMET_pt.Add(h_tausMET_pt)
        hs_tausMET_eta.Add(h_tausMET_eta)
        hS_tausMET_phi.Add(h_tausMET_phi)
        hs_totMET_pt.Add(h_totMET_pt)
        hs_totMET_eta.Add(h_totMET_eta)
        hS_totMET_phi.Add(h_totMET_phi)

        leg.AddEntry(h_tausMET_pt, mass, "L")
        phiLeg.AddEntry(h_tausMET_phi, mass, "L")
        #END mass loop
    
    #Make the plots
    canv.Divide(3, 2)
    canv.cd(1)
    hs_tausMET_pt.Draw("NOSTACK")
    hs_tausMET_pt.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(2)
    hs_tausMET_eta.Draw("NOSTACK")
    hs_tausMET_eta.GetXaxis().SetTitleSize(0.05)
    leg.Draw()
    canv.cd(3)
    hS_tausMET_phi.Draw("NOSTACK")
    hS_tausMET_phi.GetXaxis().SetTitleSize(0.05)
    phiLeg.Draw()
    canv.cd(4)
    hs_totMET_pt.Draw("NOSTACK")
    hs_totMET_pt.GetXaxis().SetTitleSize(0.04)
    leg.Draw()
    canv.cd(5)
    hs_totMET_eta.Draw("NOSTACK")
    hs_totMET_eta.GetXaxis().SetTitleSize(0.05)
    leg.Draw()
    canv.cd(6)
    hS_totMET_phi.Draw("NOSTACK")
    hS_totMET_phi.GetXaxis().SetTitleSize(0.05)
    phiLeg.Draw()

    canv.Update()

    if not args.nP:
        resp = input("Hit ENTER to close plot and save...")

    canv.SaveAs("Plots/GenPlots/met_TauZ.png")

    print("... done plotting TauZ MET")
    #END plotMET_TauZ()


## ------------------------------------------------------------------------------------------------------------------------------------------------- ##

if __name__ == "__main__":
    args = parseArgs()
    main(args)    

## ------------------------------------------------------------------------------------------------------------------------------------------------- ##
