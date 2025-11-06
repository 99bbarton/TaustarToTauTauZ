#!/bin/bash

# Usage: ./resubmit_failed_jobs.sh <DATE> <YEAR_TAG>
# Example: ./resubmit_failed_jobs.sh 10-30 2022post
#
# <YEAR_TAG> corresponds to the string in your jobConfig files,
# e.g., "2022post" in jobConfig_<PROCESS>_<YEAR_TAG>.jdl

DATE=$1
YEAR_TAG=$2
JOB_DIR="Jobs/${DATE}/${YEAR_TAG}/Resubmission"

if [ ! -d "$JOB_DIR" ]; then
    echo "Error: Directory $JOB_DIR not found."
    exit 1
fi

echo "Scanning for failed jobs in: $JOB_DIR"

# Step 1: Identify failed jobs (.stderr files without XRDEXIT=0)
FAILED_FILES=$(grep "XRDEXIT=0" "${JOB_DIR}"/condor_PFNano-Nano_*.stderr -L 2>/dev/null)

if [ -z "$FAILED_FILES" ]; then
    echo "No failed jobs found."
    exit 0
fi

echo "Found $(echo "$FAILED_FILES" | wc -l) failed jobs."

# Step 2: Loop over failed stderr files
for FILE in $FAILED_FILES; do
    # Extract job ID from filename (e.g., condor_PFNano-Nano_1180480_0.stderr -> 1180480)
    JOB_ID=$(basename "$FILE" | sed -E 's/.*_([0-9]+)_.*/\1/')
    
    # Find matching entry in jobsList.txt
    JOB_LINE=$(grep "^${JOB_ID}\." "${JOB_DIR}/jobList.txt")
    
    if [ -z "$JOB_LINE" ]; then
        echo "Warning: No matching job entry found for ID ${JOB_ID}."
        continue
    fi
    
    # Extract CMD (the last column, which should be the script name)
    CMD=$(echo "$JOB_LINE" | awk '{print $NF}')


    # CMD format: run_<PROCESS>_<NUM>_re<SUBNUM>.sh
    # Extract components
    BASENAME=$(basename "$CMD" .sh)
    # Split into parts
    #PROCESS=$(echo "$BASENAME" | sed -E 's/^run_([^_]+)_.*/\1/')
    #NUM=$(echo "$BASENAME" | sed -E 's/^run_[^_]+_([0-9]+)_re[0-9]+$/\1/')
    #SUBNUM=$(echo "$BASENAME" | sed -E 's/^run_[^_]+_[0-9]+_re([0-9]+)$/\1/')

    PROCESS=$(echo "$BASENAME" | sed -E 's/^run_([^_]+)_.*/\1/')
    NUM="${BASENAME##*_}"
    echo "CMD = $CMD"
    echo "Basename = $BASENAME"
    echo "process = $PROCESS"
    echo "NUM = $NUM"
    #echo "SUBNUM = $SUBNUM"
    
    # Build expected config filename:
    # jobConfig_<PROCESS>_<YEAR_TAG>_<NUM>re<SUBNUM>.jdl
    #CONFIG_FILE="jobConfig_${PROCESS}_${YEAR_TAG}_${NUM}re${SUBNUM}.jdl"
    CONFIG_FILE="jobConfig_${PROCESS}_${NUM}.jdl"
    CONFIG_PATH="${JOB_DIR}/${CONFIG_FILE}"
    
    if [ -f "$CONFIG_PATH" ]; then
	cd $JOB_DIR
        echo "Resubmitting job using: $CONFIG_FILE"
        condor_submit "${CONFIG_FILE}"
	cd ../../../../
    else
        echo "Missing config file: $CONFIG_PATH"
    fi
done

