
#A centrally defined spot for analysis cuts for import by analysis/plotting scripts
#Cut format: stage{gen, reco, trig}_particle/channel{z, tau, e, mu, etau, mutau, tautau}_era/year{2016, 2016post, 2017, 2018, 2022, 2022post, 2023, 2023post, run2, run3}
#If cut is agnostic to part, "all" is used



reco_z_all = "(Z_dm>=1 && Z_dm <= 2)" #TODO allow dm==0 once hadronic Z reconstruction is improved
gen_z_all = "(Gen_isCand)"

reco_tau_run3 = "(1>0)" #TODO


#TODO
def getCuts(var, channel, tier):
    cuts = "((1>0)"

    if True:
        if tier == "Rec":
            cuts += "&& (Z_dm >= 0 && Z_dm <= 2)"
            if channel != "":
                cuts += " && ("+channel+"_isCand)"
        else:
            cuts += "&& Gen_isCand"

    cuts +=")"
    return cuts
