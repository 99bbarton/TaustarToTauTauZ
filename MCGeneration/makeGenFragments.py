# A script to produce the GEN fragments needed for stage 1 of MC production
# Produces one fragment per mass + decay mode combination
# Writes output to ./GenFragments/

import os

#Taustar masses
#masses = ["500", "1000", "3000", "5000"]
masses = ["250", "500", "750", "1000", "1250", "1500", "1750", "2000", "2250", "2500", "2750", "3000", "3250", "3500", "3750", "4000", "4250", "4500", "4750", "5000", "5250", "5500", "5750", "6000"]

#Allowed decay modes in terms of PDG IDs
allowedDecays = []
#allowedDecays.append("15 22") # tau+gamma decay
allowedDecays.append("15 23") # tau+Z decay
#allowedDecays.extend(["24 12", "24 14", "24 16"]) # W+nu decays 

if not os.path.isdir("GenFragments"):
    os.system("mkdir GenFragments")

for mass in masses:
    for decay in allowedDecays:
        #Build filename
        filename = "taustarToTau"
        if decay.find("22") >=0:
            filename += "TauGamma"
        elif decay.find("23") >= 0:
            filename += "TauZ"
        elif decay.find("24") >= 0:
            filename += "WNu"
        else:
            print("ERROR: Unrecognized decay mode when creating filename")
            exit(1)
        filename += "_m" + mass + ".py"

        #Create the fragment
        with open("GenFragments/" + filename, "w+") as fragmentFile:
            fragmentFile.write("import FWCore.ParameterSet.Config as cms\n")
            fragmentFile.write("from Configuration.Generator.Pythia8CommonSettings_cfi import *\n")
            fragmentFile.write("from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *\n")
            fragmentFile.write("generator = cms.EDFilter('Pythia8ConcurrentGeneratorFilter',\n")
            fragmentFile.write("                        maxEventsToPrint = cms.untracked.int32(1),\n")
            fragmentFile.write("                        pythiaPylistVerbosity = cms.untracked.int32(1),\n")
            fragmentFile.write("                        filterEfficiency = cms.untracked.double(1.0),\n")
            fragmentFile.write("                        pythiaHepMCVerbosity = cms.untracked.bool(False),\n")
            fragmentFile.write("                        comEnergy = cms.double(13000.),\n")
            fragmentFile.write("                        PythiaParameters = cms.PSet(\n")
            fragmentFile.write("        pythia8CommonSettingsBlock,\n")
            fragmentFile.write("        pythia8CP5SettingsBlock,\n")
            fragmentFile.write("        processParameters = cms.vstring(\n")
            fragmentFile.write("            'ExcitedFermion:qqbar2tauStartau = on',\n")
            fragmentFile.write("            'ExcitedFermion:Lambda= 10000',\n")
            fragmentFile.write("            '4000015:onMode = off',\n")
            fragmentFile.write("            '4000015:onIfMatch = " + decay + "',\n")
            fragmentFile.write("            '4000015:m0 = " + mass + "'),\n")
            fragmentFile.write("                        parameterSets = cms.vstring('pythia8CommonSettings',\n")
            fragmentFile.write("                                                    'pythia8CP5Settings',\n")
            fragmentFile.write("                                                    'processParameters',\n")
            fragmentFile.write("                                                    )))\n")
