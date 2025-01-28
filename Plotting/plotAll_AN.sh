#!/usr/bin/env bash

OUTDIR="Plots/AN_7Jan2025/"
COMMON_R3=" -i $SIG_R3 -y RUN3 --nS --nP --save .png --nP --palette cms"

mkdir $OUTDIR

voms

# Motivation
# Signal MC
## Run3
python3 genPlotter.py -i $SIG_R3 -g pt -p cms -y RUN3 -m 250 -m 1000 -m 3000 -m 5000
cp Plots/GenPlots/pt_TauZ.png $OUTDIR

python3 genPlotter.py -i $SIG_R3 -g eta -p cms -y RUN3 -m 250 -m 1000 -m 3000 -m 5000
cp Plots/GenPlots/eta_TauZ.png $OUTDIR

python3 genPlotter.py -i $SIG_R3 -g phi -p cms -y RUN3 -m 250 -m 1000 -m 3000 -m 5000
cp Plots/GenPlots/phi_TauZ.png $OUTDIR

python3 genPlotter.py -i $SIG_R3 -r -p cms -y RUN3 -m 250 -m 1000 -m 3000 -m 5000
cp Plots/GenPlots/deltaR_TauZ.png $OUTDIR
cp Plots/GenPlots/deltaPhi_tsTauTau.png $OUTDIR

## Run2


# Trigger Selection
## Run3
python3 trigPlotter.py -i $SIG_R3 -y RUN3 --nP -t Trig_tau -t Trig_tauOR -t Trig_MET
cp Plots/TrigPlots/effPerMass_2022_Trig_tau.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2022_Trig_tauOR.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2022_Trig_MET.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2022post_Trig_tau.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2022post_Trig_tauOR.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2022post_Trig_MET.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023_Trig_tau.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023_Trig_tauOR.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023_Trig_MET.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023post_Trig_tau.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023post_Trig_tauOR.png $OUTDIR
cp Plots/TrigPlots/effPerMass_2023post_Trig_MET.png $OUTDIR


## Run3
## Run2
# Event Selection and Reconstruction

#z mass vs z pt
python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==0" --nP --save ".png" --plotName "Plots/zMvsPt_jet"
#python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==0" --drawStyle "CANDLE3" --plotName "Plots/zMvsPt_jet_cand" -b "30" "0" "3000" "15" "60" "120" --nP --save ".png"
python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==1" --nP --save ".png" --plotName "Plots/zMvsPt_ee"
#python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==1" --drawStyle "CANDLE3" --plotName "Plots/zMvsPt_ee_cand" -b "30" "0" "3000" "15" "60" "120" --nP --save ".png"
python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==2" --nP --save ".png" --plotName "Plots/zMvsPt_mumu"
#python3 plotter.py "Z_PT" "Z_M" -i $SIG_R3 -y "RUN3" -p "SIG_ALL" --cuts "Gen_isCand&&Z_isCand&&Z_dm==2" --drawStyle "CANDLE3" --plotName "Plots/zMvsPt_mumu_cand" -b "30" "0" "3000" "15" "60" "120" --nP --save ".png"
cp "Plots/zMvsPt_jet.png" "Plots/EvtSelAndReco/"
#cp "Plots/zMvsPt_jet_cand.png" "Plots/EvtSelAndReco/"
cp "Plots/zMvsPt_ee.png" "Plots/EvtSelAndReco/"
#cp "Plots/zMvsPt_ee_cand.png" "Plots/EvtSelAndReco/"
cp "Plots/zMvsPt_mumu.png" "Plots/EvtSelAndReco/"
#cp "Plots/zMvsPt_mumu_cand.png" "Plots/EvtSelAndReco/"


#DeltaR of visible and invisible tau decay products
python3 plotter.py "VISINVDR" $COMMON_R3 -p "SIG_DEF" -e "MASS" --cuts "Gen_isCand"
cp "Plots/vvisinvdr_per_mass.png" "EvtSelAndReco/"

#2D Collinear mass
python3 plotter.py "MIN_COL_M" "MAX_COL_M" $COMMON_R3 -p "SIG_DEF" -e "MASS" --cuts "Gen_isCand&&Z_isCand&&CHANNEL_isCand"
cp "Plots/min_col_m_vs_max_col_m.png" "EvtSelAndReco/"
