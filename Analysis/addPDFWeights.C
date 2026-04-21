// Macro to add PDF weights to nanoAODtrees
// calcAlphas, calcRenomrmWeight, and calcFacorizeWeight lightly modified from versions sent by Carlos at https://cms-pub-talk.web.cern.ch/t/comments-on-anv7/6774/3

// Compilation instuctions:
/*
  This macro requires both ROOT and the LHAPDF library so must be compiled against both.
  To compile using ROOT on LPC:

run after settign up environment:  lhapdf-config --cflags --ldflags     to get the paths necessary for compilation
      and linking against LHAPDF. The paths for run2 and run3 examples are included below


For Run 2:
  - sing
  - Set up a CMS env (>= CMSSW_10_6_X )
  - start root:    root
  - in root, run :  gSystem->AddIncludePath(" -I/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/lhapdf/6.2.1-pafccj3/include ")     where the path matches the include path from the lhapdf-config
  - in root, run : gSystem->AddLinkedLibs("-L/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/lhapdf/6.2.1-pafccj3/lib -lLHAPDF")   where the path matches the include path from the lhapdf-config
  - in root, compile this script:    .L pdfWeightAdder.C+
  - The functions below can now be run


For Run 3:
  - Set up a CMS env (e.g. CMSSW_14_1_1)
  - root
  - >  gSystem->AddIncludePath(" -I/cvmfs/cms.cern.ch/el9_amd64_gcc12/external/lhapdf/6.4.0-4aa384870ea6380250957dc033c78953/include ")
  - >  gSystem->AddLinkedLibs("-L/cvmfs/cms.cern.ch/el9_amd64_gcc12/external/lhapdf/6.4.0-4aa384870ea6380250957dc033c78953/lib -lLHAPDF")
  - >  .L pdfWeightAdder.C+
  - >  pdfWeightAdder("<YEAR>")
*/

#include "LHAPDF/LHAPDF.h"
#include "LHAPDF/Reweighting.h"
#include <cmath>
#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"

using namespace LHAPDF;

void addPDFWeights(TString filename, int nQCD, PDF* nomPDF, PDF* varPDFs[]);
double calcAlphas(double q2);
double calcRenormWeight(double q2, int up_or_dn, int nQCD);
double calcFactorizWeight(LHAPDF::PDF* pdf, double id1, double id2, double x1, double x2, double q2, int up_or_dn);


void pdfWeightAdder(TString year)
{   

    int nomPDFN;
    int nVars;
    if (year == "2022" || year == "2022post" || year == "2023" || year == "2023post" || year == "2024")
        nomPDFN = 325500;  
    else
        nomPDFN = 303600;

    //Get the PDFs
    PDF* nomPDF = LHAPDF::mkPDF(nomPDFN); 
    PDF* varPDFs[100];
    for (int i = 0; i< 100; i++)
    {
        varPDFs[i] = LHAPDF::mkPDF(nomPDFN + 1 + i);
    }
    
    //Add the weights to each file
    cout << "\nBeginning " << year << "..." << endl;
    TString masses[14] = {"m250","m500","m750","m1000","m1250","m1500","m1750","m2000","m2500","m3000","m3500","m4000","m4500","m5000"};

    for (int fN = 0; fN < 14; fN++)
    {
        //TString filename = "root://cmsxrootd.fnal.gov//store/user/bbarton/TaustarToTauTauZ/SignalMC/SigPFNano/"+year+"/V2/taustarToTauZ_"+masses[fN]+"_"+year+".root";
        TString filename = "../Data/SignalMC/WithPDFWeights/"+year+"/V2p1/taustarToTauZ_"+masses[fN]+"_"+year+".root";
        cout << "\tAdding weights to file:  " << filename << endl;
        addPDFWeights(filename, 0, nomPDF, varPDFs);
    }
}


