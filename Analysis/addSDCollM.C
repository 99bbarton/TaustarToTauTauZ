/*Macro to add min and max collinear mass branches calculated usinto pre-processed nanoAOD trees


*/

#include <TString>
#include <TFile>
#include <TTree>
#include <TBranch>
#include <TLorentzVector>
#include <TMath>

#include <vector>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <string>


void procMultFiles(string dirpath, string filelist);
void addSDCollM(TString filename);
void calcCollM(TLorentzVector& tau1, TLorentzVector& tau2, TLorentzVector& theZ, TLorentzVector& MET, float* minCM, float* maxCM);


void procMultFiles(string dirpath, string filelist)
{
    if (dirpath.compare(0, 6, "/store") == 0)  
        dirpath = "root://cmsxrootd.fnal.gov/" + dirpath;

    std::ifstream file(filelist);
    if (!file.is_open()) {
        std::cerr << "ERROR: Could not open the filelist." << std::endl;
        return 1;
    }

    TString filename;
    std:string line;
    while (std:getline(file, line))
    {
        std::cout << "Processing file: " << line << std:endl;
        filename = dirpath + "/" + line;
        addSDCollM(TString(filename));
    }

    file.close();
}

void addSDCollM(TString filename)
{
    TFile* file = TFile::Open(filename, "UPDATE");
    TTree* tree = (TTree*) file->Get("Events");
    if (tree == NULL)
        {
            cout << "File " << filename << " could not be read or does not contain a readable tree" << endl;
            exit(-1);
        }

    float minCollM_SD, maxCollM_SD;

    TBranch* b_minCollM_SD = tree->Branch("SDCM_min", minCollM_SD, "SDCM_min/F");
    TBranch* b_maxCollM_SD = tree->Branch("SDCM_max", maxCollM_SD, "SDCM_max/F");

    bool eTauCand, muTauCand, tautauCand;
    int zIdx, eIdx, muIdx, eTauIdx, muTauIdx, tau1Idx, tau2Idx; 
    float Z_pt, Z_eta, Z_phi, Z_mass;
    int Z_dm, Z_jetIdxAK8;
    float MET_pt, MET_eta, MET_phi; 
    vector<float> elPts, elEtas, elPhis;
    vector<float> muPts, muEtas, muPhis;
    vector<float> tauPts, tauEtas, tauPhis;
    vector<float> sdMasses;

    /*
    tree->SetBranchStatus("*", false);
    tree->SetBranchStatus("ETau_isCand", true);
    tree->SetBranchStatus("ETau_eIdx", true);;
    tree->SetBranchStatus("ETau_tauIdx", true);
    tree->SetBranchStatus("MuTau_isCand", true);
    tree->SetBranchStatus("MuTau_muIdx", true);
    tree->SetBranchStatus("MuTau_tauIdx", true);
    tree->SetBranchStatus("TauTau_isCand", true);
    tree->SetBranchStatus("TauTau_tau1Idx", true);
    tree->SetBranchStatus("TauTau_tau2Idx", true);
    tree->SetBranchStatus("Z_pt", true);
    tree->SetBranchStatus("Z_eta", true);
    tree->SetBranchStatus("Z_phi", true);
    tree->SetBranchStatus("Z_mass", true);
    tree->SetBranchStatus("Z_dm", true);
    tree->SetBranchStatus("MET_pt", true);
    tree->SetBranchStatus("MET_eta", true);
    tree->SetBranchStatus("MET_phi", true);
    tree->SetBranchStatus("Electron_pt", true);
    tree->SetBranchStatus("Electron_eta", true);
    tree->SetBranchStatus("Electron_phi", true);
    tree->SetBranchStatus("Muon_pt", true);
    tree->SetBranchStatus("Muon_eta", true);
    tree->SetBranchStatus("Muon_phi", true);
    tree->SetBranchStatus("Tau_pt", true);
    tree->SetBranchStatus("Tau_eta", true);
    tree->SetBranchStatus("Tau_phi", true);
    tree->SetBranchStatus("FatJet_msoftdrop", true);
    */

    tree->SetBranchAddress("ETau_isCand", &eTauCand);
    tree->SetBranchAddress("ETau_eIdx", &eIdx);
    tree->SetBranchAddress("ETau_tauIdx", &eTauIdx);
    tree->SetBranchAddress("MuTau_isCand", &muTauCand);
    tree->SetBranchAddress("MuTau_muIdx", &muIdx);
    tree->SetBranchAddress("MuTau_tauIdx", &muTauIdx);
    tree->SetBranchAddress("TauTau_isCand", &tauTauCand);
    tree->SetBranchAddress("TauTau_tau1Idx", &tau1Idx);
    tree->SetBranchAddress("TauTau_tau2Idx", &tau2Idx);
    tree->SetBranchAddress("Z_pt", &Z_pt);
    tree->SetBranchAddress("Z_eta", &Z_eta);
    tree->SetBranchAddress("Z_phi", &Z_phi);
    tree->SetBranchAddress("Z_mass", &Z_mass);
    tree->SetBranchAddress("Z_dm", &Z_dm);
    tree->SetBranchAddress("MET_pt", &MET_pt);
    tree->SetBranchAddress("MET_eta", &MET_eta);
    tree->SetBranchAddress("MET_phi", &MET_phi);
    tree->SetBranchAddress("Electron_pt", &elPts);
    tree->SetBranchAddress("Electron_eta", &elEtas);
    tree->SetBranchAddress("Electron_phi", &elPhis);
    tree->SetBranchAddress("Muon_pt", &muPts);
    tree->SetBranchAddress("Muon_eta", &muEtas);
    tree->SetBranchAddress("Muon_phi", &muPhis);
    tree->SetBranchAddress("Tau_pt", &tauPts);
    tree->SetBranchAddress("Tau_eta", &tauEtas);
    tree->SetBranchAddress("Tau_phi", &tauPhis);
    tree->SetBranchAddress("FatJet_msoftdrop", &sdMasses);

    int nEntries = tree->GetEntries();
    for (int entryN = 0; entryN < nEntries; entryN++)
    {
        tree->GetEntry(entryN);

        TLorentzVector theZ;
        if (Z_dm == 0)
            theZ.SetPtEtaPhiM(Z_pt, Z_eta, Z_phi, sdMasses.at(Z_jetIdxAK8));
        else
            theZ.SetPtEtaPhiM(Z_pt, Z_eta, Z_phi, Z_mass);

        TLorentzVector met;
        met.SetPtEtaPhiM(MET_pt, MET_eta, MET_phi, 0);

        if (eTauCand)
        {
            TLorentzVector theEl;
            theEl.SetPtEtaPhiM(elPts.at(eIdx), elEtas.at(eIdx), elPhis.at(eIdx), 0.000511);

            TLorentzVector theTau;
            theTau.SetPtEtaPhiM(tauPts.at(eTauIdx), tauEtas.at(eTauIdx), tauPhis.at(eTauIdx), 1.777);

            calcCollM(theTau, theEl, theZ, MET, &minCollM_SD, &maxCollM_SD);
        }
        else if (muTauCand)
        {
            TLorentzVector theMu;
            theMu.SetPtEtaPhiM(muPts.at(muIdx), muEtas.at(muIdx), muPhis.at(muIdx), 0.1057);

            TLorentzVector theTau;
            theTau.SetPtEtaPhiM(tauPts.at(muTauIdx), tauEtas.at(muTauIdx), tauPhis.at(muTauIdx), 1.777);

            calcCollM(theTau, theMu, theZ, MET, &minCollM_SD, &maxCollM_SD);
        }
        else if (tauTauCand)
        {
            TLorentzVector tau2;
            tau2.SetPtEtaPhiM(tauPts.at(tau2Idx), tauEtas.at(tau2Idx), tauPhis.at(tau2Idx), 1.777);

            TLorentzVector tau1;
            tau1.SetPtEtaPhiM(tauPts.at(tau1Idx), tauEtas.at(tau1Idx), tauPhis.at(tau1Idx), 1.777);

            calcCollM(tau1, tau2, theZ, MET, &minCollM_SD, &maxCollM_SD);
        } 
        else
            continue;
    }

    //TODO fill and write branches and close file
    b_minCollM_SD->Fill();
    b_maxCollM_SD->Fill();

    tree->Write("", TObject::kOverwrite); // save only the new version of the tree
    file->Close();

}


