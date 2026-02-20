#Make the Brazil plot


import glob
import re
import numpy as np
import uproot
import matplotlib.pyplot as plt
import cmsstyle as CMS
import mplhep as hep
import argparse


def parseArgs():
    argparser = argparse.ArgumentParser(description="Extracts values from Combine AsymptoticLimits Output files and makes a 'Brazil Plot' from them")
    argparser.add_argument("-i", "--inDir", help="The directory containing the output .root files")
    argparser.add_argument("-o", "--observed", action="store_true", help="If specified, plots the observed limits as well as expected")
    argparser.add_argument("-t", "--theory", nargs="+", choices=["MTS", "M10"], default=["MTS", "M10"], help="Which theory curves to plot.")
    argparser.add_argument("-n", "--name", help="A tag to label output plots with. Filenames will be limits_<name>.png/pdf")
    args = argparser.parse_args()

    return args


#Extract values from root files. Returns dictionary with: obs, exp0, exp+1, exp-1, exp+2, exp-2
def read_limits(filename):
    with uproot.open(filename) as f:
        tree = f["limit"]
        limits = tree["limit"].array(library="np")

    # Combine ordering:
    # 0: -2σ
    # 1: -1σ
    # 2: median
    # 3: +1σ
    # 4: +2σ
    # 5: observed

    return {
        "exp-2": limits[0],
        "exp-1": limits[1],
        "exp0":  limits[2],
        "exp+1": limits[3],
        "exp+2": limits[4],
        "obs":   limits[5],
    }

#Get mass from filename
def extract_mass(filename):
    match = re.search(r"mH([0-9]+(?:\.[0-9]+)?)", filename)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"Could not extract mass from {filename}")



def find_intersections(x1, y1, x2, y2):
    """
    Find intersection points between two curves defined at possibly
    different x points.

    Returns list of x-intersection values.
    """

    # Common x grid (dense for stability)
    xmin = max(min(x1), min(x2))
    xmax = min(max(x1), max(x2))

    x_common = np.linspace(xmin, xmax, 5000)

    # Interpolate both curves
    y1_interp = np.interp(x_common, x1, y1)
    y2_interp = np.interp(x_common, x2, y2)

    diff = y1_interp - y2_interp

    intersections = []

    # Find sign changes
    for i in range(len(diff) - 1):
        if diff[i] * diff[i + 1] < 0:
            # Linear interpolation for zero crossing
            x0 = x_common[i]
            x1_ = x_common[i + 1]
            y0 = diff[i]
            y1_ = diff[i + 1]

            x_cross = x0 - y0 * (x1_ - x0) / (y1_ - y0)
            intersections.append(x_cross)

    return intersections


def plotLimit(args):

    files = sorted(glob.glob(args.inDir + "/higgsCombine*.AsymptoticLimits.mH*.*.root"), key=extract_mass)
    if len(files) == 0:
        print("ERROR: No files found")
        exit(1)

    masses = []
    exp0 = []
    exp_p1 = []
    exp_m1 = []
    exp_p2 = []
    exp_m2 = []
    obs = []

    for f in files:
        # Extract mass from filename (assuming mHXXX in name)
        mass = float(f.split("mH")[1].split(".")[0])
        masses.append(mass)

        limits = read_limits(f)

        
        exp0.append(limits["exp0"])
        exp_p1.append(limits["exp+1"])
        exp_m1.append(limits["exp-1"])
        exp_p2.append(limits["exp+2"])
        exp_m2.append(limits["exp-2"])
        obs.append(limits["obs"])

    # Convert to numpy arrays
    masses = np.array(masses)
    exp0 = np.array(exp0)
    exp_p1 = np.array(exp_p1)
    exp_m1 = np.array(exp_m1)
    exp_p2 = np.array(exp_p2)
    exp_m2 = np.array(exp_m2)
    obs = np.array(obs)

    
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots()

    # Expected median
    ax.plot(masses, exp0, linestyle="--",color="black", label="Expected")

    # 2sigma band (yellow)
    ax.fill_between(masses, exp_m2, exp_p2, color='#ffcc00', label="Expected ±2σ")

    # 1 sigma band (green) - NB: must plot after yellow so it shows up
    ax.fill_between(masses, exp_m1, exp_p1, color='#228b22', label="Expected \u00B11\u03C3")
    
    # Observed
    if args.observed:
        ax.plot(masses, obs, linestyle="-", color="black", label="Observed")

    #Theory
    #theory = np.array([7.766, 5.154, 3.228, 1.996, 1.232, 0.7524, 0.4571, 0.2754, 0.09950, 0.03578, 0.01294, 0.04782, 0.001827, 0.0007319]) #All masses M250-M5000
    if "M10" in args.theory:
        theory = np.array([5.154, 3.228, 1.996, 1.232, 0.7524, 0.4571, 0.2754, 0.09950, 0.03578]) #M500 - M3000 only
        ax.plot(masses, theory, linestyle='-.', color = "magenta", label=r"Theory $\Lambda$=10 TeV")
    if "MTS" in args.theory:
        thMTaustar = [1000, 1500, 2000, 2500, 3000]#, 3500, 4000, 4500, 5000]
        sigXS_mTaustar = np.array([4.330e-09, 3.945e-10, 5.921e-11, 1.155e-11, 2.692e-12])#, 7.030e-13, 2.003e-13, 6.219e-14, 2.036e-14])
        sigXS_mTaustar *= 1e12
        ax.plot(thMTaustar, sigXS_mTaustar, linestyle='-.', color = "blue", label=r"Theory $\Lambda=m_{\tau^*}$")

    ax.set_xlabel(r"$m_{\tau^*}$ GeV")
    ax.set_ylabel(r"$\sigma B(\tau^* \rightarrow \tau Z)   [fb]$")
    hep.cms.label(ax=ax, lumi="158", com="13 and 13.6")

    ax.set_yscale("log")
    ax.legend(loc="upper right", frameon=False)
    plt.tight_layout()

    if args.name:
        plt.savefig(f"limits_{args.name}.png")
        plt.savefig(f"limits_{args.name}.pdf")
    else:
        plt.savefig("limits.png")
        plt.savefig("limits.pdf")
    plt.show()


    if "M10" in args.theory:
        exp_int_1 = find_intersections(masses, exp0, masses, theory)
        if args.observed:
            obs_int_1 = find_intersections(masses, obs,  masses, theory)
        print("\n=== For Lambda = 10 TeV ===")
        for x in exp_int_1:
            print(f"Expected limit m_taustar > {x:.0f} GeV at 95% CL")
        if args.observed:
            for x in obs_int_1:
                print(f"Observed limit m_taustar > {x:.0f} GeV at 95% CL")

    if "MTS" in args.theory:
        exp_int_2 = find_intersections(masses, exp0, thMTaustar, sigXS_mTaustar)
        if args.observed:
            obs_int_2 = find_intersections(masses, obs,  thMTaustar, sigXS_mTaustar)
        print("\n=== For Lambda = m_taustar ===")
        for x in exp_int_2:
            print(f"Expected limit m_taustar > {x:.0f} GeV at 95% CL")
        if args.observed:
            for x in obs_int_2:
                print(f"Observed limit m_taustar > {x:.0f} GeV at 95% CL")


if __name__ == "__main__":
    args = parseArgs()
    plotLimit(args)
