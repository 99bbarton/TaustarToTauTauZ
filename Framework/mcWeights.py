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
        xs = crossections[process] / 1000 #xs in pb whereas lumi is fb
        effLumi = nEvts / xs
        realLumi = lumis[year[:4]]
        weight *= realLumi / effLumi

    return weight




