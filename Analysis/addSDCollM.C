/*Macro to add min and max collinear mass branches calculated usinto pre-processed nanoAOD trees


*/

#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TLorentzVector.h"
#include "TMath.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"

#include <vector>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <string>


int procMultFiles(string dirpath, string filelist);
void addSDCollM(TString filename);
void calcCollM(TLorentzVector& tau1, TLorentzVector& tau2, TLorentzVector& theZ, TLorentzVector& MET, float* minCM, float* maxCM);


int procMultFiles(string dirpath, string filelist)
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
    while (std::getline(file, line))
    {
        std::cout << "Processing file: " << line << std::endl;
        filename = dirpath + "/" + line;
        addSDCollM(TString(filename));
    }

    file.close();
    return 0;
}

void addSDCollM(TString filename)
{
    TFile *file = TFile::Open(filename, "UPDATE");
    if (!file || file->IsZombie()) {
        std::cout << "Couldn't open " << filename << std::endl;
        return;
    }

    TTree *tree = (TTree*)file->Get("Events");
    if (!tree) {
        std::cout << "Couldn't find Events tree." << std::endl;
        file->Close();
        return;
    }

    float minCollM_SD = -999.99;
    float maxCollM_SD = -999.99;
    TBranch *b_minCollM_SD = tree->Branch("SDCM_min",&minCollM_SD,"SDCM_min/F");
    TBranch *b_maxCollM_SD = tree->Branch("SDCM_max",&maxCollM_SD,"SDCM_max/F");

    TTreeReader reader(tree);
    TTreeReaderValue<bool> eTauCand(reader,"ETau_isCand");
    TTreeReaderValue<int> eIdx(reader,"ETau_eIdx");
    TTreeReaderArray<float> Electron_pt(reader,"Electron_pt");
    TTreeReaderArray<float> Electron_eta(reader,"Electron_eta");
    TTreeReaderArray<float> Electron_phi(reader,"Electron_phi");
    TTreeReaderValue<int> eTauIdx(reader,"ETau_tauIdx");
    TTreeReaderValue<bool> muTauCand(reader,"MuTau_isCand");
    TTreeReaderValue<int> muIdx(reader,"MuTau_muIdx");
    TTreeReaderValue<int> muTauIdx(reader,"MuTau_tauIdx");
    TTreeReaderArray<float> Muon_pt(reader,"Muon_pt");
    TTreeReaderArray<float> Muon_eta(reader,"Muon_eta");
    TTreeReaderArray<float> Muon_phi(reader,"Muon_phi");
    TTreeReaderValue<bool> tauTauCand(reader,"TauTau_isCand");
    TTreeReaderValue<int> tau1Idx(reader,"TauTau_tau1Idx");
    TTreeReaderValue<int> tau2Idx(reader,"TauTau_tau2Idx");
    TTreeReaderArray<float> Tau_pt(reader,"Tau_pt");
    TTreeReaderArray<float> Tau_eta(reader,"Tau_eta");
    TTreeReaderArray<float> Tau_phi(reader,"Tau_phi");
    TTreeReaderValue<float> Z_pt(reader,"Z_pt");
    TTreeReaderValue<float> Z_eta(reader,"Z_eta");
    TTreeReaderValue<float> Z_phi(reader,"Z_phi");
    TTreeReaderValue<float> Z_mass(reader,"Z_mass");
    TTreeReaderValue<int> Z_dm(reader,"Z_dm");
    TTreeReaderValue<int> Z_jetIdxAK8(reader,"Z_jetIdxAK8");
    TTreeReaderValue<float> MET_pt(reader,"MET_pt");
    TTreeReaderValue<float> MET_phi(reader,"MET_phi");
    TTreeReaderArray<float> FatJet_msoftdrop(reader,"FatJet_msoftdrop");


    while (reader.Next())
    {
        minCollM_SD = -999.99;
        maxCollM_SD = -999.99;

        TLorentzVector theZ;

        if (*Z_dm == 0)
        {
            if (*Z_jetIdxAK8 < 0 || *Z_jetIdxAK8 >= (int)FatJet_msoftdrop.GetSize())
            {
                b_minCollM_SD->Fill();
                b_maxCollM_SD->Fill();
                continue;
            }

            theZ.SetPtEtaPhiM(*Z_pt, *Z_eta, *Z_phi, FatJet_msoftdrop[*Z_jetIdxAK8]);
        }
        else if (*Z_dm == 1 || *Z_dm == 2)
        {
            theZ.SetPtEtaPhiM(*Z_pt, *Z_eta, *Z_phi, *Z_mass);
        }
        else
        {
            b_minCollM_SD->Fill();
            b_maxCollM_SD->Fill();
            continue;
        }

        TLorentzVector met;
        met.SetPtEtaPhiM(*MET_pt,0.,*MET_phi,0.);

        if (*eTauCand)
        {
            TLorentzVector el;
            el.SetPtEtaPhiM(Electron_pt[*eIdx], Electron_eta[*eIdx], Electron_phi[*eIdx], 0.000511);

            TLorentzVector tau;
            tau.SetPtEtaPhiM(Tau_pt[*eTauIdx], Tau_eta[*eTauIdx], Tau_phi[*eTauIdx], 1.777);

            calcCollM(tau, el, theZ, met, &minCollM_SD, &maxCollM_SD);
        }
        else if (*muTauCand)
        {
            TLorentzVector mu;
            mu.SetPtEtaPhiM(Muon_pt[*muIdx], Muon_eta[*muIdx], Muon_phi[*muIdx], 0.1057);

            TLorentzVector tau;
            tau.SetPtEtaPhiM(Tau_pt[*muTauIdx], Tau_eta[*muTauIdx], Tau_phi[*muTauIdx], 1.777);

            calcCollM(tau, mu, theZ, met, &minCollM_SD, &maxCollM_SD);
        }
        else if (*tauTauCand)
        {
            TLorentzVector tau1;
            tau1.SetPtEtaPhiM(Tau_pt[*tau1Idx], Tau_eta[*tau1Idx], Tau_phi[*tau1Idx], 1.777);

            TLorentzVector tau2;
            tau2.SetPtEtaPhiM(Tau_pt[*tau2Idx], Tau_eta[*tau2Idx], Tau_phi[*tau2Idx], 1.777);

            calcCollM(tau1, tau2, theZ, met, &minCollM_SD, &maxCollM_SD);
        }

        b_minCollM_SD->Fill();
        b_maxCollM_SD->Fill();
    }

    tree->Write("", TObject::kOverwrite);
    file->Close();
}

