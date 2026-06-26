

def getMETFilters(year):
    cutStr = "("
    if year == "2016" or "2016post":
        cutStr += "Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter &&Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter)"
    elif year == "2017 or 2018":
        cutStr += "Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter)"
    elif year == "2022" or "2022post" or "2023" or "2023post":
        cutStr += "Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_hfNoisyHitsFilter && Flag_eeBadScFilter)"
    elif year == "2024":
        cutStr += "Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_hfNoisyHitsFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter)"
    else:
        print("\nWARNING: year",year,"was not recognized by getMETFilters!")
        cutStr += "0>1)"

    return cutStr
