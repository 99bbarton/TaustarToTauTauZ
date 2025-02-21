

import os
import sys

if len(sys.argv) != 2:
    print("USAGE: python3 rename.py YEAR")
    exit(1)

    
for filename in os.listdir():
    if filename.endswith(".root"):
        #xprint(filename)
        newName = "taustarToTauZ_" +filename[filename.find("__m")+2: filename.find(".root")] + "_" + sys.argv[1] + ".root"
        #print(newName)
        os.system("mv " + filename +  " " + newName)
