
#year options:  ["2022", "2022post", "2023", "2023post"]
years = ["2022post"]
#process options: ["ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"]
processes = ["ZZ"]

yearToConfig = {"2022": "MC_preEE2022_22Sep2023_NANO.py", "2022post" : "MC_2022_22Sep2023_NANO.py", "2023": "MC_Summer23_NANO.py", "2023post": "MC_Summer23_postBPix_NANO.py" }



datasets = {
    "2022" : {},
    "2022post" : {
                "ZZ" : ["/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/ZZto2Nu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "WZ" : ["/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/WZtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "WW" : ["/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/WWtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                ],
                "WJets" : ["/WtoLNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "DY" : ["/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "TT" : ["/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "ST" : ["/TWminusto4Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TWminustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TbarWplusto4Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TbarWplustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TBbarQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/TbarBQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM"
                ],
                "QCD" : ["/QCD_PT-80to120_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-120to170_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-120to170_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-1400to1800_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-1400to1800_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-170to300_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-170to300_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-300to470_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-300to470_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-3200_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-3200_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-470to600_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-470to600_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-600to800_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-600to800_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-800to1000_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-800to1000_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-1000to1400_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-1000to1400_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-1800to2400_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-1800to2400_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM",
                        "/QCD_PT-2400to3200_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM",
                        "/QCD_PT-2400to3200_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM"
                ]
            },
    "2023" : {},
    "2023post" : {}
}


for year in years:
    for proc in processes:
        for dataset in datasets[year][proc]:
            dsName = dataset[:dataset.find("TuneCP5")-1]
            filename = "crab_ymls/MC/"+year+"/" + dsName + "_" + year + ".yml"
            with open(filename, "w+") as outFile:
                outFile.write("campaign:\n")
                outFile.write("  name: mc_" + proc + "_" + year + "\n")
                outFile.write("  crab_template: template_crab.py\n")
                outFile.write("  \n")
                outFile.write("  # User specific\n")
                outFile.write("  workArea: MCPFNano\n")
                outFile.write("  storageSite: T3_US_FNALLPC\n")
                outFile.write("  outLFNDirBase: /store/user/bbarton/TaustarToTauTauZ/BackgroundMC/PFNano/"+year+"/"+proc+"\n")
                outFile.write("  voGroup: null # or leave empty\n")
                outFile.write("  \n")
                outFile.write("  # Campaign specific\n")
                outFile.write("  tag_extension: " + dsName + " # Will get appended after the current tag\n")
                outFile.write("  tag_mod: # Will modify name in-place for MC eg. 'PFNanoAODv1' will replace MiniAODv2 -> PFNanoAODv1\n")
                outFile.write("  # If others shall be able to access dataset via DAS (important when collaborating for commissioning!)\n")
                outFile.write("  publication: False\n")
                outFile.write("  config: " + yearToConfig[year] + "\n")
                outFile.write("  # Specify if running on data\n")
                outFile.write("  data: False\n")
                outFile.write("  lumiMask:\n")
                outFile.write("  # datasets will take either a list of DAS names or a text file containing them\n")
                outFile.write("  # do NOT submit too many tasks at the same time, despite it looking more convenient to you\n")
                outFile.write("  # wait for tasks to finish before submitting entire campaigns,\n")
                outFile.write("  # it's better to request one dataset at a time (taking fairshare into account)\n")
                outFile.write("  datasets: \n")
                outFile.write("    " + dataset + "\n")
