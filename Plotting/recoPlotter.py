

from ROOT import TCanvas, TH1F, TFile, gStyle, TLegend, THStack, gPad
import os
import sys
import argparse

sys.path.append("../Framework/")
import Colors as cols

def parseArgs():
    argparser = argparse.ArgumentParser(description="Script to plot GEN-level variables")
    argparser.add_argument("-i", "--inDir", required=True, action="store", help="A directory to find the input root files")
    argparser.add_argument("-d", "--decay", required=True, choices=["Z", "W"], help="The particle to plot/calculate RECO related params for")
    argparser.add_argument("-p", "--palette",choices=cols.getPalettes(), help="A palette to use for plotting")
    argparser.add_argument("-m", "--masses", type=str, choices = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"], action="append", help = "Which signal masses to plot")
    argparser.add_argument("-y", "--years", choices=["ALL", "2018"], default="ALL")

    args = argparser.parse_args()

    if not args.masses:
        args.masses = ["250", "1000", "3000", "5000"]

    if args.years == "ALL":
        args.years = ["2018"] #TODO Update this as more years are processed

    return args

def main(args):
    if args.decay == "Z":
        calcRecoZEffs(args)

def calcRecoZEffs(args):

    nElDecays = 0
    elDecaysMatch = 0
    nMuDecays = 0
    muDecaysMatch = 0
    nTauDecays = 0
    tauDecaysMatch = 0
    nHadDecays = 0
    hadDecaysMatch = 0
    elD1DecaysMatch = 0
    muD1DecaysMatch = 0
    tauD1DecaysMatch = 0
    elD2DecaysMatch = 0
    muD2DecaysMatch = 0
    tauD2DecaysMatch = 0
    hadDecaysMatch_dt = 0
    hadDecaysMatch_pn = 0
    nElCorrectReco = 0
    nMuCorrectReco = 0
    nTauCorrectReco = 0

    for mass in args.masses:

        for year in args.years:
            inFile = TFile.Open(args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root", "READ")
            if inFile == "None":
                print("ERROR: Could not read file " + args.inDir + "/taustarToTauZ_m"+mass+"_"+year+".root")
                continue
            tree = inFile.Get("Events")

            #Do some efficiency calculations
            print("Parameters for Z reconstruction:")

            nHadDecays += tree.GetEntries("Gen_zDM==0")
            nElDecays += tree.GetEntries("Gen_zDM==1")
            nMuDecays += tree.GetEntries("Gen_zDM==2")
            nTauDecays += tree.GetEntries("Gen_zDM==3")
            hadDecaysMatch += tree.GetEntries("Gen_zDM==0 && Z_dm==0")
            elDecaysMatch += tree.GetEntries("Gen_zDM==1 && Z_dm==1")
            muDecaysMatch += tree.GetEntries("Gen_zDM==2 && Z_dm==2")
            tauDecaysMatch += tree.GetEntries("Gen_zDM==3 && Z_dm==3")

            hadDecaysMatch_pn += tree.GetEntries("Z_jetIdxPN > 0 && Gen_zDM==0 && Z_dm==0 && FatJet_genJetAK8Idx[Z_jetIdxPN]==Gen_zGenAK8Idx")
            hadDecaysMatch_dt += tree.GetEntries("Z_jetIdxDT > 0 && Gen_zDM==0 && Z_dm==0 && FatJet_genJetAK8Idx[Z_jetIdxDT]==Gen_zGenAK8Idx")

            elD1DecaysMatch += tree.GetEntries("Gen_zDM==1 && Z_dm==1 && Electron_genPartIdx[Z_d1Idx]==Gen_zDau1Idx")
            muD1DecaysMatch += tree.GetEntries("Gen_zDM==2 && Z_dm==2 && Muon_genPartIdx[Z_d1Idx]==Gen_zDau1Idx")
            tauD1DecaysMatch += tree.GetEntries("Gen_zDM==3 && Z_dm==3 && Tau_genPartIdx[Z_d1Idx]==Gen_zDau1Idx")
            elD2DecaysMatch += tree.GetEntries("Gen_zDM==1 && Z_dm==1 && Electron_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")
            muD2DecaysMatch += tree.GetEntries("Gen_zDM==2 && Z_dm==2 && Muon_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")
            tauD2DecaysMatch += tree.GetEntries("Gen_zDM==3 && Z_dm==3 && Tau_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")

            nElCorrectReco +=  tree.GetEntries("Gen_zDM==1 && Z_dm==1 && Electron_genPartIdx[Z_d1Idx]==Gen_zDau1Idx && Electron_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")
            nMuCorrectReco += tree.GetEntries("Gen_zDM==2 && Z_dm==2 && Muon_genPartIdx[Z_d1Idx]==Gen_zDau1Idx && Muon_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")
            nTauCorrectReco += tree.GetEntries("Gen_zDM==3 && Z_dm==3 && Tau_genPartIdx[Z_d1Idx]==Gen_zDau1Idx && Tau_genPartIdx[Z_d2Idx]==Gen_zDau2Idx")

    print("\n=============  Z RECO parameters: =============")
    print("years = " + str(args.years))
    print("masses = " + str(args.masses))
    print("----------------- Z->ee -----------------------")
    print("Num Events (MC Truth): " + str(nElDecays))
    print("Decay mode choice eff: {:.2f}%".format(float(elDecaysMatch) / nElDecays * 100.0))
    print("Daughter 1 match eff:  {:.2f}%".format(float(elD1DecaysMatch) / elDecaysMatch * 100.0))
    print("Daughter 2 match eff:  {:.2f}%".format(float(elD2DecaysMatch) / elDecaysMatch * 100.0))
    print("Total Z->ee reco eff:  {:.2f}%".format(float(nElCorrectReco) / nElDecays * 100.0)) 
    print("---------------- Z->mumu ----------------------")
    print("Num Events (MC Truth): " + str(nMuDecays))
    print("Decay mode choice eff: {:.2f}%".format(float(muDecaysMatch) / nMuDecays * 100.0))
    print("Daughter 1 match eff:  {:.2f}%".format(float(muD1DecaysMatch) / muDecaysMatch * 100.0))
    print("Daughter 2 match eff:  {:.2f}%".format(float(muD2DecaysMatch) / muDecaysMatch * 100.0))
    print("Total Z->mumu reco eff: {:.2f}%".format(float(nMuCorrectReco) / nMuDecays * 100.0)) 
    #print("--------------- Z->tautau ---------------------")
    #print("Num Events (MC Truth): {:.2f}%" + str(nTauDecays))
    #print("Decay mode choice eff: {:.2f}%" + str(tauDecaysMatch / nTauDecays))
    #print("Daughter 1 match eff:  {:.2f}%" + str(tauD1DecaysMatch / tauDecaysMatch))
    #print("Daughter 2 match eff:  {:.2f}%" + str(tauD2DecaysMatch / tauDecaysMatch))
    #print("Total Z->ee reco eff:  {:.2f}%" + str(nTauCorrectReco / nTauDecays)) 
    print("----------------- Z->jets -----------------------")
    print("Num Events (MC Truth): " + str(nHadDecays))
    print("Decay mode choice eff: {:.2f}%".format(float(hadDecaysMatch) / nHadDecays * 100.0))
    print("ParticleNet match eff:  {:.2f}%".format(float(hadDecaysMatch_pn) / hadDecaysMatch * 100.0))
    print("DeepBoostedJet match eff:  {:.2f}%".format(float(hadDecaysMatch_dt) / hadDecaysMatch * 100.0))
    
    print("=================================================\n")

if __name__ == "__main__":
    args = parseArgs()
    main(args)