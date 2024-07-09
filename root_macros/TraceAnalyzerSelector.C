#define TraceAnalyzerSelector_cxx


#include "TraceAnalyzerSelector.h"
#include <TH2.h>
#include <TStyle.h>

void TraceAnalyzerSelector::Begin(TTree * /*tree*/)
{
   TString option = GetOption();
   output_file_name_ = "test_tree_output.root";
}

void TraceAnalyzerSelector::SlaveBegin(TTree * /*tree*/)
{

   TString option = GetOption();
   if(option.EqualTo("")){
      output_file_name_ = "test_tree_output.root";
   }else{
      output_file_name_ = option.Data();
   }

   auto savedir = gDirectory;
   if (fProofFile) delete fProofFile;
   //TString msg = TString::Format("test here: %s", output_file_name_.c_str());
   //if (gProofServ) gProofServ->SendAsynMessage(msg);
   fProofFile = new TProofOutputFile(output_file_name_.c_str(), "M");
   fProofFile->SetOutputFileName(output_file_name_.c_str());
   if (fOutputFile) delete fOutputFile;
   fOutputFile = fProofFile->OpenFile("RECREATE");
   if (fOutputTree) delete fOutputTree;
   fOutputTree = new TTree("OutputTree", "OutputTree");
   fOutputTree->Branch("ts_low",&ts_low,"ts_low/D");
   fOutputTree->Branch("ts_high",&ts_high,"ts_high/D");
   fOutputTree->Branch("dE",&dE,"dE/D");
   //fOutputTree->Branch("ToF1",&ToF1_,"ToF1/D");
   fOutputTree->Branch("ToF",&ToF,"ToF/D");
   fOutputTree->Branch("ion_x",&ion_x,"ion_x/D");
   fOutputTree->Branch("ion_y",&ion_y,"ion_y/D");
   fOutputTree->Branch("pin1_energy",&pin1_energy,"pin1_energy/D");
   fOutputTree->Branch("pin1_time",&pin1_time,"pin1_time/D");
   fOutputTree->Branch("pin0_energy",&pin0_energy,"pin0_energy/D");
   fOutputTree->Branch("pin0_time",&pin0_time,"pin0_time/D");
   fOutputTree->Branch("tac0",&tac0,"tac0/D");
   fOutputTree->Branch("tac1",&tac1,"tac1/D");
   
   fOutputTree->SetDirectory(fOutputFile);
   fOutputTree->AutoSave();
   gDirectory = savedir;
}

Bool_t TraceAnalyzerSelector::Process(Long64_t entry)
{
   dE.clear();
   ToF.clear();
   pin0_energy.clear();
   pin1_energy.clear();
   pin0_time.clear();
   pin1_time.clear();
   tac0.clear();
   tac1.clear();
   
  

   fReader.SetLocalEntry(entry);
   // want to require implants
   if(*low_gain__energy_.Get() <= 0.0) return kFALSE;
   // now require a front ion signal
   //if (!(*fit_b1__energy_.Get() > 0.0 || *fit_b2__energy_.Get() > 0.0)) return kFALSE;
   // now require that the back veto does not trigger
   if ((*rit_b1__energy_.Get() >= 0.0 || *rit_b2__energy_.Get() >= 0.0)) return kFALSE;
   
   std::size_t sz = pid_vec__tac_1.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__tac_1.At(i); 
      ToF.push_back(tval);
   }

   sz = pid_vec__pin_0_energy.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__pin_0_energy.At(i); 
      dE.push_back(tval);
   }

   sz = pid_vec__pin_1_energy.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__pin_1_energy.At(i); 
      pin1_energy.push_back(tval);
   }

   sz = pid_vec__tac_0.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__tac_0.At(i); 
      tac0.push_back(tval);
   }
   
   sz = pid_vec__tac_1.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__tac_1.At(i); 
      tac1.push_back(tval);
   }

   sz = pid_vec__pin_0_time.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__pin_0_time.At(i); 
      pin0_time.push_back(tval);
   }

   sz = pid_vec__pin_1_time.GetSize();
   for(std::size_t i = 0; i < sz; i++) {
      double tval = pid_vec__pin_1_time.At(i); 
      pin1_time.push_back(tval);
   }
   
   ion_x   = *low_gain__pos_x_;
   ion_y   = *low_gain__pos_y_;
   ts_low  = *external_ts_low_;
   ts_high = *external_ts_high_;
   
   // fill the tree in memory
   fOutputTree->Fill();
   ion_x = -5;
   ion_y = -5;
   ts_low = -1e9;
   ts_high = -1e9;
   return kTRUE;
}

void TraceAnalyzerSelector::SlaveTerminate()
{
   fReader.SetTree((TTree*)nullptr);
   auto savedir = gDirectory;
   fOutputFile->cd();
   fOutputTree->Write();
   fOutput->Add(fProofFile);
   fOutputTree->SetDirectory(0);
   fOutputFile->Close();
   gDirectory = savedir;
}

void TraceAnalyzerSelector::Terminate()
{
   
}