
#Definitions of trigger+associated cuts
#Dictionary naming convention: trig_run_cutTier
#Trigger Naming convention: obj_year_ch

trig_run3 = {"tau_2023_eTau" : "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1",
                 "tau_2023_muTau" : "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1",
                 "tau_2023_tautau": "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1",
                 "tau_2023_tau": "HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1",
                 "tai_2023_all": "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1 || HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 || HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 || HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1", 
                 "tau_2022_eTau" : "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1",
                 "tau_2022_muTau" : "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1",
                 "tau_2022_tautau": "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1",
                 "tau_2022_tau": "HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1",
                 "tau_2022_all": "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1 || HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 || HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 || HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1",
                 "met_2023": "HLT_PFMET200_BeamHaloCleaned",
                 "met_2022": "HLT_PFMET200_BeamHaloCleaned"
               }



trig_run3_gen = {"tau_2023_eTau" : "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0))",
                 "tau_2023_muTau" : "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0))",
                 "tau_2023_tautau": "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 && (Gen_tsTauDM==0&&Gen_tauDM==0)",
                 "tau_2023_tau": "HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1 && (Gen_tsTauDM==0||Gen_tauDM==0)",
                 "tau_2023_all": "((HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0)))||(HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0)))||(HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 && (Gen_tsTauDM==0&&Gen_tauDM==0))||(HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1 && (Gen_tsTauDM==0||Gen_tauDM==0)))",
                 "tau_2022_eTau" : "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1  && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0))",
                 "tau_2022_muTau" : "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0))",
                 "tau_2022_tautau": "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 && (Gen_tsTauDM==0&&Gen_tauDM==0)",
                 "tau_2022_tau": "HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1 && (Gen_tsTauDM==0||Gen_tauDM==0)",
                 "tau_2022_all": "((HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1  && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0)))||(HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0)))||(HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1 && (Gen_tsTauDM==0&&Gen_tauDM==0))||(HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1 && (Gen_tsTauDM==0||Gen_tauDM==0)))",
                 "met_2023": "HLT_PFMET200_BeamHaloCleaned && (Gen_tsTauDM==0||Gen_tauDM==0)",
                 "met_2022": "HLT_PFMET200_BeamHaloCleaned && (Gen_tsTauDM==0||Gen_tauDM==0)"
               }


trig_run2_gen = {"tau_2018_eTau": "HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0))",
                 "tau_2018_muTau": "HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0))",
                 "tau_2018_tautau": "HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg && ((Gen_tsTauDM==0&&Gen_tauDM==0))",
                 "tau_2018_all": "((HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==1)||(Gen_tsTauDM==1&&Gen_tauDM==0)))||(HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1 && ((Gen_tsTauDM==0&&Gen_tauDM==2)||(Gen_tsTauDM==2&&Gen_tauDM==0)))||(HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg && ((Gen_tsTauDM==0&&Gen_tauDM==0))))",
                 "met_2018": "HLT_PFMET200_HBHE_BeamHaloCleaned && (Gen_tsTauDM==0||Gen_tauDM==0)"

}

