//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Mon Apr 24 11:18:29 2023 by ROOT version 6.18/04
// from TTree pspmt/pspmt
// found on file: /SCRATCH/DScratch5/e19044/vandle/merger/TraceAnalyzer/29F/29F_012.root
//////////////////////////////////////////////////////////

#ifndef TraceAnalyzerSelector_h
#define TraceAnalyzerSelector_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TProofOutputFile.h>
#include "TProofServ.h"

// Headers needed by this particular selector
#include "PspmtData.hpp"

#include "PaassRootStruct.hpp"

#include <vector>



class TraceAnalyzerSelector : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<unsigned int> fUniqueID = {fReader, "fUniqueID"};
   TTreeReaderValue<unsigned int> fBits = {fReader, "fBits"};
   TTreeReaderValue<ULong64_t> event_number_ = {fReader, "event_number_"};
   //TTreeReaderValue<string>    file_name_ = {fReader, "file_name_"};
   TTreeReaderValue<ULong64_t> external_ts_high_ = {fReader, "external_ts_high_"};
   TTreeReaderValue<ULong64_t> external_ts_low_ = {fReader, "external_ts_low_"};
   TTreeReaderValue<Double_t> rit_b1__energy_ = {fReader, "rit_b1_.energy_"};
   TTreeReaderValue<Double_t> rit_b1__time_ = {fReader, "rit_b1_.time_"};
   TTreeReaderValue<Double_t> rit_b2__energy_ = {fReader, "rit_b2_.energy_"};
   TTreeReaderValue<Double_t> rit_b2__time_ = {fReader, "rit_b2_.time_"};
   TTreeReaderValue<Double_t> fit_b1__energy_ = {fReader, "fit_b1_.energy_"};
   TTreeReaderValue<Double_t> fit_b1__time_ = {fReader, "fit_b1_.time_"};
   TTreeReaderValue<Double_t> fit_b2__energy_ = {fReader, "fit_b2_.energy_"};
   TTreeReaderValue<Double_t> fit_b2__time_ = {fReader, "fit_b2_.time_"};
   TTreeReaderValue<Double_t> dyn_single__energy_ = {fReader, "dyn_single_.energy_"};
   TTreeReaderValue<Double_t> dyn_single__time_ = {fReader, "dyn_single_.time_"};
   TTreeReaderValue<Double_t> high_gain__pos_x_ = {fReader, "high_gain_.pos_x_"};
   TTreeReaderValue<Double_t> high_gain__pos_y_ = {fReader, "high_gain_.pos_y_"};
   TTreeReaderValue<Int_t>    high_gain__valid_ = {fReader, "high_gain_.valid_"};
   TTreeReaderValue<Double_t> high_gain__qdc_ = {fReader, "high_gain_.qdc_"};
   TTreeReaderValue<Double_t> high_gain__energy_ = {fReader, "high_gain_.energy_"};
   TTreeReaderValue<Double_t> high_gain__time_ = {fReader, "high_gain_.time_"};
   TTreeReaderValue<Double_t> high_gain__energy_sum_ = {fReader, "high_gain_.energy_sum_"};
   TTreeReaderValue<Double_t> high_gain__xa_energy_ = {fReader, "high_gain_.xa_energy_"};
   TTreeReaderValue<Double_t> high_gain__xb_energy_ = {fReader, "high_gain_.xb_energy_"};
   TTreeReaderValue<Double_t> high_gain__ya_energy_ = {fReader, "high_gain_.ya_energy_"};
   TTreeReaderValue<Double_t> high_gain__yb_energy_ = {fReader, "high_gain_.yb_energy_"};
   TTreeReaderValue<Double_t> high_gain__xa_qdc_ = {fReader, "high_gain_.xa_qdc_"};
   TTreeReaderValue<Double_t> high_gain__xb_qdc_ = {fReader, "high_gain_.xb_qdc_"};
   TTreeReaderValue<Double_t> high_gain__ya_qdc_ = {fReader, "high_gain_.ya_qdc_"};
   TTreeReaderValue<Double_t> high_gain__yb_qdc_ = {fReader, "high_gain_.yb_qdc_"};
   TTreeReaderValue<Double_t> low_gain__pos_x_ = {fReader, "low_gain_.pos_x_"};
   TTreeReaderValue<Double_t> low_gain__pos_y_ = {fReader, "low_gain_.pos_y_"};
   TTreeReaderValue<Int_t>    low_gain__valid_ = {fReader, "low_gain_.valid_"};
   TTreeReaderValue<Double_t> low_gain__qdc_ = {fReader, "low_gain_.qdc_"};
   TTreeReaderValue<Double_t> low_gain__energy_ = {fReader, "low_gain_.energy_"};
   TTreeReaderValue<Double_t> low_gain__time_ = {fReader, "low_gain_.time_"};
   TTreeReaderValue<Double_t> low_gain__energy_sum_ = {fReader, "low_gain_.energy_sum_"};
   TTreeReaderValue<Double_t> low_gain__xa_energy_ = {fReader, "low_gain_.xa_energy_"};
   TTreeReaderValue<Double_t> low_gain__xb_energy_ = {fReader, "low_gain_.xb_energy_"};
   TTreeReaderValue<Double_t> low_gain__ya_energy_ = {fReader, "low_gain_.ya_energy_"};
   TTreeReaderValue<Double_t> low_gain__yb_energy_ = {fReader, "low_gain_.yb_energy_"};
   TTreeReaderValue<Double_t> low_gain__xa_qdc_ = {fReader, "low_gain_.xa_qdc_"};
   TTreeReaderValue<Double_t> low_gain__xb_qdc_ = {fReader, "low_gain_.xb_qdc_"};
   TTreeReaderValue<Double_t> low_gain__ya_qdc_ = {fReader, "low_gain_.ya_qdc_"};
   TTreeReaderValue<Double_t> low_gain__yb_qdc_ = {fReader, "low_gain_.yb_qdc_"};
   TTreeReaderValue<Double_t> pid_pin0_ = {fReader, "pid_pin0_"};
   TTreeReaderValue<Double_t> pid_tac1_ = {fReader, "pid_tac1_"};
   TTreeReaderValue<Double_t> pid_tof1_ = {fReader, "pid_tof1_"};
   TTreeReaderValue<ULong64_t> pixie_event_num_ = {fReader, "pixie_event_num_"};
   TTreeReaderArray<vector<double>> bato_vec__pQDCsums = {fReader, "bato_vec_.pQDCsums"};
   TTreeReaderArray<Double_t> bato_vec__time = {fReader, "bato_vec_.time"};
   TTreeReaderArray<Double_t> bato_vec__energy = {fReader, "bato_vec_.energy"};
   TTreeReaderArray<Double_t> bato_vec__qdc = {fReader, "bato_vec_.qdc"};
   TTreeReaderArray<Int_t>    bato_vec__detNum = {fReader, "bato_vec_.detNum"};
   TTreeReaderArray<Double_t> clover_vec__energy = {fReader, "clover_vec_.energy"};
   TTreeReaderArray<Double_t> clover_vec__rawEnergy = {fReader, "clover_vec_.rawEnergy"};
   TTreeReaderArray<Double_t> clover_vec__time = {fReader, "clover_vec_.time"};
   TTreeReaderArray<Int_t>    clover_vec__detNum = {fReader, "clover_vec_.detNum"};
   TTreeReaderArray<Int_t>    clover_vec__cloverNum = {fReader, "clover_vec_.cloverNum"};
   TTreeReaderArray<Bool_t>   clover_vec__cloverHigh = {fReader, "clover_vec_.cloverHigh"};
   TTreeReaderArray<Double_t> pid_vec__rfq_time = {fReader, "pid_vec_.rfq_time"};
   TTreeReaderArray<Double_t> pid_vec__fp_time = {fReader, "pid_vec_.fp_time"};
   TTreeReaderArray<Double_t> pid_vec__pinCfd_time = {fReader, "pid_vec_.pinCfd_time"};
   TTreeReaderArray<Double_t> pid_vec__pin_0_time = {fReader, "pid_vec_.pin_0_time"};
   TTreeReaderArray<Double_t> pid_vec__pin_1_time = {fReader, "pid_vec_.pin_1_time"};
   TTreeReaderArray<Double_t> pid_vec__pin_0_energy = {fReader, "pid_vec_.pin_0_energy"};
   TTreeReaderArray<Double_t> pid_vec__pin_1_energy = {fReader, "pid_vec_.pin_1_energy"};
   TTreeReaderArray<Double_t> pid_vec__tac_0 = {fReader, "pid_vec_.tac_0"};
   TTreeReaderArray<Double_t> pid_vec__tac_1 = {fReader, "pid_vec_.tac_1"};
   TTreeReaderArray<Double_t> pid_vec__tof0 = {fReader, "pid_vec_.tof0"};
   TTreeReaderArray<Double_t> pid_vec__tof1 = {fReader, "pid_vec_.tof1"};
   //TTreeReaderArray<string>    vandle_vec__barType = {fReader, "vandle_vec_.barType"};
   TTreeReaderArray<Double_t> vandle_vec__tof = {fReader, "vandle_vec_.tof"};
   TTreeReaderArray<Double_t> vandle_vec__corTof = {fReader, "vandle_vec_.corTof"};
   TTreeReaderArray<Double_t> vandle_vec__qdcPos = {fReader, "vandle_vec_.qdcPos"};
   TTreeReaderArray<Double_t> vandle_vec__qdc = {fReader, "vandle_vec_.qdc"};
   TTreeReaderArray<Int_t>    vandle_vec__barNum = {fReader, "vandle_vec_.barNum"};
   TTreeReaderArray<Double_t> vandle_vec__tAvg = {fReader, "vandle_vec_.tAvg"};
   TTreeReaderArray<Double_t> vandle_vec__tDiff = {fReader, "vandle_vec_.tDiff"};
   TTreeReaderArray<Double_t> vandle_vec__wcTavg = {fReader, "vandle_vec_.wcTavg"};
   TTreeReaderArray<Double_t> vandle_vec__wcTdiff = {fReader, "vandle_vec_.wcTdiff"};
   TTreeReaderArray<Int_t>    vandle_vec__sNum = {fReader, "vandle_vec_.sNum"};
   TTreeReaderArray<Int_t>    vandle_vec__vMulti = {fReader, "vandle_vec_.vMulti"};
   TTreeReaderArray<Double_t> vandle_vec__sTime = {fReader, "vandle_vec_.sTime"};
   TTreeReaderArray<Double_t> vandle_vec__sQdc = {fReader, "vandle_vec_.sQdc"};

   double ts_low;
   double ts_high;
   std::vector<double> dE;
   std::vector<double> ToF;
   double ion_x;
   double ion_y;
   std::vector<double> pin1_energy;
   std::vector<double> pin1_time;
   std::vector<double> pin0_energy;
   std::vector<double> pin0_time;
   std::vector<double> tac0;
   std::vector<double> tac1;


   

   

   TTree* fOutputTree = nullptr;
   TFile* fOutputFile = nullptr;
   TProofOutputFile* fProofFile = nullptr;
   std::string output_file_name_;





   TraceAnalyzerSelector(TTree * /*tree*/ =0) { }
   virtual ~TraceAnalyzerSelector() { }
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

   ClassDef(TraceAnalyzerSelector,0);

};

#endif

#ifdef TraceAnalyzerSelector_cxx
void TraceAnalyzerSelector::Init(TTree *tree)
{
   fReader.SetTree(tree);
}

Bool_t TraceAnalyzerSelector::Notify()
{
   return kTRUE;
}


#endif // #ifdef TraceAnalyzerSelector_cxx