/* Reads in nominal weighting information from the Events tree in filename and calculates and stores new weights in the tree
    TString filename : the name of the root file to be read, relative to FILEPATH_BASE. This file will be updated in place
    int nQCD : the number of QCD vertices (i.e. ggq, qqgg, etc) in the diagram
*/
void addPDFWeights(TString filename, int nQCD, PDF* nomPDF, PDF* varPDFs[])
{
    TFile* file = TFile::Open(filename, "UPDATE");
    TTree* tree = (TTree*) file->Get("Events");
    if (tree == NULL)
        {
            cout << "File " << filename << " could not be read or does not contain a readable tree" << endl;
            exit(-1);
        }

    //Set up storage of new weights
    double alphas;
    double renormWeights[2]; //Up, down
    //double factorizWeights[200];
    double factWeightUp, factWeightDown;
    double weightsForVar[100]; 
    double factWeightsRMSs[2]; // Up, down
    double varWeightsRMS;
    double varWeightsErr;
    int nVars = 100;
    TBranch *b_alphas = tree->Branch("PDFWeights_alphas", &alphas, "PDFWeights_alphas/D");
    TBranch *b_renormWeights = tree->Branch("PDFWeights_renormWeights", renormWeights, "PDFWeights_renormWeights[2]/D");
    //TBranch *b_nVarsUD = tree->Branch("PDFWeights_nVarsUD", &nVarsUD, "PDFWeights_nVarsUD/i");
    TBranch *b_nVars = tree->Branch("PDFWeights_nVars", &nVars, "PDFWeights_nVars/i");
    //TBranch *b_factorizeWeights = tree->Branch("PDFWeights_factorizeWeights", factorizWeights, "PDFWeights_factorizeWeights[200]/D");
    //TBranch *b_weightsForVar = tree->Branch("PDFWeights_weightsForVar", weightsForVar, "PDFWeights_weightsForVar[100]/D");
    TBranch *b_factWeightsRMSs = tree->Branch("PDFWeights_factWeightsRMSs", factWeightsRMSs, "PDFWeights_factWeightsRMSs[2]/D");
    TBranch *b_varWeightsRMS = tree->Branch("PDFWeights_varWeightsRMS", &varWeightsRMS, "PDFWeights_varWeightsRMS/D");
    TBranch *b_varWeightsErr = tree->Branch("PDFWeights_varWeightsErr", &varWeightsErr, "PDFWeights_varWeightsErr/D");

    const int VAR_UP = 1;
    const int VAR_DOWN = -1;
    float scalePDF, x1, x2; //The existing variables in the tree that we'll need to calc the new weights
    int id1, id2;
    
    tree->SetBranchAddress("Generator_id1", &id1);
    tree->SetBranchAddress("Generator_id2", &id2);
    tree->SetBranchAddress("Generator_scalePDF", &scalePDF);
    tree->SetBranchAddress("Generator_x1", &x1);
    tree->SetBranchAddress("Generator_x2", &x2);
    int nEntries = tree->GetEntries();

    
    for (int entryN = 0; entryN < nEntries; entryN++)
    {
        //Get the existing values from the tree
        tree->GetEntry(entryN);


	
        //Calc the new weights
        alphas = calcAlphas(scalePDF);
        renormWeights[0] = calcRenormWeight(scalePDF, VAR_UP, nQCD); 
        renormWeights[1] = calcRenormWeight(scalePDF, VAR_DOWN, nQCD); 

	factWeightsRMSs[0] = 0;
	factWeightsRMSs[1] = 0;
	varWeightsRMS = 0;
       
	for (int varN = 0; varN < 100; varN++) 
	{
	    factWeightUp = calcFactorizWeight(varPDFs[varN], id1, id2, x1, x2, scalePDF, VAR_UP);
	    factWeightDown = calcFactorizWeight(varPDFs[varN], id1, id2, x1, x2, scalePDF, VAR_DOWN);
	    
	    factWeightsRMSs[0] += (factWeightUp * factWeightUp);
	    factWeightsRMSs[1] += (factWeightDown * factWeightDown);

            // weight using https://lhapdf.hepforge.org/group__reweight__double.html, one per replica.
            weightsForVar[varN] = LHAPDF::weightxxQ(id1, id2, x1, x2, scalePDF, nomPDF, varPDFs[varN]); 
            varWeightsRMS += (weightsForVar[varN] * weightsForVar[varN]);
        }
	
        //Calculate the RMS's
        factWeightsRMSs[0] /= 100;
        factWeightsRMSs[1] /= 100;
	if (factWeightsRMSs[0] < 0 || (factWeightsRMSs[0] != factWeightsRMSs[0]))
	  factWeightsRMSs[0] = 1
	if (factWeightsRMSs[1] < 0 || (factWeightsRMSs[1] != factWeightsRMSs[1]))
          factWeightsRMSs[1] = 1
        factWeightsRMSs[0] = sqrt(factWeightsRMSs[0]);
        factWeightsRMSs[1] = sqrt(factWeightsRMSs[1]);
        varWeightsRMS /= 100;
	if (varWeightsRMS < 0 || (varWeightsRMS != varWeightsRMS)) // Protect against very rare nan's
	  varWeightsRMS = 1;
        varWeightsRMS = sqrt(varWeightsRMS);


        //Calculated the error on the varWeightsRMS according to eqn 6.4 from https://arxiv.org/pdf/2203.05506.pdf
        //Need the values in sorted order
        int arrSize = sizeof(weightsForVar) / sizeof(weightsForVar[0]);
        sort(weightsForVar, weightsForVar + arrSize);
        double weight16 = weightsForVar[15];
        double weight84 = weightsForVar[83];
        varWeightsErr = (weight84 - weight16) / 2.0;
        if (varWeightsErr < 0 || (varWeightsErr != varWeightsErr))
            varWeightsErr = 0;

        //Fill the tree
        b_alphas->Fill();
        b_renormWeights->Fill();
        //b_factorizeWeights->Fill();
        //b_weightsForVar->Fill();
        //b_nVarsUD->Fill();
        b_nVars->Fill();
        b_factWeightsRMSs->Fill();
        b_varWeightsRMS->Fill();
        b_varWeightsErr->Fill();
    }
    
    tree->Write("", TObject::kOverwrite); // save only the new version of the tree
	
}

