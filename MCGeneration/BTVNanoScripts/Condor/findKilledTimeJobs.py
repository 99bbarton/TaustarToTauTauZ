#Script to find the processes of jobs which ran into Condor job time limit and were killed
#Courtesy of ChatGPT

# Directory with log files
log_dir = "Jobs/25Sep2025/2022post"   #CHANGE ME

import os
import re

# Job list file
job_list_file = log_dir+"/jobList.txt"

# Step 1: Parse jobList.txt into a dictionary {jobID: CMD}
job_map = {}
with open(job_list_file, "r") as f:
    for line in f:
        line = line.strip()
        # Match jobID lines like "842245.0   bbarton ..."
        m = re.match(r"^(\d+)\.\d+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(.+)$", line)
        if m:
            job_id = m.group(1)   # numeric jobID
            cmd = m.group(2)
            job_map[job_id] = cmd

# Step 2: Collect unique processes
unique_processes = set()

for filename in os.listdir(log_dir):
    if filename.startswith("condor_PFNano-Nano_") and filename.endswith(".log"):
        filepath = os.path.join(log_dir, filename)

        # Extract jobID from filename
        m = re.search(r"condor_PFNano-Nano_(\d+)_", filename)
        if not m:
            continue
        job_id = m.group(1)

        # Step 3: Check if file contains SYSTEM_PERIODIC_REMOVE
        with open(filepath, "r") as f:
            contents = f.read()
            if "SYSTEM_PERIODIC_REMOVE" in contents:
                cmd = job_map.get(job_id)
                if cmd and cmd.endswith(".sh"):
                    # Extract process name from run_..._X.sh
                    process = cmd.replace("run_", "").replace(".sh", "")
                    process = process.rsplit("_", 1)[0]  # remove last underscore + number
                    unique_processes.add(process)

# Step 4: Output
print("Processes which had jobs killed by SYSTEM_PERIODIC_REMOVE:")
for proc in sorted(unique_processes):
    print(proc)