void calcCollM(TLorentzVector& tau1, TLorentzVector& tau2, TLorentzVector& theZ, TLorentzVector& MET, float* minCM, float* maxCM)
{
    float cos_nuTau1_MET = TMath::cos(tau1.DeltaPhi(MET));
    float cos_nuTau2_MET = TMath::cos(tau2.DeltaPhi(MET));
    float cos_tau1_tau2 = TMath::cos(tau1.DeltaPhi(tau2));
    float cos_tau1_tau2_sqrd = cos_tau1_tau2 * cos_tau1_tau2;
    
    if (cos_tau1_tau2_sqrd > 0.999)
        cos_tau1_tau2_sqrd = 0.999;
    
    TLorentzVector nuTau1;
    nuTau1Mag = MET.PT() * (cos_nuTau1_MET - (cos_nuTau2_MET * cos_tau1_tau2)) / (1. - cos_tau1_tau2_sqrd);
    nuTau1.SetPtEtaPhiM(nuTau1_mag, tau1.eta, tau1.phi, 0.);

    TLorentzVector nuTau2;
    nuTau2_mag = ((MET.PT() * cos_nuTau1_MET) - nuTau1_mag) / cos_tau1_tau2;
    nuTau2.SetPtEtaPhiM(nuTau2_mag, tau2.eta, tau2.phi, 0.);
    
    float collM_tau1Z = (tau1 + nuTau1 + theZ).M();
    float collM_tau2Z = (tau2 + nuTau2 + theZ).M();

    *minCM = std::min(collM_tau1Z, collM_tau2Z);
    *maxCM = std::max(collM_tau1Z, collM_tau2Z);
}