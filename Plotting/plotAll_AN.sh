#!/usr/bin/env bash

OUTDIR="Plots/AN_7Jan2025/"
COMMON_R3="-i $SIG_R3 -y RUN3 --nS --nP --save .png --nP --figName"

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
### Generation
### GEN-Level Kinematics and Topography
# Trigger Selection

## Run3
## Run2
# Event Selection and Reconstruction


