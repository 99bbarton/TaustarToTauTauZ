#Utility script to read nanoAOD producer scripts and build a variable list for use as a reference
#Reads the .py files in ../NanoAOD-tools/python/postprocessing/modules/
# and outputs a .csv file and prints to the console the columns: Variable Name, Type, Description, Source File
# for all producers which add branches to the trees

import os



with open("../branchList.csv", "w+") as outFile:
    outFile.write("Branch Name, Type, Description, Source\n")
    print("\n")
    print("{:<20}".format("Branch Name") + " | " + "{:^4}".format("Type") + " | " + "{:<80}".format("Description") + " | " + "{:<20}".format("Source File"))
    print("-"*130)

    for filename in os.listdir("../NanoAOD-tools/python/postprocessing/modules/"):
        if not filename.endswith(".py"):
            continue

        with open("../NanoAOD-tools/python/postprocessing/modules/"+filename,"r") as inFile:
            lines = inFile.readlines()
            for line in lines:
                strtIdx = line.find("self.out.branch(")
                if strtIdx >= 0 and line.find("#self.") < 0:
                    strtIdx = strtIdx + 16
                    subStr = line[strtIdx:]
                    quoteIdxs = [i for i in range(len(subStr)) if subStr.startswith('"', i)] # Find indices of a ll " in line
                    if len(quoteIdxs) != 6: 
                        print('WARNING: Unrecognized line format. Number of " found was not 6. Skipping...')
                        print("Line was: " + subStr)
                        continue
                    var = subStr[quoteIdxs[0]+1:quoteIdxs[1]]
                    varType = subStr[quoteIdxs[2]+1:quoteIdxs[3]]
                    varDesc = subStr[quoteIdxs[4]+1:quoteIdxs[5]]
                    outFile.write(var + ", " + varType + ", " + varDesc + ", " + filename + "\n")
                    print("{:<20}".format(var) + " | " + "{:^4}".format(varType) + " | " + "{:<80}".format(varDesc) + " | " + "{:<20}".format(filename))
    print("-"*130 + "\n")
