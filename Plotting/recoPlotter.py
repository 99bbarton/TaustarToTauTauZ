

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gROOT, TGraph, PyConfig
PyConfig.IgnoreCommandLineOptions = True
import os
import sys
import argparse
from array import array

sys.path.append("../Framework/")
import Colors as cols


# -----------------------------------------------------------------------------------------------------------------------------

#Take in command line arguments and return a dictionary of settings to use for calculations/plotting
def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot reco related variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-d", "--decay", required=False, choices=["Z", "W"], default="Z", help="The particle to plot/calculate RECO related params for")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], action="append", help = "Which signal masses to plot")
    argparser.add_argument("-y", "--years", required=True, choices=["ALL", "2015","2016", "2017", "2018","RUN2", "2022post", "2022", "2023post", "2023", "RUN3"], type=str, action="append")
    argparser.add_argument("-n", "--noPlot", action="store_true", help="If specified, will skip the plot making step and just print the table")
    argparser.add_argument("--zDauID", action="store_true", help="If specified, will require Z_dauID to be True." )

    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"]

    #TODO Update this as more years are processed
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
    if args.decay == "Z":
        recoEffs_Z(args)

# -----------------------------------------------------------------------------------------------------------------------------

#Calculate the Z RECO efficiency for each decay mode using MCTruth info from GenProducerTauZ.py and RECO info from ZProducer.py
def recoEffs_Z(args):
  
    
    nElDecays = []
    nEls = []
    nEE = []
    elDecaysMatch = []
    nMuDecays = []
    nMuMu = []
    muDecaysMatch = []
    nEE_MuMu = []
    nTauDecays = []
    tauDecaysMatch = []
    nHadDecays = []
    hadDecaysMatch = []
    elD1DecaysMatch = []
    muD1DecaysMatch = []
    tauD1DecaysMatch = []
    elD2DecaysMatch = []
    muD2DecaysMatch = []
    tauD2DecaysMatch = []
    hadDecaysMatch_dt = []
    hadDecaysMatch_pn = []
    nElCorrectReco = []
    nMuCorrectReco = []
    nTauCorrectReco = []

    effs_ee = []
    effs_mumu = []
    effs_tautau = []
    effs_had_pn = []
    effs_had_dt = []
    
    
    for mass in args.masses:
        nElDecays.append(0)
        nEE.append(0)
        nEls.append(0)
        elDecaysMatch.append(0)
        nMuDecays.append(0)
        nMuMu.append(0)
        muDecaysMatch.append(0)
        nEE_MuMu.append(0)
        nTauDecays.append(0)
        tauDecaysMatch.append(0)
        nHadDecays.append(0)
        hadDecaysMatch.append(0)
        elD1DecaysMatch.append(0)
        muD1DecaysMatch.append(0)
        tauD1DecaysMatch.append(0)
        elD2DecaysMatch.append(0)
        muD2DecaysMatch.append(0)
        tauD2DecaysMatch.append(0)
        hadDecaysMatch_dt.append(0)
        hadDecaysMatch_pn.append(0)
        nElCorrectReco.append(0)
        nMuCorrectReco.append(0)
        nTauCorrectReco.append(0)


        if args.zDauID:
            zDauID = " && Z_dauID"
            #zDauID = " && Muon_looseId[Z_d1Idx] && Muon_looseId[Z_d2Idx]"
        else:
            zDauID = ""
        
        for year in args.years:
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            #Do some efficiency calculations
            #print("Parameters for Z reconstruction:")
            
            nHadDecays[-1] += tree.GetEntries("Gen_zDM==0 && Gen_isCand")
            nElDecays[-1] += tree.GetEntries("Gen_zDM==1 && Gen_isCand")
            nMuDecays[-1] += tree.GetEntries("Gen_zDM==2 && Gen_isCand")
            nTauDecays[-1] += tree.GetEntries("Gen_zDM==3 && Gen_isCand")
            nEE[-1] += tree.GetEntries("Z_nEE>=1")
            nEls[-1] += tree.GetEntries("nElectron>=2")
            nMuMu[-1] += tree.GetEntries("Z_nMuMu>=1")
            nEE_MuMu[-1] += tree.GetEntries("Z_nEE>=1 && Z_nMuMu>=1")
            hadDecaysMatch[-1] += tree.GetEntries("Gen_zDM==0 && Z_dm==0")
            elDecaysMatch[-1] += tree.GetEntries("Gen_zDM==1 && Gen_isCand && Z_dm==1" + zDauID)
            muDecaysMatch[-1] += tree.GetEntries("Gen_zDM==2 && Gen_isCand && Z_dm==2" + zDauID)
            #tauDecaysMatch[-1] += tree.GetEntries("Gen_zDM==3 && Gen_isCand && Z_dm==3")

            hadDecaysMatch_pn[-1] += tree.GetEntries("Z_jetIdxPN > 0 && Gen_zDM==0 && Gen_isCand && Z_dm==0 && FatJet_genJetAK8Idx[Z_jetIdxPN]==Gen_zGenAK8Idx")
            #hadDecaysMatch_dt[-1] += tree.GetEntries("Z_jetIdxDT > 0 && Gen_zDM==0 && Gen_isCand && Z_dm==0 && FatJet_genJetAK8Idx[Z_jetIdxDT]==Gen_zGenAK8Idx")

            elD1DecaysMatch[-1] += tree.GetEntries("Gen_zDM==1 && Gen_isCand && Z_dm==1 && Z_d1Idx==Gen_zD1RecIdx" + zDauID)
            muD1DecaysMatch[-1] += tree.GetEntries("Gen_zDM==2 && Gen_isCand && Z_dm==2 && Z_d1Idx==Gen_zD1RecIdx" + zDauID)
            #tauD1DecaysMatch[-1] += tree.GetEntries("Gen_zDM==3 && Gen_isCand && Z_dm==3 && Z_d1Idx==Gen_zD1RecIdx")
            elD2DecaysMatch[-1] += tree.GetEntries("Gen_zDM==1 && Gen_isCand && Z_dm==1 && Z_d2Idx==Gen_zD2RecIdx" + zDauID)
            muD2DecaysMatch[-1] += tree.GetEntries("Gen_zDM==2 && Gen_isCand && Z_dm==2 && Z_d2Idx==Gen_zD2RecIdx" + zDauID)
            #tauD2DecaysMatch[-1] += tree.GetEntries("Gen_zDM==3 && Gen_isCand && Z_dm==3 && Z_d2Idx==Gen_zD2RecIdx")

            nElCorrectReco[-1] += tree.GetEntries("Gen_zDM==1 && Gen_isCand && Z_dm==1 && Z_d1Idx==Gen_zD1RecIdx && Z_d2Idx==Gen_zD2RecIdx" + zDauID)
            nMuCorrectReco[-1] += tree.GetEntries("Gen_zDM==2 && Gen_isCand && Z_dm==2 && Z_d1Idx==Gen_zD1RecIdx && Z_d2Idx==Gen_zD2RecIdx" + zDauID)
            #nTauCorrectReco[-1] += tree.GetEntries("Gen_zDM==3 && Gen_isCand && Z_dm==3 && Z_d1Idx==Gen_zD1RecIdx && Z_d2Idx==Gen_zD2RecIdx")

        effs_ee.append(float(nElCorrectReco[-1]) / nElDecays[-1] * 100.0)
        effs_mumu.append(float(nMuCorrectReco[-1]) / nMuDecays[-1] * 100.0)
        #effs_tautau.append(float(nTauCorrectReco[-1]) / nTauDecays[-1])
        effs_had_pn.append(float(hadDecaysMatch_pn[-1]) / hadDecaysMatch[-1] * 100.0)
        effs_had_dt.append(float(hadDecaysMatch_dt[-1]) / hadDecaysMatch[-1] * 100.0)

    #Print out is done for masses * years cumulative
    print("\n=============  Z RECO parameters: =============")
    print("years = " + str(args.years))
    print("mass = " + str(args.masses))
    print("----------------- Z->ee -----------------------")
    print("Num Events (MC Truth)     : " + str(nElDecays))
    
    print("Num Events with Z_nEE >=1 : " + str(nEE) )
    print("Decay mode choice eff: {:.2f}%".format(float(sum(elDecaysMatch)) / sum(nElDecays) * 100.0))
    print("Daughter 1 match eff:  {:.2f}%".format(float(sum(elD1DecaysMatch)) / sum(elDecaysMatch) * 100.0))
    print("Daughter 2 match eff:  {:.2f}%".format(float(sum(elD2DecaysMatch)) / sum(elDecaysMatch) * 100.0))
    print("Total Z->ee reco eff:  {:.2f}%".format(float(sum(nElCorrectReco)) / sum(nElDecays) * 100.0)) 
    print("---------------- Z->mumu ----------------------")
    print("Num Events (MC Truth)       : " + str(nMuDecays))
    print("Num Events with Z_nMuMu >=1 : " + str(nMuMu) )
    print("Decay mode choice eff: {:.2f}%".format(float(sum(muDecaysMatch)) / sum(nMuDecays) * 100.0))
    print("Daughter 1 match eff:  {:.2f}%".format(float(sum(muD1DecaysMatch)) / sum(muDecaysMatch) * 100.0))
    print("Daughter 2 match eff:  {:.2f}%".format(float(sum(muD2DecaysMatch)) / sum(muDecaysMatch) * 100.0))
    print("Total Z->mumu reco eff: {:.2f}%".format(float(sum(nMuCorrectReco)) / sum(nMuDecays) * 100.0))
    print("-----------------------------------------------")
    print("Events with both nEE>=1 and nMuMu>=1: = " + str(nEE_MuMu))
    #print("--------------- Z->tautau ---------------------")
    #print("Num Events (MC Truth): {:.2f}%" + str(nTauDecays))
    #print("Decay mode choice eff: {:.2f}%" + str(tauDecaysMatch / nTauDecays))
    #print("Daughter 1 match eff:  {:.2f}%" + str(tauD1DecaysMatch / tauDecaysMatch))
    #print("Daughter 2 match eff:  {:.2f}%" + str(tauD2DecaysMatch / tauDecaysMatch))
    #print("Total Z->ee reco eff:  {:.2f}%" + str(nTauCorrectReco / nTauDecays)) 
    print("----------------- Z->had -----------------------")
    print("Num Events (MC Truth): " + str(nHadDecays))
    print("Decay mode choice eff: {:.2f}%".format(float(sum(hadDecaysMatch)) / sum(nHadDecays) * 100.0))
    print("ParticleNet match eff:  {:.2f}%".format(float(sum(hadDecaysMatch_pn)) / sum(hadDecaysMatch) * 100.0))
    #print("DeepBoostedJet match eff:  {:.2f}%".format(float(sum(hadDecaysMatch_dt)) / sum(hadDecaysMatch) * 100.0))
    
    print("=================================================\n")
    

    if args.noPlot:
        return 0

    fltMasses = []
    for mass in args.masses:
        fltMasses.append(float(mass))

    nPts = len(fltMasses)
    #Now make plots
    g_ee = TGraph(nPts, array("f", fltMasses), array("f", effs_ee))
    g_mumu = TGraph(nPts, array("f", fltMasses), array("f", effs_mumu))
    #g_tautau = TGraph(nPts, array("f", fltMasses), array("f", effs_tautau))
    g_had_pn = TGraph(nPts, array("f", fltMasses), array("f", effs_had_pn))
    #g_had_dt = TGraph(nPts, array("f", fltMasses), array("f", effs_had_dt))

    g_ee.SetMaximum(105)
    g_mumu.SetMaximum(105)
    #g_tautau.SetMaximum(105)
    g_had_pn.SetMaximum(105)
    #g_had_dt.SetMaximum(105)
    g_ee.SetMinimum(0)
    g_mumu.SetMinimum(0)
    #g_tautau.SetMinimum(0)
    g_had_pn.SetMinimum(0)
    #g_had_dt.SetMinimum(0)

    specTitle = ""
    if len(args.years) == 1:
        specTitle += " " + args.years[0]
    g_ee.SetTitle("RECO Eff" + specTitle + ": Z#rightarrow ee;#tau* Mass [GeV]; Efficiency [%]")
    g_mumu.SetTitle("RECO Eff" + specTitle + ": Z#rightarrow #mu#mu;#tau* Mass [GeV]; Efficiency [%]")
    #g_tautau.SetTitle("RECO Eff" + specTitle + ": Z#rightarrow#tau#tau;#tau* Mass [GeV]; Efficiency [%]")
    g_had_pn.SetTitle("RECO Eff (PN ID)" + specTitle + ": Z#rightarrow had;#tau* Mass [GeV]; Efficiency [%]")
    #g_had_dt.SetTitle("RECO Eff (DT ID)" + specTitle + ": Z#rightarrow had;#tau* Mass [GeV]; Efficiency [%]")

    g_ee.SetMarkerStyle(5)
    g_mumu.SetMarkerStyle(5)
    #g_tautau.SetMarkerStyle(5)
    g_had_pn.SetMarkerStyle(5)
    #g_had_dt.SetMarkerStyle(5)

    g_ee.SetMarkerSize(3)
    g_mumu.SetMarkerSize(3)
    #g_tautau.SetMarkerSize(3)
    g_had_pn.SetMarkerSize(3)
#    g_had_dt.SetMarkerSize(3)

    g_ee.SetLineWidth(2)
    g_mumu.SetLineWidth(2)
    #g_tautau.SetLineWidth(2)
    g_had_pn.SetLineWidth(2)
 #   g_had_dt.SetLineWidth(2)

    drawStyle = "AP"
    gStyle.SetOptStat(0)
    canv = TCanvas("zCanv", "Z RECO Plots", 1800, 1000)
    canv.Divide(2,2)
    canv.cd(1)
    g_ee.Draw(drawStyle)
    canv.cd(2)
    g_mumu.Draw(drawStyle)
    canv.cd(3)
    #g_tautau.Draw(drawStyle)
    #canv.cd(4)
    g_had_pn.Draw(drawStyle)
   # canv.cd(4)
    #canv.cd(5)
  #  g_had_dt.Draw(drawStyle)

    resp = input("Hit ENTER to save and close plot... ")
    canv.SaveAs("Plots/recoEffs_Z.png")

    
    #END calRecoEffs_Z

# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = parseArgs()
    main(args)
