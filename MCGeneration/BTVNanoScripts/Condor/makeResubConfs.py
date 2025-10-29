#Script to compare created configs to completed .root output file lists and make resubmission jobs
#Jobs needing resubmission are split into halves so as to reduce their required running time
#To produce the completed job file lists, from the original job submission directory, do e.g.

# for proc in DY QCD ST TT WJets WW WZ ZZ; do eosls $TSTTZ/BackgroundMC/PFNano/JobOutputs/25Sep2025/2022/$proc; done > doneFileList.txt

#Script mostly from ChatGPT




#!/usr/bin/env python3
import argparse
import subprocess
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# --- Import process mappings ---
sys.path.append("../../../Framework")
from datasets import procToSubProc_run2, procToSubProc_run3, years_run2, years_run3

EOS_BASE_PATH = "$TSTTZ/BackgroundMC/PFNano/JobOutputs"


def get_finished_jobs(date, year, proc, subproc):
    """Get list of finished jobs for a given subprocess under a category."""
    eosJobList_path = f"./Jobs/{date}/{year}/doneFileList.txt"
    eosJobList_path = os.path.expandvars(eosJobList_path)
    try:
        output = subprocess.check_output(["cat", eosJobList_path], text=True)
    except subprocess.CalledProcessError:
        print(f"Could not access EOS path: {eos_path}")
        return set()

    pattern = re.compile(rf"{subproc}_{year}_(\d+)\.root$")
    finished_jobs = {int(m.group(1)) for line in output.splitlines() if (m := pattern.search(line))}
    return finished_jobs


def get_total_jobs(date, year, subproc):
    """Get list of total jobs (local .sh files) for a given subprocess."""
    job_dir = Path(f"./Jobs/{date}/{year}/")
    if not job_dir.exists():
        print(f"Missing directory: {job_dir}")
        return set()

    pattern = re.compile(rf"run_{subproc}_(\d+)\.sh$")
    total_jobs = {int(m.group(1)) for fname in os.listdir(job_dir) if (m := pattern.match(fname))}
    return total_jobs


def make_jdl_file(jdl_path: Path, executable_name: str, year: str):
    """Write Condor JDL file. Add Run2-specific settings if needed."""
    header = ""
    if year in years_run2:
        header = '+ApptainerImage = "/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7"\n'

    contents = (
        f"{header}"
        f"universe = vanilla\n"
        f"Executable = {executable_name}\n"
        f"should_transfer_files = YES\n"
        f"when_to_transfer_output = ON_EXIT\n"
        f"Output = condor_PFNano-Nano_$(Cluster)_$(Process).stdout\n"
        f"Error = condor_PFNano-Nano_$(Cluster)_$(Process).stderr\n"
        f"Log = condor_PFNano-Nano_$(Cluster)_$(Process).log\n"
    )

    if year in years_run2:
        contents += '+REQUIRED_OS = "rhel7"\n'

    contents += "Queue 1\n"

    with open(jdl_path, "w") as f:
        f.write(contents)
    print(f"Created JDL: {jdl_path.name}")


def split_job_script(job_script_path, year):
    """Split a .sh job file into two new resubmission scripts and matching JDLs."""
    job_script_path = Path(job_script_path)
    with open(job_script_path) as f:
        lines = f.readlines()

    triplets, indices = [], []
    for i, line in enumerate(lines):
        if line.strip().startswith("export INP_FILE="):
            triplets.append(lines[i : i + 3])
            indices.append(i)

    if not triplets:
        print(f"No INP_FILE blocks found in {job_script_path}")
        return

    mid = len(triplets) // 2
    first_half, second_half = triplets[:mid], triplets[mid:]
    start_idx, end_idx = indices[0], indices[-1] + 3
    prologue, epilogue = lines[:start_idx], lines[end_idx:]

    xrdcp_pattern = re.compile(r"(xrdcp\s+tree\.root\s+\S+/)([^/]+\.root)")
    out_pattern = re.compile(r"(export OUT_FILE=)(\S+\.root)")

    def rewrite_half(blocks, epilogue, half_suffix):
        new_blocks, counter = [], 0
        for blk in blocks:
            blk_mod = []
            for l in blk:
                if (m_out := out_pattern.search(l)):
                    rootfile = m_out.group(2)
                    rootfile_mod = rootfile.replace(".root", f"re{half_suffix}_{counter}.root")
                    l = out_pattern.sub(m_out.group(1) + rootfile_mod, l)
                    counter += 1
                blk_mod.append(l)
            new_blocks.extend(blk_mod)

        new_epilogue = []
        for line in epilogue:
            if (m := xrdcp_pattern.search(line)):
                base, rootname = m.group(1), m.group(2)
                rootname_mod = rootname.replace(".root", f"re{half_suffix}.root")
                line = xrdcp_pattern.sub(base + rootname_mod, line)
            new_epilogue.append(line)
        return new_blocks, new_epilogue

    half1_blocks, epilog1 = rewrite_half(first_half, epilogue, 1)
    half2_blocks, epilog2 = rewrite_half(second_half, epilogue, 2)

    resub_dir = job_script_path.parent / "Resubmission"
    resub_dir.mkdir(parents=True, exist_ok=True)

    match = re.match(r"run_(.+)_(\d+)\.sh$", job_script_path.name)
    proc_name, jobnum = match.groups() if match else ("UnknownProc", "UnknownJob")

    for idx, (half_blocks, epilog) in enumerate([(half1_blocks, epilog1), (half2_blocks, epilog2)], start=1):
        new_script_name = job_script_path.stem + f"_re{idx}.sh"
        new_script_path = resub_dir / new_script_name
        with open(new_script_path, "w") as f:
            f.writelines(prologue + half_blocks + epilog)
        os.chmod(new_script_path, 0o755)
        print(f"Created split script: {new_script_path}")

        jdl_name = f"jobConfig_{proc_name}_{year}_{jobnum}re{idx}.jdl"
        jdl_path = resub_dir / jdl_name
        make_jdl_file(jdl_path, new_script_name, year)


