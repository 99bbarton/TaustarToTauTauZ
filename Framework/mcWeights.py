#Tool to provide the event weight for MC samples

from datasets import nEvents, crossections_2016, crossections_2017, crossections_2018, crossections_run3, yrTonEventsIdx, years_run3
from math import sqrt

#year : [lumi, err] in fb^-1 
#values from: https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3
# https://docs.google.com/presentation/d/1F4ndU7DBcyvrEEyLfYqb29NGkBPs20EAnBxe_l7AEII/edit?slide=id.g289f499aa6b_2_52#slide=id.g289f499aa6b_2_52
# https://docs.google.com/presentation/d/1TjPem5jX0fzqvTGl271_nQFoVBabsrdrO0i8Qo1uD5E/edit?slide=id.g289f499aa6b_2_58#slide=id.g289f499aa6b_2_58


lumis = {
    "2016" : [19.5, 0.234],
    "2016post" : [16.8, 0.202],
    "2017" : [41.5, 0.955],
    "2018" : [59.8, 0.150],
    "2022" : [7.98, 0.112],
    "2022post" : [26.67, 0.373],
    "2023" : [17.79, 0.231],
    "2023post" : [9.45, 0.123],
    "2024" : [109, 2.18]   #NB: LUMI POG does not provide a lumi uncertainty for 2024. Using 2% here as a conservative (bigger than all other years) value
}

def getXSWeight(process, year):

    if year == "2016" or year == "2016post":
        crossections = crossections_2016
    elif year == "2017":
        crossections = crossections_2017
    elif year == "2018":
        crossections = crossections_2018
    else:
        crossections = crossections_run3

    nEvts = nEvents[process][yrTonEventsIdx[year]]
    xs = crossections[process][0] *1000 #xs in pb but lumi in fb 
    xsUnc = crossections[process][1] *1000
    effLumi = nEvts / xs
    realLumi = lumis[year][0]
    realLumiUnc = lumis[year][1]
    weight = (realLumi / effLumi)
    uncert = sqrt(xsUnc**2 + realLumiUnc**2)
        
    #print(process, weight)
    return weight, uncert

# Given a year, channel and dictionary containing any or all of the following systematics,
# return the variable string used to extract corresponding weights from the Events tree
# Each syst can have the value "DOWN", "NOM", or "UP"
#systDict = {"TAUID": "", "EID": "", "MUID": "", "TRIG":""}
def getSystStr(year, channel, systDict):
    
    if channel not in ["ETau", "MuTau", "TauTau"]:
        print("ERROR: Unrecognized channel :", channel, "in getSystStr()")
        exit(1)
    
    tagToIdxStr = {"DOWN" : "[0]", "NOM" : "[1]", "UP" : "[2]", "DOWN2" : "[3]", "NOM2" : "[4]", "UP2" : "[5]"}

    systStr = "*(1.0"
    
    for key in systDict:
        key = key.upper()
        idxStr = tagToIdxStr[systDict[key].upper()]
        secIdxStr = tagToIdxStr[systDict[key].upper() + "2"]
        if key == "TAUID":
            if channel == "TauTau":
                systStr += "*" + channel + "_tauVsESF"+ idxStr + "*" + channel + "_tauVsMuSF"+ idxStr + "*" + channel + "_tauVsJetSF"+ idxStr
                systStr += "*" + channel + "_tauVsESF"+ secIdxStr + "*" + channel + "_tauVsMuSF"+ secIdxStr + "*" + channel + "_tauVsJetSF"+ secIdxStr
            else:
                systStr += "*" + channel + "_tauVsESF"+ idxStr + "*" + channel + "_tauVsMuSF"+ idxStr + "*" + channel + "_tauVsJetSF"+ idxStr
        elif key == "EID":
            if channel == "ETau":
                systStr += "*ETau_eIDSF" + idxStr + "*Z_eIDSFs"+idxStr + "*Z_eIDSFs" + secIdxStr
            else:
                systStr += "*Z_eIDSFs"+idxStr + "*Z_eIDSFs" + secIdxStr
        elif key == "MUID":
            if channel == "MuTau":
                systStr += "*MuTau_muIDSF" + idxStr + "*Z_muIDSFs"+idxStr + "*Z_muIDSFs" + secIdxStr
            else:
                systStr += "*Z_muIDSFs"+idxStr + "*Z_muIDSFs" + secIdxStr
        if key == "TRIG" and year in years_run3:
            if key == "DOWN":
                systStr += "*0.94"
            elif key == "NOM":
                systStr += "*1.0"
            elif key == "UP":
                systStr += "*1.04"
    
    systStr += ")"
    return systStr




#Systematics (applicability domain):
#Lumi 
#Tau Energy scale
#Tau ID
#E ID (ETau, Z_ee)
#Mu ID (MuTau, Z_mumu)
#Trigger SF (run3)
#PDF reweighting (signal)