void calcCollM(TLorentzVector& tau1, TLorentzVector& tau2, TLorentzVector& theZ, TLorentzVector& MET, float* minCM, float* maxCM)
{
    float cos_nuTau1_MET = TMath::Cos(tau1.DeltaPhi(MET));
    float cos_nuTau2_MET = TMath::Cos(tau2.DeltaPhi(MET));
    float cos_tau1_tau2 = TMath::Cos(tau1.DeltaPhi(tau2));
    float cos_tau1_tau2_sqrd = cos_tau1_tau2 * cos_tau1_tau2;
    
    if (cos_tau1_tau2_sqrd > 0.999)
        cos_tau1_tau2_sqrd = 0.999;
    
    TLorentzVector nuTau1;
    float nuTau1Mag = MET.Pt() * (cos_nuTau1_MET - (cos_nuTau2_MET * cos_tau1_tau2)) / (1. - cos_tau1_tau2_sqrd);
    nuTau1.SetPtEtaPhiM(nuTau1Mag, tau1.Eta(), tau1.Phi(), 0.);

    TLorentzVector nuTau2;
    float nuTau2Mag = ((MET.Pt() * cos_nuTau1_MET) - nuTau1Mag) / cos_tau1_tau2;
    nuTau2.SetPtEtaPhiM(nuTau2Mag, tau2.Eta(), tau2.Phi(), 0.);
    
    float collM_tau1Z = (tau1 + nuTau1 + theZ).M();
    float collM_tau2Z = (tau2 + nuTau2 + theZ).M();

    *minCM = std::min(collM_tau1Z, collM_tau2Z);
    *maxCM = std::max(collM_tau1Z, collM_tau2Z);
}
