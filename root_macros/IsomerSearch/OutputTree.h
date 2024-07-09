//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Thu Jun  1 11:47:10 2023 by ROOT version 6.18/04
// from TTree OutputTree/OutputTree
// found on file: 25F.root
//////////////////////////////////////////////////////////

#ifndef OutputTree_h
#define OutputTree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

// Headers needed by this particular selector
#include <vector>



class OutputTree : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<Double_t> ts = {fReader, "ts"};
   TTreeReaderValue<Double_t> dE = {fReader, "dE"};
   TTreeReaderValue<Double_t> ToF = {fReader, "ToF"};
   TTreeReaderValue<Int_t> Zed = {fReader, "Zed"};
   TTreeReaderValue<Int_t> IfAnodeFull = {fReader, "IfAnodeFull"};
   TTreeReaderValue<Int_t> IfDynodeHigh = {fReader, "IfDynodeHigh"};
   TTreeReaderValue<Double_t> pos_x = {fReader, "pos_x"};
   TTreeReaderValue<Double_t> pos_y = {fReader, "pos_y"};
   TTreeReaderValue<Int_t> AMass = {fReader, "AMass"};
   TTreeReaderValue<Double_t> dynode_E_low = {fReader, "dynode_E_low"};
   TTreeReaderValue<Double_t> dynode_E_high = {fReader, "dynode_E_high"};
   TTreeReaderValue<Double_t> anode_xa_high = {fReader, "anode_xa_high"};
   TTreeReaderValue<Double_t> anode_xb_high = {fReader, "anode_xb_high"};
   TTreeReaderValue<Double_t> anode_ya_high = {fReader, "anode_ya_high"};
   TTreeReaderValue<Double_t> anode_yb_high = {fReader, "anode_yb_high"};
   TTreeReaderValue<Double_t> anode_xa_low = {fReader, "anode_xa_low"};
   TTreeReaderValue<Double_t> anode_xb_low = {fReader, "anode_xb_low"};
   TTreeReaderValue<Double_t> anode_ya_low = {fReader, "anode_ya_low"};
   TTreeReaderValue<Double_t> anode_yb_low = {fReader, "anode_yb_low"};
   TTreeReaderValue<Double_t> FIT_b1_E = {fReader, "FIT_b1_E"};
   TTreeReaderValue<Double_t> FIT_b2_E = {fReader, "FIT_b2_E"};
   TTreeReaderArray<double> clover_E = {fReader, "clover_E"};
   TTreeReaderArray<double> clover_rawE = {fReader, "clover_rawE"};
   TTreeReaderArray<double> clover_T = {fReader, "clover_T"};
   TTreeReaderArray<double> clover_Twc = {fReader, "clover_Twc"};
   TTreeReaderArray<double> clover_ch = {fReader, "clover_ch"};

   std::vector<double> clover_E_out;
   std::vector<double> clover_rawE_out;
   std::vector<double> clover_T_out;
   std::vector<double> clover_Twc_out;
   std::vector<int> clover_ch_out;

   std::vector<double> clover_AB_E_out;
   std::vector<double> clover_AB_MaxE_out;
   std::vector<double> clover_AB_Twc_out;
   std::vector<double> clover_AB_T_out;
   std::vector<int> clover_AB_ch_out;

   std::vector<double> clover_GG_AB_E1_out;
   std::vector<double> clover_GG_AB_T1_out;
   std::vector<double> clover_GG_AB_E2_out;
   std::vector<double> clover_GG_AB_T2_out;

   std::vector<double> clover_GG_E1_out;
   std::vector<double> clover_GG_T1_out;
   std::vector<double> clover_GG_E2_out;
   std::vector<double> clover_GG_T2_out;
   int clover_mult_out;
   int clover_AB_mult_out;
   double ts_out;
   double dE_out;
   double ToF_out;
   int Zed_out;
   int IfAnodeFull_out;
   int IfDynodeHigh_out;
   double pos_x_out;
   double pos_y_out;
   int AMass_out;
   double dynode_E_low_out;
   double dynode_E_high_out;
   double anode_xa_high_out;
   double anode_xb_high_out;
   double anode_ya_high_out;
   double anode_yb_high_out;
   double anode_xa_low_out;
   double anode_xb_low_out;
   double anode_ya_low_out;
   double anode_yb_low_out;
   double FIT_b1_E_out;
   double FIT_b2_E_out;



   OutputTree(TTree * /*tree*/ =0) { }
   virtual ~OutputTree() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   ClassDef(OutputTree,0);

};

#endif

#ifdef OutputTree_cxx
void OutputTree::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   fReader.SetTree(tree);
}

Bool_t OutputTree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef OutputTree_cxx
