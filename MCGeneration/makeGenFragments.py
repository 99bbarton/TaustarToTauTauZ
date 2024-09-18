# A script to produce the GEN fragments needed for stage 1 of MC production
# Produces one fragment per mass + decay mode combination
# Writes output to ./GenFragments/

import os

run3 = True

#Taustar masses
#masses = ["500", "1000", "3000", "5000"]
masses = ["250", "500", "750", "1000", "1250", "1500", "1750", "2000", "2500", "3000", "3500", "4000", "4500",  "5000"]

#Allowed decay modes in terms of PDG IDs
allowedDecays = []
#allowedDecays.append("15 22") # tau+gamma decay
allowedDecays.append("15 23") # tau+Z decay
#allowedDecays.extend(["24 16"]) # W+nu decays 

if not os.path.isdir("GenFragments"):
    os.system("mkdir GenFragments")
    if run3 and not os.path.isdir("GenFragments/Run3/"):
        os.system("mkdir GenFragments/Run3/")
    elif not run3 and not os.path.isdir("GenFragments/Run2/"):
        os.system("mkdir GenFragments/Run2/")

for mass in masses:
    #Build filename
    if run3:
        filename = "taustarTo"
    else:
        filename = "taustarToTau"
    if allowedDecays[0].find("22") >=0:
        filename += "TauGamma"
    elif allowedDecays[0].find("23") >= 0:
        filename += "TauZ"
    elif allowedDecays[0].find("24") >= 0:
        filename += "WNu"
    else:
        print("ERROR: Unrecognized decay mode when creating filename")
        exit(1)
    filename += "_m" + mass + ".py"

    #Create the fragment
    dir = "GenFragments/"
    if run3:
        dir += "Run3/"
    else:
        dir += "Run2/"
    with open(dir + filename, "w+") as fragmentFile:
        fragmentFile.write("import FWCore.ParameterSet.Config as cms\n")
        fragmentFile.write("from Configuration.Generator.Pythia8CommonSettings_cfi import *\n")
        if run3:
            fragmentFile.write("from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *\n")
        else:
            fragmentFile.write("from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *\n")
        fragmentFile.write("generator = cms.EDFilter('Pythia8ConcurrentGeneratorFilter',\n")
        fragmentFile.write("                        maxEventsToPrint = cms.untracked.int32(1),\n")
        fragmentFile.write("                        pythiaPylistVerbosity = cms.untracked.int32(1),\n")
        fragmentFile.write("                        filterEfficiency = cms.untracked.double(1.0),\n")
        fragmentFile.write("                        pythiaHepMCVerbosity = cms.untracked.bool(False),\n")
        if run3:
            fragmentFile.write("                        comEnergy = cms.double(13600.),\n")
        else:
            fragmentFile.write("                        comEnergy = cms.double(13000.),\n")
        fragmentFile.write("                        PythiaParameters = cms.PSet(\n")
        fragmentFile.write("        pythia8CommonSettingsBlock,\n")
        fragmentFile.write("        pythia8CP5SettingsBlock,\n")
        fragmentFile.write("        processParameters = cms.vstring(\n")
        fragmentFile.write("            'ExcitedFermion:qqbar2tauStartau = on',\n")
        fragmentFile.write("            'ExcitedFermion:Lambda= 10000',\n")
        fragmentFile.write("            '4000015:onMode = off',\n")
        for decay in allowedDecays:
            fragmentFile.write("            '4000015:onIfMatch = " + decay + "',\n")
        fragmentFile.write("            '4000015:m0 = " + mass + "'),\n")
        fragmentFile.write("                        parameterSets = cms.vstring('pythia8CommonSettings',\n")
        fragmentFile.write("                                                    'pythia8CP5Settings',\n")
        fragmentFile.write("                                                    'processParameters',\n")
        fragmentFile.write("                                                    )))\n")
