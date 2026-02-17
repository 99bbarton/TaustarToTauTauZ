#Make the Brazil plot


import glob
import numpy as np
import uproot
import matplotlib.pyplot as plt
import cmsstyle as CMS

# --------------------------------------------------
# User configuration
# --------------------------------------------------

# Pattern for your Combine output files
# Example: higgsCombineTest.AsymptoticLimits.mH*.root
file_pattern = "Outputs/higgsCombineTest.AsymptoticLimits.mH*.*.root"

# Label for x-axis (mass or parameter)
x_label = "m_{"#tau^*} [GeV]"

# Label for y-axis
y_label = "95% CL upper limit on σ/σ_{theory}"

# Luminosity label
lumi = 138  # fb^-1

# --------------------------------------------------
# Helper function to extract limits from file
# --------------------------------------------------

def read_limits(filename):
    """
    Reads expected and observed limits from a Combine AsymptoticLimits ROOT file.
    Returns dictionary with:
        obs, exp0, exp+1, exp-1, exp+2, exp-2
    """

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

# --------------------------------------------------
# Collect files and extract limits
# --------------------------------------------------

files = sorted(glob.glob(file_pattern))

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

# --------------------------------------------------
# Plotting (CMS style)
# --------------------------------------------------

CMS.set_style()
fig, ax = plt.subplots()

# 2σ band (yellow)
ax.fill_between(masses, exp_m2, exp_p2, color="yellow", label="Expected ±2σ")

# 1σ band (green)
ax.fill_between(masses, exp_m1, exp_p1, color="green", label="Expected ±1σ")

# Expected median
ax.plot(masses, exp0, linestyle="--",color="black", label="Expected")

# Observed
ax.plot(masses, obs, linestyle="-", color="black", label="Observed")

# Axes labels
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)

ax.set_yscale("log")

# CMS label
CMS.cmslabel(ax=ax, lumi=lumi, year=2022, label="Preliminary")

# Legend
ax.legend(loc="upper right", frameon=False)

plt.tight_layout()
plt.savefig("limits.png", dpi=300)
plt.savefig("limits.pdf")
plt.show()



