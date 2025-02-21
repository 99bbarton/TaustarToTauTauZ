
masses = ["250","500","750","1000","1500","2000","2500","3000","3500","4000","4500","5000"]
years = ["2022", "2022post", "2023", "2023post"]

yearToConfig = {"2022": "MC_preEE2022_22Sep2023_NANO.py", "2022post" : "MC_2022_22Sep2023_NANO.py", "2023": "MC_Summer23_NANO.py", "2023post": "MC_Summer23_postBPix_NANO.py" }
yearToDASTag = {"2022" : "Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2", "2022post": "Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2", "2023": "Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v15-v2", "2023post": "Run3Summer23BPixMiniAODv4-130X_mcRun3_2023_realistic_postBPix_v6-v2" }

for year in years:
    for mass in masses:
        with open("crab_ymls/taustar_"+year+"_"+mass+".yml", "w+") as outFile:

            outFile.write("campaign:\n")
            outFile.write("  name: taustar_sig_" + year + "\n")
            outFile.write("  crab_template: template_crab.py\n")
            outFile.write("  \n")
            outFile.write("  # User specific\n")
            outFile.write("  workArea: SigPFNano\n")
            outFile.write("  storageSite: T3_US_FNALLPC\n")
            outFile.write("  outLFNDirBase: /store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/"+year+"\n")
            outFile.write("  voGroup: null # or leave empty\n")
            outFile.write("  \n")
            outFile.write("  # Campaign specific\n")
            outFile.write("  tag_extension: _m"+ mass + " # Will get appended after the current tag\n")
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
            outFile.write("  datasets: |\n")
            outFile.write("    /TaustarToTauZ_m"+mass+"_TuneCP5_13p6TeV_pythia8/"+ yearToDASTag[year] +"/MINIAODSIM\n")
