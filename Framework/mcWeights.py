#Tool to provide the event weight for MC samples

from datasets import nEvents, crossections_2016, crossections_2017, crossections_2018, crossections_run3, yrTonEventsIdx

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
    "2023post" : [9.45, 0.123]
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