// q2 == Generator_scalePDF in NanoAOD
double calcAlphas(double q2) 
{ 
    double mZ = 91.2; //Z boson mass in the NNPDF31_nnlo_as_0118 docs (http://lhapdfsets.web.cern.ch/lhapdfsets/current/NNPDF31_nnlo_as_0118/NNPDF31_nnlo_as_0118.info )
    double alphas_mZ = 0.118; //alpha_s evaluated at Z boson mass, based on the NNPDF31_nnlo_as_0118 docs (http://lhapdfsets.web.cern.ch/lhapdfsets/current/NNPDF31_nnlo_as_0118/NNPDF31_nnlo_as_0118.info )
    int nFlavors = 5; //effective number of flavors
    double b0 = (33 - 2.0 * nFlavors) / (12 * M_PI); 
    return alphas_mZ / (1 + alphas_mZ * b0 * std::log(q2 / std::pow(mZ,2))); // alphas evolution
}

// Will always be 1 for electroweak processes at LO
// number of QCD vertices (including both cubic and quartic e.g. qqg, ggqq, etc) 
double calcRenormWeight(double q2, int up_or_dn, int nQCD) 
{ 
    if (nQCD == 0) //Time saving check since we will exponentiate by nQCD as the last step
        return 1;

    double k2;
    if ( up_or_dn ==  1 )
        k2 = 4; // 2*q ==> 4*q2
    else if ( up_or_dn == -1 )
        k2 = 0.25; // 0.5*q ==> 0.25*q2
    else {
      throw std::invalid_argument("up_or_dn must be -1 or 1");
    }
    
    double alphas_old = calcAlphas(q2);
    double alphas_new = calcAlphas(k2*q2);
 
    return std::pow(alphas_new / alphas_old, nQCD);
}


double calcFactorizWeight(LHAPDF::PDF* pdf, double id1, double id2, double x1, double x2, double q2, int up_or_dn) 
{
    double k2;
    if ( up_or_dn ==  1 )
        k2 = 4; // 2*q ==> 4*q2
    else if ( up_or_dn == -1 )
        k2 = 0.25; // 0.5*q ==> 0.25*q2
    else {
        throw std::invalid_argument("up_or_dn must be -1 or 1");
    }

    double pdf1old = pdf->xfxQ2(id1,x1,q2);
    double pdf2old = pdf->xfxQ2(id2,x2,q2);
    double pdf1new = pdf->xfxQ2(id1,x1,k2*q2);
    double pdf2new = pdf->xfxQ2(id2,x2,k2*q2);
    double weight = (pdf1new * pdf2new) / (pdf1old * pdf2old);

    return weight;
}
