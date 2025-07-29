#Tool to provide the event weight for MC samples

from datasets import nEvents, crossections, yrTonEventsIdx

#year : [lumi, err] in fb^-1 
#values from: https://twiki.cern.ch/twiki/bin/view/CMSPublic/LumiPublicResults
lumis = {
    "2022" : [41.5, 0],
    "2023" : [32.7, 0]
}

def getWeight(process, year, xs=True):

    weight = 1

    if xs:
        nEvts = nEvents[process][yrTonEventsIdx[year]]
        xs = crossections[process][0] *1000 #xs in pb but lumi in fb 
        if process.startswith("M"):
            xs = xs*100
        effLumi = nEvts / xs
        realLumi = lumis[year[:4]][0]
        weight *= (realLumi / effLumi)
        
    #print(process, weight)
    return weight