def expand_years(years):
    """Expand symbolic year selections like ALL, RUN2, RUN3 into actual years."""
    if "ALL" in years:
        return list(set(years_run2 + years_run3))
    result = []
    if "RUN2" in years:
        result += years_run2
    if "RUN3" in years:
        result += years_run3
    for y in years:
        if y not in ["ALL", "RUN2", "RUN3"]:
            result.append(y)
    return sorted(set(result))


def main():
    parser = argparse.ArgumentParser(description="Check unfinished jobs and split them for resubmission.")
    parser.add_argument("-d", "--dates", nargs="+", required=True, help="Date strings (e.g. 25Sep2025)")
    parser.add_argument(
        "-y", "--years",
        required=True, nargs="+",
        choices=["2016", "2016post", "2017", "2018", "2022", "2022post", "2023", "2023post"],
        help="Which years to process"
    )
    parser.add_argument(
        "-p", "--processes",
        required=True, nargs="+",
        choices=["ALL", "ZZ", "WZ", "WW", "WJets", "DY", "TT", "ST", "QCD"],
        help="Which samples to process"
    )
    parser.add_argument("-s", "--split", action="store_true", help="Split unfinished job scripts into halves")
    args = parser.parse_args()

    years_to_run = expand_years(args.years)
    summary = defaultdict(lambda: {"total": 0, "finished": 0, "missing": 0})

    for date in args.dates:
        for year in years_to_run:
            if year in years_run2:
                mapping = procToSubProc_run2
            elif year in years_run3:
                mapping = procToSubProc_run3
            else:
                print(f"Year {year} not found in any mapping, skipping.")
                continue


            for proc in args.processes:
                if proc not in mapping:
                    print(f"Category '{proc}' not found in mapping for {year}.")
                    continue
                subprocs = mapping[proc]

                for subproc in subprocs:
                    print(f"\nChecking {date} / {year} / {proc}/{subproc} ...")
                    finished = get_finished_jobs(date, year, proc, subproc)
                    total = get_total_jobs(date, year, subproc)
                    missing = sorted(total - finished)

                    summary_key = f"{year}/{proc}/{subproc}"
                    summary[summary_key]["total"] = len(total)
                    summary[summary_key]["finished"] = len(finished)
                    summary[summary_key]["missing"] = len(missing)

                    if missing:
                        print(f"{len(missing)} jobs missing for {subproc}:")
                        for jobnum in missing:
                            job_file = Path(f"./Jobs/{date}/{year}/run_{subproc}_{jobnum}.sh")
                            print(f"  {job_file.name}")
                            if args.split and job_file.exists():
                                split_job_script(job_file, year)
                    else:
                        print(f"All jobs finished successfully for {subproc}.")

    # ---- Print summary ----
    print("\n" + "=" * 80)
    print(f"{'SUMMARY OF JOB STATUS':^80}")
    print("=" * 80)
    print(f"{'Year':<10} {'Category':<12} {'Subprocess':<25} {'Total':>6} {'Done':>6} {'Missing':>8}")
    print("-" * 80)
    total_all = {"total": 0, "finished": 0, "missing": 0}
    for key, vals in sorted(summary.items()):
        year, proc, subproc = key.split("/")
        print(f"{year:<10} {proc:<12} {subproc:<25} {vals['total']:>6} {vals['finished']:>6} {vals['missing']:>8}")
        for k in total_all:
            total_all[k] += vals[k]
    print("-" * 80)
    print(f"{'TOTAL':<49} {total_all['total']:>6} {total_all['finished']:>6} {total_all['missing']:>8}")
    print("=" * 80)
    print("Summary complete.\n")


if __name__ == "__main__":
    main()
