//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Jan 27 11:25:47 2021 by ROOT version 6.18/04
// from TTree mergedBeta/mergedBeta
// found on file: MergedROOT/29F/29F_012_r0.2.root
//////////////////////////////////////////////////////////

#ifndef MergerAnalysis_h
#define MergerAnalysis_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TProofOutputFile.h>
#include "TProofServ.h"
#include "MakeTCutG.C"

// Headers needed by this particular selector
#include "OutputTreeData.hpp"

#include "PaassRootStruct.hpp"

#include <vector>



class MergerAnalysis : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<unsigned int> fUniqueID = {fReader, "input_.fUniqueID"};
   TTreeReaderValue<unsigned int> fBits = {fReader, "input_.fBits"};
   TTreeReaderValue<ULong64_t> event_number_ = {fReader, "input_.event_number_"};
   TTreeReaderValue<string> file_name_ = {fReader, "input_.file_name_"};
   TTreeReaderValue<ULong64_t> external_ts_high_ = {fReader, "input_.external_ts_high_"};
   TTreeReaderValue<ULong64_t> external_ts_low_ = {fReader, "input_.external_ts_low_"};
   TTreeReaderValue<Double_t> rit_b1__energy_ = {fReader, "input_.rit_b1_.energy_"};
   TTreeReaderValue<Double_t> rit_b1__time_ = {fReader, "input_.rit_b1_.time_"};
   TTreeReaderValue<Double_t> rit_b2__energy_ = {fReader, "input_.rit_b2_.energy_"};
   TTreeReaderValue<Double_t> rit_b2__time_ = {fReader, "input_.rit_b2_.time_"};
   TTreeReaderValue<Double_t> fit_b1__energy_ = {fReader, "input_.fit_b1_.energy_"};
   TTreeReaderValue<Double_t> fit_b1__time_ = {fReader, "input_.fit_b1_.time_"};
   TTreeReaderValue<Double_t> fit_b2__energy_ = {fReader, "input_.fit_b2_.energy_"};
   TTreeReaderValue<Double_t> fit_b2__time_ = {fReader, "input_.fit_b2_.time_"};
   TTreeReaderValue<Double_t> dyn_single__energy_ = {fReader, "input_.dyn_single_.energy_"};
   TTreeReaderValue<Double_t> dyn_single__time_ = {fReader, "input_.dyn_single_.time_"};
   TTreeReaderValue<Double_t> high_gain__pos_x_ = {fReader, "input_.high_gain_.pos_x_"};
   TTreeReaderValue<Double_t> high_gain__pos_y_ = {fReader, "input_.high_gain_.pos_y_"};
   TTreeReaderValue<Int_t> high_gain__valid_ = {fReader, "input_.high_gain_.valid_"};
   TTreeReaderValue<Double_t> high_gain__qdc_ = {fReader, "input_.high_gain_.qdc_"};
   TTreeReaderValue<Double_t> high_gain__energy_ = {fReader, "input_.high_gain_.energy_"};
   TTreeReaderValue<Double_t> high_gain__time_ = {fReader, "input_.high_gain_.time_"};
   TTreeReaderValue<Double_t> high_gain__energy_sum_ = {fReader, "input_.high_gain_.energy_sum_"};
   TTreeReaderValue<Double_t> high_gain__xa_energy_ = {fReader, "input_.high_gain_.xa_energy_"};
   TTreeReaderValue<Double_t> high_gain__xb_energy_ = {fReader, "input_.high_gain_.xb_energy_"};
   TTreeReaderValue<Double_t> high_gain__ya_energy_ = {fReader, "input_.high_gain_.ya_energy_"};
   TTreeReaderValue<Double_t> high_gain__yb_energy_ = {fReader, "input_.high_gain_.yb_energy_"};
   TTreeReaderValue<Double_t> high_gain__xa_qdc_ = {fReader, "input_.high_gain_.xa_qdc_"};
   TTreeReaderValue<Double_t> high_gain__xb_qdc_ = {fReader, "input_.high_gain_.xb_qdc_"};
   TTreeReaderValue<Double_t> high_gain__ya_qdc_ = {fReader, "input_.high_gain_.ya_qdc_"};
   TTreeReaderValue<Double_t> high_gain__yb_qdc_ = {fReader, "input_.high_gain_.yb_qdc_"};
   TTreeReaderValue<Double_t> low_gain__pos_x_ = {fReader, "input_.low_gain_.pos_x_"};
   TTreeReaderValue<Double_t> low_gain__pos_y_ = {fReader, "input_.low_gain_.pos_y_"};
   TTreeReaderValue<Int_t> low_gain__valid_ = {fReader, "input_.low_gain_.valid_"};
   TTreeReaderValue<Double_t> low_gain__qdc_ = {fReader, "input_.low_gain_.qdc_"};
   TTreeReaderValue<Double_t> low_gain__energy_ = {fReader, "input_.low_gain_.energy_"};
   TTreeReaderValue<Double_t> low_gain__time_ = {fReader, "input_.low_gain_.time_"};
   TTreeReaderValue<Double_t> low_gain__energy_sum_ = {fReader, "input_.low_gain_.energy_sum_"};
   TTreeReaderValue<Double_t> low_gain__xa_energy_ = {fReader, "input_.low_gain_.xa_energy_"};
   TTreeReaderValue<Double_t> low_gain__xb_energy_ = {fReader, "input_.low_gain_.xb_energy_"};
   TTreeReaderValue<Double_t> low_gain__ya_energy_ = {fReader, "input_.low_gain_.ya_energy_"};
   TTreeReaderValue<Double_t> low_gain__yb_energy_ = {fReader, "input_.low_gain_.yb_energy_"};
   TTreeReaderValue<Double_t> low_gain__xa_qdc_ = {fReader, "input_.low_gain_.xa_qdc_"};
   TTreeReaderValue<Double_t> low_gain__xb_qdc_ = {fReader, "input_.low_gain_.xb_qdc_"};
   TTreeReaderValue<Double_t> low_gain__ya_qdc_ = {fReader, "input_.low_gain_.ya_qdc_"};
   TTreeReaderValue<Double_t> low_gain__yb_qdc_ = {fReader, "input_.low_gain_.yb_qdc_"};
   TTreeReaderArray<unsigned int> output_vec__fUniqueID = {fReader, "output_vec_.fUniqueID"};
   TTreeReaderArray<unsigned int> output_vec__fBits = {fReader, "output_vec_.fBits"};
   TTreeReaderArray<ULong64_t> output_vec__event_number_ = {fReader, "output_vec_.event_number_"};
   TTreeReaderArray<string> output_vec__file_name_ = {fReader, "output_vec_.file_name_"};
   TTreeReaderArray<ULong64_t> output_vec__external_ts_high_ = {fReader, "output_vec_.external_ts_high_"};
   TTreeReaderArray<ULong64_t> output_vec__external_ts_low_ = {fReader, "output_vec_.external_ts_low_"};
   TTreeReaderArray<Double_t> output_vec__rit_b1__energy_ = {fReader, "output_vec_.rit_b1_.energy_"};
   TTreeReaderArray<Double_t> output_vec__rit_b1__time_ = {fReader, "output_vec_.rit_b1_.time_"};
   TTreeReaderArray<Double_t> output_vec__rit_b2__energy_ = {fReader, "output_vec_.rit_b2_.energy_"};
   TTreeReaderArray<Double_t> output_vec__rit_b2__time_ = {fReader, "output_vec_.rit_b2_.time_"};
   TTreeReaderArray<Double_t> output_vec__fit_b1__energy_ = {fReader, "output_vec_.fit_b1_.energy_"};
   TTreeReaderArray<Double_t> output_vec__fit_b1__time_ = {fReader, "output_vec_.fit_b1_.time_"};
   TTreeReaderArray<Double_t> output_vec__fit_b2__energy_ = {fReader, "output_vec_.fit_b2_.energy_"};
   TTreeReaderArray<Double_t> output_vec__fit_b2__time_ = {fReader, "output_vec_.fit_b2_.time_"};
   TTreeReaderArray<Double_t> output_vec__dyn_single__energy_ = {fReader, "output_vec_.dyn_single_.energy_"};
   TTreeReaderArray<Double_t> output_vec__dyn_single__time_ = {fReader, "output_vec_.dyn_single_.time_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__pos_x_ = {fReader, "output_vec_.high_gain_.pos_x_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__pos_y_ = {fReader, "output_vec_.high_gain_.pos_y_"};
   TTreeReaderArray<Int_t> output_vec__high_gain__valid_ = {fReader, "output_vec_.high_gain_.valid_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__qdc_ = {fReader, "output_vec_.high_gain_.qdc_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__energy_ = {fReader, "output_vec_.high_gain_.energy_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__time_ = {fReader, "output_vec_.high_gain_.time_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__energy_sum_ = {fReader, "output_vec_.high_gain_.energy_sum_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__xa_energy_ = {fReader, "output_vec_.high_gain_.xa_energy_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__xb_energy_ = {fReader, "output_vec_.high_gain_.xb_energy_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__ya_energy_ = {fReader, "output_vec_.high_gain_.ya_energy_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__yb_energy_ = {fReader, "output_vec_.high_gain_.yb_energy_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__xa_qdc_ = {fReader, "output_vec_.high_gain_.xa_qdc_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__xb_qdc_ = {fReader, "output_vec_.high_gain_.xb_qdc_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__ya_qdc_ = {fReader, "output_vec_.high_gain_.ya_qdc_"};
   TTreeReaderArray<Double_t> output_vec__high_gain__yb_qdc_ = {fReader, "output_vec_.high_gain_.yb_qdc_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__pos_x_ = {fReader, "output_vec_.low_gain_.pos_x_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__pos_y_ = {fReader, "output_vec_.low_gain_.pos_y_"};
   TTreeReaderArray<Int_t> output_vec__low_gain__valid_ = {fReader, "output_vec_.low_gain_.valid_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__qdc_ = {fReader, "output_vec_.low_gain_.qdc_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__energy_ = {fReader, "output_vec_.low_gain_.energy_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__time_ = {fReader, "output_vec_.low_gain_.time_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__energy_sum_ = {fReader, "output_vec_.low_gain_.energy_sum_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__xa_energy_ = {fReader, "output_vec_.low_gain_.xa_energy_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__xb_energy_ = {fReader, "output_vec_.low_gain_.xb_energy_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__ya_energy_ = {fReader, "output_vec_.low_gain_.ya_energy_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__yb_energy_ = {fReader, "output_vec_.low_gain_.yb_energy_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__xa_qdc_ = {fReader, "output_vec_.low_gain_.xa_qdc_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__xb_qdc_ = {fReader, "output_vec_.low_gain_.xb_qdc_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__ya_qdc_ = {fReader, "output_vec_.low_gain_.ya_qdc_"};
   TTreeReaderArray<Double_t> output_vec__low_gain__yb_qdc_ = {fReader, "output_vec_.low_gain_.yb_qdc_"};
   TTreeReaderArray<Double_t> output_vec__pid_pin0_ = {fReader, "output_vec_.pid_pin0_"};
   TTreeReaderArray<Double_t> output_vec__pid_tac1_ = {fReader, "output_vec_.pid_tac1_"};
   //TTreeReaderArray<Double_t> bato_vec__time_ = {fReader, "bato_vec_.time"};
   //TTreeReaderArray<Double_t> bato_vec__energy_ = {fReader, "bato_vec_.energy"};
   //TTreeReaderArray<Double_t> bato_vec__qdc_ = {fReader, "bato_vec_.qdc"};
   //TTreeReaderArray<Double_t> bato_vec__detNum_ = {fReader, "bato_vec_.detNum"};
   TTreeReaderArray<Double_t> clover_vec__energy = {fReader, "clover_vec_.energy"};
   TTreeReaderArray<Double_t> clover_vec__rawEnergy = {fReader, "clover_vec_.rawEnergy"};
   TTreeReaderArray<Double_t> clover_vec__time = {fReader, "clover_vec_.time"};
   TTreeReaderArray<Int_t> clover_vec__detNum = {fReader, "clover_vec_.detNum"};
   TTreeReaderArray<Int_t> clover_vec__cloverNum = {fReader, "clover_vec_.cloverNum"};
   TTreeReaderArray<Bool_t> clover_vec__cloverHigh = {fReader, "clover_vec_.cloverHigh"};
   TTreeReaderArray<string> vandle_vec__barType = {fReader, "vandle_vec_.barType"};
   TTreeReaderArray<Double_t> vandle_vec__tof = {fReader, "vandle_vec_.tof"};
   TTreeReaderArray<Double_t> vandle_vec__corTof = {fReader, "vandle_vec_.corTof"};
   TTreeReaderArray<Double_t> vandle_vec__qdcPos = {fReader, "vandle_vec_.qdcPos"};
   TTreeReaderArray<Double_t> vandle_vec__qdc = {fReader, "vandle_vec_.qdc"};
   TTreeReaderArray<Int_t> vandle_vec__barNum = {fReader, "vandle_vec_.barNum"};
   TTreeReaderArray<Double_t> vandle_vec__tAvg = {fReader, "vandle_vec_.tAvg"};
   TTreeReaderArray<Double_t> vandle_vec__tDiff = {fReader, "vandle_vec_.tDiff"};
   TTreeReaderArray<Double_t> vandle_vec__wcTavg = {fReader, "vandle_vec_.wcTavg"};
   TTreeReaderArray<Double_t> vandle_vec__wcTdiff = {fReader, "vandle_vec_.wcTdiff"};
   TTreeReaderArray<Int_t> vandle_vec__sNum = {fReader, "vandle_vec_.sNum"};
   TTreeReaderArray<Int_t> vandle_vec__vMulti = {fReader, "vandle_vec_.vMulti"};
   TTreeReaderArray<Double_t> vandle_vec__sTime = {fReader, "vandle_vec_.sTime"};
   TTreeReaderArray<Double_t> vandle_vec__sQdc = {fReader, "vandle_vec_.sQdc"};

   double dE_;
   double ToF_;
   int Zed_;
   int AMass_;
   double beta_x_;
   double beta_y_;
   double ion_x_;
   double ion_y_;
   double dr_;//spacial distance
   double dT_;//time distance
   double betaQdcHighGain_;
   double betaQdcLowGain_;
   double betaEnergyHighGain_;
   double betaEnergyLowGain_;
   double fit_energy_;
   int clover_mult_;
   std::vector<double> clover_E_;
   std::vector<double> clover_rawE_;
   std::vector<double> clover_T_;
   std::vector<double> cloverGG_E1_;
   std::vector<double> cloverGG_T1_;
   std::vector<double> cloverGG_E2_;
   std::vector<double> cloverGG_T2_;
   std::vector<int> clover_ch_;
   std::vector<double> clover_bato_;
   int cloverAB_mult_;
   std::vector<double> cloverAB_E_;
   std::vector<double> cloverAB_MaxE_;
   std::vector<double> cloverAB_T_;
   std::vector<double> cloverABGG_E1_;
   std::vector<double> cloverABGG_T1_;
   std::vector<double> cloverABGG_E2_;
   std::vector<double> cloverABGG_T2_;
   std::vector<int> cloverAB_ch_;
   std::vector<double> cloverAB_bato_;
   int vandle_mult_;
   std::vector<double> vandle_tof_;
   std::vector<double> vandle_qdc_;
   std::vector<double> vandle_sqdc_;
   std::vector<double> vandle_tdiff_;
   std::vector<int> vandle_bar_;
   std::vector<double> vandle_corTof_;
   int vandle_mult_Neutron_;//tof between 25 ~ 250 ns
   int vandle_mult_BKG_;//tof between 275 ~ 500 ns
   std::vector<double> vandle_tofTest_;//test branch for 2n channel
   std::vector<double> vandle_qdcTest_;
   std::vector<double> vandle_barTest_;
   TTree* fOutputTree = nullptr;
   TFile* fOutputFile = nullptr;
   TProofOutputFile* fProofFile = nullptr;
   std::string output_file_name_;
   TCutG* F29CUT;
   TCutG* F27CUT;
   TCutG* F26CUT;
   TCutG* Ne29CUT;
   TCutG* Ne30CUT;
   TCutG* Ne31CUT;
   TCutG* Ne32CUT;
   TCutG* Na32CUT;
   TCutG* Na33CUT;
   TCutG* Na34CUT;
   TCutG* Na35CUT;
   TCutG* Mg36CUT;
   TCutG* Mg37CUT;


   std::string cut_dir="/home/jchristie/repos/E19044_James/32Na/CUT/";

   MergerAnalysis(TTree * /*tree*/ =0) {
      F29CUT  = ReadPIDCut((cut_dir + std::string("F29CUT.txt")).c_str());
      F27CUT  = ReadPIDCut((cut_dir + std::string("F27CUT.txt")).c_str());
      F26CUT  = ReadPIDCut((cut_dir + std::string("F26CUT.txt")).c_str());
      Ne28CUT = ReadPIDCut((cut_dir + std::string("Ne28CUT.txt")).c_str());
      Ne29CUT = ReadPIDCut((cut_dir + std::string("Ne29CUT.txt")).c_str());
      Ne30CUT = ReadPIDCut((cut_dir + std::string("Ne30CUT.txt")).c_str());
      Ne31CUT = ReadPIDCut((cut_dir + std::string("Ne31CUT.txt")).c_str());
      Ne32CUT = ReadPIDCut((cut_dir + std::string("Ne32CUT.txt")).c_str());
      Na32CUT = ReadPIDCut((cut_dir + std::string("Na32CUT.txt")).c_str());
      Na33CUT = ReadPIDCut((cut_dir + std::string("Na33CUT.txt")).c_str());
      Na34CUT = ReadPIDCut((cut_dir + std::string("Na34CUT.txt")).c_str());
      Na35CUT = ReadPIDCut((cut_dir + std::string("Na35CUT.txt")).c_str());
      Mg36CUT = ReadPIDCut((cut_dir + std::string("Mg36CUT.txt")).c_str());
      Mg37CUT = ReadPIDCut((cut_dir + std::string("Mg37CUT.txt")).c_str());
      //TString msg = TString::Format("Load cut at %p", F29PID);
   }
   virtual ~MergerAnalysis() { }
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

   ClassDef(MergerAnalysis,0);

};

#endif

#ifdef MergerAnalysis_cxx
void MergerAnalysis::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   fReader.SetTree(tree);
}

Bool_t MergerAnalysis::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef MergerAnalysis_cxx
