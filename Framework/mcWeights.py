#Tool to provide the event weight for MC samples

from datasets import nEvents, crossections_2016, crossections_2017, crossections_2018, crossections_run3, yrTonEventsIdx, years_run3

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

def getWeight(process, year, xs=True):

    weight = 1

    if year == "2016" or year == "2016post":
        crossections = crossections_2016
    elif year == "2017":
        crossections = crossections_2017
    elif year == "2018":
        crossections = crossections_2018
    else:
        crossections = crossections_run3
    
    
    if xs:
        nEvts = nEvents[process][yrTonEventsIdx[year]]
        xs = crossections[process][0] *1000 #xs in pb but lumi in fb 
        if process.startswith("M"):
            xs = xs*1
        effLumi = nEvts / xs
        realLumi = lumis[year][0]
        weight *= (realLumi / effLumi)
        
    #print(process, weight)
    return weight

#def getSystStr(year, channel, lumi="NOM", tauES="NOM", tauID="NOM", eID="NOM", muID="NOM", trig="NOM", PDF="NOM"):
#    systDict = {"lumi":1, "tauES":1, "tauID":1, "eID":1, "muID":1, "trig":1, "PDF":1}
#    syst = 1.0

#Systematics (applicability domain):
#Lumi 
#Tau Energy scale
#Tau ID
#E ID (ETau, Z_ee)
#Mu ID (MuTau, Z_mumu)
#Trigger SF (run3)
#PDF reweighting (signal)