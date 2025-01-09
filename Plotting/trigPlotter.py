

#-t HLT_PFMET200_NotCleaned -t HLT_PFMET200_HBHE_BeamHaloCleaned -t HLT_CaloMET250_NotCleaned -t HLT_CaloMET250_HBHECleaned -t (HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg||HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1||HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1)

#

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gROOT, TGraph, PyConfig, TCut
PyConfig.IgnoreCommandLineOptions = True
import os
import sys
import argparse
from array import array

sys.path.append("../Framework/")
import Colors as cols
from trigDef import trig_run3_gen, trig_run2_gen

#Take in command line arguments and return a dictionary of settings to use for calculations/plotting
def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-t", "--triggers", required=True, nargs="+", help="A trigger string to test")
    #argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, nargs= "+", choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], help = "Which signal masses to plot")
    argparser.add_argument("-y", "--years", choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], type=str, nargs="+", help="What years to plot")
    argparser.add_argument("--nP", action="store_true", help="If specified, will not prompt the user before saving and closing plots")
    
    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"]

    #TODO update as more years are processed
    if "ALL" in args.years:
        args.years = ["2018", "2022", "2022post", "2023", "2023post"]
    if "RUN3" in args.years:
        args.years = ["2022", "2022post", "2023", "2023post"]

    if args.inDir.startswith("/store"):
        args.inDir = os.environ["ROOTURL"] + args.inDir
    
    return args

# -----------------------------------------------------------------------------------------------------------------------------

#Main driving function, calls calculation/plotting functions based on args
def main(args):
    trigEffsPerMass(args)

# -----------------------------------------------------------------------------------------------------------------------------

def trigEffsPerMass(args):

    canv = None
    canv = TCanvas("canv", "Trigger Efficiencies Per Taustar Mass", 800, 800)
    #if len(args.triggers) == 1:
    #    canv = TCanvas("canv", "Trigger Efficiencies Per Taustar Mass", 800, 800)
    #elif len(args.triggers) < 2:
    #    canv = TCanvas("canv", "Trigger Efficiencies Per Taustar Mass", 1200, 800)
    #else:
    #    canv = TCanvas("canv", "Trigger Efficiencies Per Taustar Mass", 1200, 1000)
        
    gStyle.SetOptStat(0)

    #For now, base cuts use gen info and just require z->ee/mumu/had + etau/mutau/tautau
    baseCuts = "Gen_isCand"

    #graphs = {}
    print("\nTrigger efficiencies:")
    print("year : mass : trigger : nPassing : nTotal : efficiency")
    for trigN, trigger in enumerate(args.triggers):
        #graphs[trigN] = []
    
        #if trigger == "(HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg||HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1||HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1)":
        #   triggerName = "tau2018"
            #trigger = "((HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg && Gen_tsTauDM == && Gen_tauDM == 0 && GenPart[Gen_tsTauIdx].pt > 40 && GenPart[Gen_tsTauIdx].eta < 2.1 && GenPart[Gen_tauIdx].pt > 40 && GenPart[Gen_tauIdx].eta < 2.1)"
            #trigger += " && (HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1 && ((Gen_tsTauDM == 0 && Gen_tauDM == 0) || (Gen_tsTauDM == 0 && Gen_tauDM == 0)) )"
        # if trigger in trig_run2_gen.keys():
        #     triggerName = trigger
        #     trigger = trig_run2_gen[triggerName]
        # elif trigger in trig_run3_gen.keys():
        #     triggerName = trigger
        #     trigger = trig_run3_gen[triggerName]
        
        # else:
        #     triggerName = trigger
        
        for year in args.years:
            intMasses = []
            efficiencies = []
            for mass in args.masses:
                intMasses.append(int(mass))

                inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
                if inFile == "None":
                    print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                    continue
                tree = inFile.Get("Events")
                denEvents = tree.GetEntries(baseCuts)
                efficiencies.append(tree.GetEntries(baseCuts + " && " + trigger))
                print(year + " : " + mass + " : " + trigger + " : " + str(efficiencies[-1]) + " : " + str(denEvents) + " : " + str(round(efficiencies[-1]/float(denEvents), 2)))
                efficiencies[-1] /= float(denEvents)

                inFile.Close()
            
            graph = TGraph(len(intMasses), array("f", intMasses), array("f", efficiencies))
            graph.SetTitle(year+" : " + trigger + ";Taustar Mass [GeV]; Overall Efficiency")
            graph.SetMaximum(1.0)
            graph.SetMinimum(0.0)
            graph.SetMarkerStyle(5)
            graph.SetMarkerSize(3)

            #graphs[trigN].append(graph)

            #if len(args.triggers) == 1:
            canv.cd()
            graph.Draw("AP")
            canv.Update()
            
            if not args.nP:
                wait = input("Hit ENTER to continue...")
            canv.SaveAs("Plots/TrigPlots/effPerMass_"+ year + "_" + trigger + ".png")


    #if len(args.triggers) > 1:
    #   for trigN, trigger in enumerate(args.triggers):
            

# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    main(args)
