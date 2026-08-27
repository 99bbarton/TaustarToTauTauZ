//Print the details of events passing selection criteria

#include "TFile.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"

#include <fstream>

int procFiles(string dirpath, string filelist);
void printSelEvents(TString filename);


int procFiles(string dirpath, string filelist)
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
        printSelEvents(TString(filename));
    }

    file.close();
    return 0;
}

void printSelEvents(TString filename)
{
    TFile *file = TFile::Open(filename, "READ");
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
    TTreeReader reader(tree);

    int nMasses = 9;
    float masses[9] = {500.0, 750.0, 1000.0, 1250.0, 1500.0, 1750.0, 2000.0, 2500.0, 2500.0};
    float minBounds[9] = {420.0, 620.0, 700.0, 1000.0, 1300.0, 1500.0, 1700.0, 1700.0, 1700.0};
    float maxBounds[9] = {650.0, 975.0, 1300.0, 1600.0, 2250.0, 2500.0, 3000.0, 3000.0, 3200.0};


    TTreeReaderArray<bool> eTauCand(reader,"ETau_isCand");
    TTreeReaderArray<float> eTauMinCollM(reader,"ETau_minCollM");
    TTreeReaderArray<float> eTauMaxCollM(reader,"ETau_maxCollM");
    TTreeReaderArray<int> eTauSign(reader,"ETau_sign");
    TTreeReaderArray<float> eTauDPhi(reader,"ETau_ETauDPhi");
    TTreeReaderArray<float> eTauDR(reader,"ETau_ETauDR");
    TTreeReaderArray<float> eTauVisM(reader,"ETau_visM");
    TTreeReaderValue<int> eIdx(reader,"ETau_eIdx");
    TTreeReaderArray<float> Electron_pt(reader,"Electron_pt");
    TTreeReaderArray<float> Electron_eta(reader,"Electron_eta");
    TTreeReaderArray<float> Electron_phi(reader,"Electron_phi");
    TTreeReaderArray<int> eTauIdx(reader,"ETau_tauIdx");
    TTreeReaderArray<bool> muTauCand(reader,"MuTau_isCand");
    TTreeReaderArray<float> muTauMinCollM(reader,"MuTau_minCollM");
    TTreeReaderArray<float> muTauMaxCollM(reader,"MuTau_maxCollM");
    TTreeReaderArray<int> muTauSign(reader,"MuTau_sign");
    TTreeReaderArray<float> muTauDPhi(reader,"MuTau_MuTauDPhi");
    TTreeReaderArray<float> muTauDR(reader,"MuTau_MuTauDR");
    TTreeReaderArray<float> muTauVisM(reader,"MuTau_visM");
    TTreeReaderValue<int> muIdx(reader,"MuTau_muIdx");
    TTreeReaderArray<int> muTauIdx(reader,"MuTau_tauIdx");
    TTreeReaderArray<float> Muon_pt(reader,"Muon_pt");
    TTreeReaderArray<float> Muon_eta(reader,"Muon_eta");
    TTreeReaderArray<float> Muon_phi(reader,"Muon_phi");
    TTreeReaderArray<bool> tauTauCand(reader,"TauTau_isCand");
    TTreeReaderArray<float> tauTauMinCollM(reader,"TauTau_minCollM");
    TTreeReaderArray<float> tauTauMaxCollM(reader,"TauTau_maxCollM");
    TTreeReaderArray<int> tauTauSign(reader,"TauTau_sign");
    TTreeReaderArray<float> tauTauDPhi(reader,"TauTau_TauTauDPhi");
    TTreeReaderArray<float> tauTauDR(reader,"TauTau_TauTauDR");
    TTreeReaderArray<float> tauTauVisM(reader,"TauTau_visM");
    TTreeReaderArray<int> tau1Idx(reader,"TauTau_tau1Idx");
    TTreeReaderArray<int> tau2Idx(reader,"TauTau_tau2Idx");
    TTreeReaderArray<float> Tau_pt(reader,"Tau_pt");
    TTreeReaderArray<float> Tau_eta(reader,"Tau_eta");
    TTreeReaderArray<float> Tau_phi(reader,"Tau_phi");
    TTreeReaderValue<float> Z_pt(reader,"Z_pt");
    TTreeReaderValue<float> Z_eta(reader,"Z_eta");
    TTreeReaderValue<float> Z_phi(reader,"Z_phi");
    TTreeReaderValue<float> Z_mass(reader,"Z_mass");
    TTreeReaderValue<int> Z_dm(reader,"Z_dm");
    TTreeReaderValue<int> Z_jetIdxAK8(reader,"Z_jetIdxAK8");
    TTreeReaderValue<float> Z_dauDR(reader,"Z_dauDR");
    TTreeReaderValue<float> MET_pt(reader,"MET_pt");
    TTreeReaderValue<float> MET_phi(reader,"MET_phi");
    TTreeReaderValue<float> sdcmMin(reader,"SDCM_min");
    TTreeReaderValue<float> sdcmMax(reader,"SDCM_max");
    TTreeReaderValue<int> nBTags(reader, "ObjCnt_nBTags");
    TTreeReaderValue<bool> metTrig(reader, "Trig_MET");
    TTreeReaderValue<unsigned int> run(reader, "run");
    TTreeReaderValue<unsigned int> lumiBlock(reader, "luminosityBlock");
    TTreeReaderValue<unsigned long long> event(reader, "event");

    while (reader.Next())
    {
        //Run 2 needs to check MET trigger but run 3 trigger is pre-checked
        bool trig;
        if (filename.Contains("201"))
            trig = *metTrig;
        else
            trig = true;


        if (eTauCand[1])
        {
            if (*nBTags < 2 && eTauSign[1] < 0 && abs(eTauDPhi[1]) < 2.8 && eTauDR[1] > 1.5 && *MET_pt > 175 && *Z_pt > 400 && *Z_dauDR < 0.5 && eTauVisM[1] > 200 && trig && Tau_pt[eTauIdx[1]] > 100 && Electron_pt[*eIdx] > 50)
            {
                for (int mN = 0; mN < nMasses; mN++)
                {
                    //NB: if using SDCM, need to swap the below lines
                    //if ((sdcmMin > minBounds[mN] && sdcmMin < maxBounds[mN]) || (sdcmMax > minBounds[mN] && sdcmMax < maxBounds[mN]))
                    if ((eTauMinCollM[1] > minBounds[mN] && eTauMinCollM[1] < maxBounds[mN]) || (eTauMaxCollM[1] > minBounds[mN] && eTauMaxCollM[1] < maxBounds[mN]))
                    {
                        std::cout<<"\nFound ETau channel event for m=" << masses[mN] << " in " << filename << std::endl;
                        std::cout<<"Run = "<< *run << " : LumiBlock = " << *lumiBlock << " : event = " << *event << std::endl; 
                        //NB: if using SDCM, need to swap the below lines
                        std::cout<<"\tMin Collinear Mass = " << eTauMinCollM[1] << " : Max Collinear Mass = " << eTauMaxCollM[1] << std::endl;
                        //std::cout<<"\tMin Collinear Mass = " << sdcmMin << " : Max Collinear Mass = " << sdcmMax << std::endl;
                        std::cout<<"\tTau_pt =  " << Tau_pt[eTauIdx[1]] << " : Tau_eta = " << Tau_eta[eTauIdx[1]] << " : Tau_phi = " << Tau_phi[eTauIdx[1]] << std::endl;
                        std::cout<<"\tEl_pt = " << Electron_pt[*eIdx] << " : El_eta = " << Electron_eta[*eIdx] << " : El_phi = " << Electron_phi[*eIdx] << std::endl;
                        std::cout<<"\tZ_dm = " << *Z_dm << " : Z_pt = " << *Z_pt << " : Z_eta = " << *Z_eta << " : Z_phi = " << *Z_phi << std::endl;
                        std::cout<<"\tMET_pt = " << *MET_pt << " : MET_phi = " << *MET_phi << std::endl; 
                    }
                }
            }
        }
        else if (muTauCand[1])
        {
            if (*nBTags < 2 && muTauSign[1] < 0 && abs(muTauDPhi[1]) < 2.8 && muTauDR[1] > 1.5 && *MET_pt > 175 && *Z_pt > 400 && *Z_dauDR < 0.5 && muTauVisM[1] > 200 && trig && Tau_pt[muTauIdx[1]] > 100 && Muon_pt[*muIdx] > 50)
            {
                for (int mN = 0; mN < nMasses; mN++)
                    {
                        //NB: if using SDCM, need to swap the below lines
                        //if ((sdcmMin > minBounds[mN] && sdcmMin < maxBounds[mN]) || (sdcmMax > minBounds[mN] && sdcmMax < maxBounds[mN]))
                        if ((muTauMinCollM[1] > minBounds[mN] && muTauMinCollM[1] < maxBounds[mN]) || (muTauMaxCollM[1] > minBounds[mN] && muTauMaxCollM[1] < maxBounds[mN]))
                        {
                            std::cout<<"\nFound MuTau channel event for m=" << masses[mN] << " in " << filename << std::endl;
			    std::cout<<"Run = "<< *run << " : LumiBlock = " << *lumiBlock << " : event = " << *event << std::endl; 
                            //NB: if using SDCM, need to swap the below lines
                            std::cout<<"\tMin Collinear Mass = " << muTauMinCollM[1] << " : Max Collinear Mass = " << muTauMaxCollM[1] << std::endl;
                            //std::cout<<"\tMin Collinear Mass = " << sdcmMin << " : Max Collinear Mass = " << sdcmMax << std::endl;
                            std::cout<<"\tTau_pt =  " << Tau_pt[muTauIdx[1]] << " : Tau_eta = " << Tau_eta[muTauIdx[1]] << " : Tau_phi = " << Tau_phi[muTauIdx[1]] << std::endl;
                            std::cout<<"\tMu_pt = " << Muon_pt[*muIdx] << " : Mu_eta = " << Muon_eta[*muIdx] << " : Mu_phi = " << Muon_phi[*muIdx] << std::endl;
                            std::cout<<"\tZ_dm = " << *Z_dm << " : Z_pt = " << *Z_pt << " : Z_eta = " << *Z_eta << " : Z_phi = " << *Z_phi << std::endl;
                            std::cout<<"\tMET_pt = " << *MET_pt << " : MET_phi = " << *MET_phi << std::endl;   
                        }
                    }
            }
        }
        else if (tauTauCand[1])
        {
            if (*nBTags < 2 && tauTauSign[1] < 0 && abs(tauTauDPhi[1]) < 2.8 && tauTauDR[1] > 1.5 && *MET_pt > 175 && *Z_pt > 400 && *Z_dauDR < 0.5 && tauTauVisM[1] > 200 && trig && Tau_pt[tau1Idx[1]] > 100 && Tau_pt[tau2Idx[1]] > 100)
            {
                for (int mN = 0; mN < nMasses; mN++)
                {
                    //NB: if using SDCM, need to swap the below lines
                    //if ((sdcmMin > minBounds[mN] && sdcmMin < maxBounds[mN]) || (sdcmMax > minBounds[mN] && sdcmMax < maxBounds[mN]))
                    if ((tauTauMinCollM[1] > minBounds[mN] && tauTauMinCollM[1] < maxBounds[mN]) || (tauTauMaxCollM[1] > minBounds[mN] && tauTauMaxCollM[1] < maxBounds[mN]))
                    {
                        std::cout<<"\nFound TauTau channel event for m=" << masses[mN] << " in " << filename << std::endl;
                        std::cout<<"Run = "<< *run << " : LumiBlock = " << *lumiBlock << " : event = " << *event << std::endl; 
                        //NB: if using SDCM, need to swap the below lines
                        std::cout<<"\tMin Collinear Mass = " << tauTauMinCollM[1] << " : Max Collinear Mass = " << tauTauMaxCollM[1] << std::endl;
                        //std::cout<<"\tMin Collinear Mass = " << sdcmMin << " : Max Collinear Mass = " << sdcmMax << std::endl;
                        std::cout<<"\tTau1_pt =  " << Tau_pt[tau1Idx[1]] << " : Tau1_eta = " << Tau_eta[tau1Idx[1]] << " : Tau1_phi = " << Tau_phi[tau1Idx[1]] << std::endl;
                        std::cout<<"\tTau2_pt =  " << Tau_pt[tau2Idx[1]] << " : Tau2_eta = " << Tau_eta[tau2Idx[1]] << " : Tau2_phi = " << Tau_phi[tau2Idx[1]] << std::endl;
                        std::cout<<"\tZ_dm = " << *Z_dm << " : Z_pt = " << *Z_pt << " : Z_eta = " << *Z_eta << " : Z_phi = " << *Z_phi << std::endl;
                        std::cout<<"\tMET_pt = " << *MET_pt << " : MET_phi = " << *MET_phi << std::endl; 
                    }
                }
            }
        }
        else
        {
            continue;
        }
    }

    file->Close();
}
