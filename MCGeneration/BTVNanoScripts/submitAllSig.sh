#!/usr/bin/env bash

#Make sure you've run this:
#source /cvmfs/cms.cern.ch/common/crab-setup.sh prod

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <YEAR>"
  exit 1
fi


YEAR=$1

VALID_YEARS=("2022" "2022post" "2023" "2023post")

if [[ ! " ${VALID_YEARS[@]} " =~ " ${YEAR} " ]]; then
  echo "Error: Invalid YEAR. Valid options are: ${VALID_YEARS[@]}"
  exit 1
fi

MASSES=("250" "500" "750" "1000" "1500" "2000" "2500" "3000" "3500" "4000" "4500" "5000")

for MASS in "${MASSES[@]}"; do
  #echo "Running for MASS=${MASS} and YEAR=${YEAR}..."  
  python3 crabby.py -c crab_ymls/taustar_${YEAR}_${MASS}.yml --make --submit
done

