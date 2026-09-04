#include <TFile.h>
#include <TTree.h>
#include <TString.h>

#include <fstream>
#include <iostream>

void skimFiles(const char* fileList)
{
    std::ifstream infile(fileList);
    if (!infile.is_open()) {
        std::cerr << "Error: could not open file list " << fileList << std::endl;
        return;
    }

    TString inputFileName;
    //const TString selection = "(PDFWeights_varWeightsRMS == PDFWeights_varWeightsRMS)"; ////////////////////////////////////// FIX BACK TO CHANNEL_ISCAND OR
    const TString selection = "(ETau_isCand || MuTau_isCand || TauTau_isCand)";

    while (infile >> inputFileName) {

        std::cout << "Processing: " << inputFileName << std::endl;

        // Open input file
        TFile *inFile = TFile::Open("root://cmsxrootd.fnal.gov//store/user/bbarton/TaustarToTauTauZ/Data/JobOutputs/28Aug2026/2024/" + inputFileName, "READ");
	
        if (!inFile || inFile->IsZombie()) {
            std::cerr << "  Could not open input file!" << std::endl;
            delete inFile;
            continue;
        }
	

        // Get the tree
        TTree *inTree = (TTree*)inFile->Get("Events");
        if (!inTree) {
            std::cerr << "  Tree 'Events' not found!" << std::endl;
            inFile->Close();
            delete inFile;
            continue;
        }
	if (inTree->GetEntries() == 0)
	  {
	    std::cerr << "No entries in " << inputFileName << std::endl;
	    inFile->Close();
            delete inFile;
            continue;
	  }
	if (!inTree->GetBranch("ObjCnt_nBTags"))
	  {
	    std::cerr << "\t\tNo objcnt branch" <<std::endl;
	    continue;
	  }

	inTree->AddBranchToCache("*", true);

        // Construct output file name
        TString outFileName = inputFileName;
        //outFileName.ReplaceAll(".root", "_skim.root"); ////////////////////////////////////////////////////////////////////////// READDME FOR MC/DAT

        // Create output file
        TFile *outFile = TFile::Open("./Test/"+outFileName, "RECREATE");

	TTree *outTree;
        // Skim the tree
	try {
	  outTree = inTree->CopyTree(selection);
	}
	catch(...)
	  {
	    std::cerr << "\t\tFailed!" <<std::endl;
	    continue;
	  }
	  


	/*Bool_t ETau_isCand, MuTau_isCand, TauTau_isCand;

	inTree->SetBranchAddress("ETau_isCand", &ETau_isCand);
	inTree->SetBranchAddress("MuTau_isCand", &MuTau_isCand);
	inTree->SetBranchAddress("TauTau_isCand", &TauTau_isCand);

	TTree *outTree = inTree->CloneTree(0); // empty clone

	Long64_t nEntries = inTree->GetEntries();
	for (Long64_t i = 0; i < nEntries; ++i) {
	  inTree->GetEntry(i);

	  if (ETau_isCand || MuTau_isCand || TauTau_isCand) {
	    outTree->Fill();
	  }
	  }*/
	
	
	
        // Write output
        outFile->cd();
        outTree->Write("Events");
        outFile->Close();

        // Cleanup
        inFile->Close();
        delete outFile;
        delete inFile;

        std::cout << "  Written: " << outFileName << std::endl;
    }

    infile.close();
    std::cout << "Done skimming all files." << std::endl;
}
