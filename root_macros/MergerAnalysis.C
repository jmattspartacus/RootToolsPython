#define MergerAnalysis_cxx
// The class definition in MergerAnalysis.h has been generated automatically
// by the ROOT utility TTree::MakeSelector(). This class is derived
// from the ROOT class TSelector. For more information on the TSelector
// framework see $ROOTSYS/README/README.SELECTOR or the ROOT User Manual.


// The following methods are defined in this file:
//    Begin():        called every time a loop on the tree starts,
//                    a convenient place to create your histograms.
//    SlaveBegin():   called after Begin(), when on PROOF called only on the
//                    slave servers.
//    Process():      called for each event, in this function you decide what
//                    to read and fill your histograms.
//    SlaveTerminate: called at the end of the loop on the tree, when on PROOF
//                    called only on the slave servers.
//    Terminate():    called at the end of the loop on the tree,
//                    a convenient place to draw/fit your histograms.
//
// To use this file, try the following session on your Tree T:
//
// root> T->Process("MergerAnalysis.C")
// root> T->Process("MergerAnalysis.C","some options")
// root> T->Process("MergerAnalysis.C+")
//


#include "MergerAnalysis.h"
#include <TH2.h>
#include <TStyle.h>
#include "ReadVandleSetup.C"
#include <vector>

//the parameters to remove VANDLE crosstalk
#define CROSSTALKWIDTH 10
#define CROSSTALKWIDTH2 500
#define CROSSTALKBAR 10

double GetBetaGammaWalk(double gammaE){
   if(gammaE<10){
      return 0;
   }else{
      double par0=2591.7;
      double par1=0;
      double par2=-0.544195;
      double par3=20.0743;
      return par0*pow(gammaE-par1,par2)+par3;
   }
}

double GetSpeedOfLight(double qdc){
   return -5.94268e+06*pow(qdc+454.261,-2.27498)+13.4352;
}

double GetCorrectedTOF(double tof, double fp, double idealFp){
   return tof/fp*idealFp;
}

double GetFlightPath(int barNum, double qdc, double tdiff, double pspmt_x, double pspmt_y){
   double vandle_x = VANDLEZ0[barNum]*cos(VANDLERadians[barNum]);
   double vandle_y = VANDLEZ0[barNum]*sin(VANDLERadians[barNum]);
   double SpeedOfLight=GetSpeedOfLight(qdc);
   double vandle_z = tdiff*SpeedOfLight*0.5 + VANDLEXOffset[barNum];
   if(abs(vandle_z)>60) return 0;
   double pspmt_z = 0;
   return sqrt(pow(vandle_x-pspmt_x, 2)+pow(vandle_y-pspmt_y, 2)+pow(vandle_z-pspmt_z, 2));
}


int cloverIndex[12] = {0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2};

void MergerAnalysis::Begin(TTree * /*tree*/)
{
   // The Begin() function is called at the start of the query.
   // When running with PROOF Begin() is only called on the client.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();
   output_file_name_ = "test_tree_output.root";
}

void MergerAnalysis::SlaveBegin(TTree * /*tree*/)
{
   // The SlaveBegin() function is called after the Begin() function.
   // When running with PROOF SlaveBegin() is called on each slave server.
   // The tree argument is deprecated (on PROOF 0 is passed).

   ReadVandleSetup("/home/jchristie/repos/E19044_James/data/medium.dat");
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
   fOutputTree->Branch("dE",&dE_,"dE/D");
   fOutputTree->Branch("ToF",&ToF_,"ToF/D");
   fOutputTree->Branch("beta_x",&beta_x_,"beta_x/D");
   fOutputTree->Branch("beta_y",&beta_y_,"beta_y/D");
   fOutputTree->Branch("ion_x",&ion_x_,"ion_x/D");
   fOutputTree->Branch("ion_y",&ion_y_,"ion_y/D");
   fOutputTree->Branch("Zed",&Zed_,"Zed/I");
   fOutputTree->Branch("AMass",&AMass_,"AMass/I");
   fOutputTree->Branch("betaQdcHighGain",&betaQdcHighGain_,"betaQdcHighGain/D");
   fOutputTree->Branch("betaQdcLowGain",&betaQdcLowGain_,"betaQdcLowGain/D");
   fOutputTree->Branch("betaEnergyHighGain",&betaEnergyHighGain_,"betaEnergyHighGain/D");
   fOutputTree->Branch("betaEnergyLowGain",&betaEnergyLowGain_,"betaEnergyLowGain/D");
   fOutputTree->Branch("fit_energy",&fit_energy_,"fit_energy/D");
   fOutputTree->Branch("dT",&dT_,"dT/D");
   fOutputTree->Branch("dr",&dr_,"dr/D");
   fOutputTree->Branch("clover_mult",&clover_mult_,"clover_mult/I");
   fOutputTree->Branch("clover_E",&clover_E_);
   fOutputTree->Branch("clover_rawE",&clover_rawE_);
   fOutputTree->Branch("clover_T",&clover_T_);
   fOutputTree->Branch("cloverGG_E1",&cloverGG_E1_);
   fOutputTree->Branch("cloverGG_T1",&cloverGG_T1_);
   fOutputTree->Branch("cloverGG_E2",&cloverGG_E2_);
   fOutputTree->Branch("cloverGG_T2",&cloverGG_T2_);
   fOutputTree->Branch("clover_ch",&clover_ch_);
   //fOutputTree->Branch("clover_bato",&clover_bato_);
   fOutputTree->Branch("cloverAB_mult",&cloverAB_mult_,"cloverAB_mult/I");
   fOutputTree->Branch("cloverAB_E",&cloverAB_E_);
   fOutputTree->Branch("cloverAB_T",&cloverAB_T_);
   fOutputTree->Branch("cloverABGG_E1",&cloverABGG_E1_);
   fOutputTree->Branch("cloverABGG_T1",&cloverABGG_T1_);
   fOutputTree->Branch("cloverABGG_E2",&cloverABGG_E2_);
   fOutputTree->Branch("cloverABGG_T2",&cloverABGG_T2_);
   fOutputTree->Branch("cloverAB_ch",&cloverAB_ch_);
   //fOutputTree->Branch("cloverAB_bato",&cloverAB_bato_);
   fOutputTree->Branch("vandle_mult",&vandle_mult_,"vandle_mult/I");
   fOutputTree->Branch("vandle_mult_Neutron",&vandle_mult_Neutron_,"vandle_mult_Neutron/I");
   fOutputTree->Branch("vandle_mult_BKG",&vandle_mult_BKG_,"vandle_mult_BKG/I");
   fOutputTree->Branch("vandle_tof",&vandle_tof_);
   fOutputTree->Branch("vandle_qdc",&vandle_qdc_);
   fOutputTree->Branch("vandle_sqdc",&vandle_sqdc_);
   fOutputTree->Branch("vandle_tdiff",&vandle_tdiff_);
   fOutputTree->Branch("vandle_bar",&vandle_bar_);
   fOutputTree->Branch("vandle_corTof",&vandle_corTof_);
   fOutputTree->Branch("vandle_tofTest",&vandle_tofTest_);
   fOutputTree->Branch("vandle_qdcTest",&vandle_qdcTest_);
   fOutputTree->Branch("vandle_barTest",&vandle_barTest_);
   fOutputTree->SetDirectory(fOutputFile);
   fOutputTree->AutoSave();

   gDirectory = savedir;

}

Bool_t MergerAnalysis::Process(Long64_t entry)
{
   // The Process() function is called for each entry in the tree (or possibly
   // keyed object in the case of PROOF) to be processed. The entry argument
   // specifies which entry in the currently loaded tree is to be processed.
   // When processing keyed objects with PROOF, the object is already loaded
   // and is available via the fObject pointer.
   //
   // This function should contain the \"body\" of the analysis. It can contain
   // simple or elaborate selection criteria, run algorithms on the data
   // of the event and typically fill histograms.
   //
   // The processing can be stopped by calling Abort().
   //
   // Use fStatus to set the return value of TTree::Process().
   //
   // The return value is currently not used.

   fReader.SetLocalEntry(entry);

   dE_=-999;
   ToF_=-999;
   Zed_=-999;
   AMass_=-999;
   dT_=-99999;
   dr_=-99999;
   beta_x_=-999;
   beta_y_=-999;
   ion_x_=-999;
   ion_y_=-999;
   int NumOfCloverEvent=0;
   int NumOfCloverABEvent=0;
   clover_mult_=0;
   clover_E_.clear();
   clover_rawE_.clear();
   clover_T_.clear();
   cloverGG_E1_.clear();
   cloverGG_T1_.clear();
   cloverGG_E2_.clear();
   cloverGG_T2_.clear();
   clover_ch_.clear();
   //clover_bato_.clear();
   cloverAB_mult_=0;
   cloverAB_E_.clear();
   cloverAB_MaxE_.clear();
   cloverAB_T_.clear();
   cloverABGG_E1_.clear();
   cloverABGG_T1_.clear();
   cloverABGG_E2_.clear();
   cloverABGG_T2_.clear();
   cloverAB_ch_.clear();
   //cloverAB_bato_.clear();
   vandle_mult_=0;
   vandle_mult_Neutron_=0;
   vandle_mult_BKG_=0;
   vandle_bar_.clear();
   vandle_qdc_.clear();
   vandle_sqdc_.clear();
   vandle_tof_.clear();
   vandle_tdiff_.clear();
   vandle_corTof_.clear();

   double t_beta = *high_gain__time_;
   betaQdcHighGain_ = *high_gain__qdc_;
   betaQdcLowGain_ = *low_gain__qdc_;
   betaEnergyHighGain_ = *high_gain__energy_;
   betaEnergyLowGain_ = *low_gain__energy_;
   fit_energy_=0;
   double b1 = *fit_b1__energy_;
   if(b1>0){
      fit_energy_+=b1;
   }
   double b2 = *fit_b2__energy_;
   if(b2>0){
      fit_energy_+=b2;
   }
   beta_x_ = *high_gain__pos_x_;
   beta_y_ = *high_gain__pos_y_;

   //bool CloverEvent=false;
   for(unsigned int i=0; i<clover_vec__energy.GetSize(); i++){
      if(clover_vec__cloverHigh.At(i)==1){
         clover_E_.push_back(clover_vec__energy.At(i));
         clover_rawE_.push_back(clover_vec__rawEnergy.At(i));
         double twalk = GetBetaGammaWalk(clover_vec__energy.At(i));
         clover_T_.push_back(clover_vec__time.At(i)-t_beta-twalk);
         clover_ch_.push_back(clover_vec__detNum.At(i));
         int cloverDetNum = clover_vec__detNum.At(i);
         //int batoNum = cloverDetNum/4 * 2;
         //double bato = 0;
         //int batoSize = bato_vec__energy_.GetSize();
         //for(int j=0; j<batoSize; j++){
         //   if(bato_vec__detNum_.At(j)>=batoNum && bato_vec__detNum_.At(j)<=batoNum+1){
         //      bato = bato + bato_vec__energy_.At(j);
         //   }
         //}
         //clover_bato_.push_back(bato);
         NumOfCloverEvent++;
      }
   }
   clover_mult_=NumOfCloverEvent;
   for(int i=0; i<NumOfCloverEvent; i++){
      for(int j=0; j<NumOfCloverEvent; j++){
         if(i==j) continue;
         cloverGG_E1_.push_back(clover_E_[i]);
         cloverGG_T1_.push_back(clover_T_[i]);
         cloverGG_E2_.push_back(clover_E_[j]);
         cloverGG_T2_.push_back(clover_T_[j]);
      }
   }
   //for clover addback
   for(unsigned int i=0; i<clover_E_.size(); i++){
      if(clover_E_[i]<10) continue;
      bool NewClover=true;
      int thisClover = cloverIndex[clover_ch_[i]];
      for(unsigned int j=0; j<cloverAB_E_.size(); j++){
         int thatClover = cloverIndex[cloverAB_ch_[j]];
         if(thisClover==thatClover){
            NewClover=false;
            cloverAB_E_[j]+=clover_E_[i];
            if(clover_E_[i]>cloverAB_MaxE_[j]){
               cloverAB_T_[j]=clover_T_[i];
               cloverAB_ch_[j]=clover_ch_[i];
               cloverAB_MaxE_[j]=clover_E_[i];
            }
            break;
         }
      }
      if(NewClover){
         cloverAB_E_.push_back(clover_E_[i]);
         cloverAB_MaxE_.push_back(clover_E_[i]);
         cloverAB_ch_.push_back(clover_ch_[i]);
         cloverAB_T_.push_back(clover_T_[i]);
         //cloverAB_bato_.push_back(clover_bato_[i]);
         NumOfCloverABEvent++;
      }
   }
   cloverAB_mult_=NumOfCloverABEvent;
   for(int i=0; i<NumOfCloverABEvent; i++){
      for(int j=0; j<NumOfCloverABEvent; j++){
         if(i==j) continue;
         cloverABGG_E1_.push_back(cloverAB_E_[i]);
         cloverABGG_T1_.push_back(cloverAB_T_[i]);
         cloverABGG_E2_.push_back(cloverAB_E_[j]);
         cloverABGG_T2_.push_back(cloverAB_T_[j]);
      }
   }
   unsigned int tmpVandleSize = vandle_vec__tof.GetSize();
   map<double, pair<int, pair<double, double> > > vvct;//vandle vector with cross talk
   map<double, pair<int, pair<double, double> > >::iterator ivvct;
   double tmpV_sqdc;
   for(unsigned int i=0; i<tmpVandleSize; i++){
      int bar = vandle_vec__barNum.At(i);
      double qdc = vandle_vec__qdc.At(i);
      double sqdc = vandle_vec__sQdc.At(i);
      double tof=vandle_vec__tof.At(i);
      double tdiff=vandle_vec__tDiff.At(i);
      tmpV_sqdc=sqdc;
      vvct.insert(std::make_pair(tof, std::make_pair(bar, std::make_pair(qdc, tdiff) ) ) );
   }
   bool NuScater=false;
   int VandleSize=0;
   for(ivvct=vvct.begin(); ivvct!=vvct.end(); ivvct++){
      double tof=ivvct->first;
      int bar=ivvct->second.first;
      double qdc=ivvct->second.second.first;
      double tdiff=ivvct->second.second.second;
      //if(vvct.size()>2){
      //   std::cout<<"tof="<<tof<<", qdc="<<qdc<<", bar="<<bar<< std::endl;
      //}
      bool REALEVT=true;
      for(unsigned int i=0; i<vandle_tof_.size(); i++){
         if(fabs(tof-vandle_tof_[i])<CROSSTALKWIDTH || (fabs(tof-vandle_tof_[i])<CROSSTALKWIDTH2 && abs(bar-vandle_bar_[i])<=CROSSTALKBAR)){
            NuScater=true;
            REALEVT=false;
            break;
         }
      }
      if(REALEVT){
         vandle_tof_.push_back(tof);
         vandle_bar_.push_back(bar);
         vandle_qdc_.push_back(qdc);
         vandle_tdiff_.push_back(tdiff);
         vandle_sqdc_.push_back(tmpV_sqdc);
         VandleSize++;
      }
   }
   vandle_mult_=VandleSize;
   //if(NumOfCloverEvent>0) CloverEvent=true;
   for(unsigned int i=0; i<output_vec__pid_pin0_.GetSize(); i++){
      dE_=output_vec__pid_pin0_.At(i);
      ToF_=output_vec__pid_tac1_.At(i);
      if(F29CUT->IsInside(ToF_, dE_)){
         Zed_=9;
         AMass_=29;
      }else if(F27CUT->IsInside(ToF_, dE_)){
         Zed_=9;
         AMass_=27;
      }else if(F26CUT->IsInside(ToF_, dE_)){
         Zed_=9;
         AMass_=26;
      }else if(Ne29CUT->IsInside(ToF_, dE_)){
         Zed_=10;
         AMass_=29;
      }else if(Ne30CUT->IsInside(ToF_, dE_)){
         Zed_=10;
         AMass_=30;
      }else if(Ne31CUT->IsInside(ToF_, dE_)){
         Zed_=10;
         AMass_=31;
      }else if(Ne32CUT->IsInside(ToF_, dE_)){
         Zed_=10;
         AMass_=32;
      }else if(Na32CUT->IsInside(ToF_, dE_)){
         Zed_=11;
         AMass_=32;
      }else if(Na33CUT->IsInside(ToF_, dE_)){
         Zed_=11;
         AMass_=33;
      }else if(Na34CUT->IsInside(ToF_, dE_)){
         Zed_=11;
         AMass_=34;
      }else if(Na35CUT->IsInside(ToF_, dE_)){
         Zed_=11;
         AMass_=35;
      }else if(Mg36CUT->IsInside(ToF_, dE_)){
         Zed_=12;
         AMass_=36;
      }else if(Mg37CUT->IsInside(ToF_, dE_)){
         Zed_=12;
         AMass_=37;
      }
      double t_ion = output_vec__low_gain__time_.At(i);
      ion_x_ = output_vec__low_gain__pos_x_.At(i);
      ion_y_ = output_vec__low_gain__pos_y_.At(i);
      vandle_mult_Neutron_=0;
      vandle_mult_BKG_=0;
      vandle_tofTest_.clear();
      vandle_qdcTest_.clear();
      vandle_barTest_.clear();
      for(int j=0; j<VandleSize; j++){
         double qdc=vandle_qdc_[j];
         double tof=vandle_tof_[j];
         double tdiff=vandle_tdiff_[j];
         int bar = vandle_bar_[j];
         double fp = GetFlightPath(bar, qdc, tdiff, ion_x_, ion_y_);
         double ctof = GetCorrectedTOF(tof, fp, 105);
         vandle_corTof_.push_back(ctof);
         if(ctof>25 && ctof<250){
            vandle_mult_Neutron_++;
            vandle_tofTest_.push_back(ctof);
            vandle_qdcTest_.push_back(qdc);
            vandle_barTest_.push_back(bar);
         }
         if(ctof>250 && ctof<475){
            vandle_mult_BKG_++;
            vandle_tofTest_.push_back(ctof-225);
            vandle_qdcTest_.push_back(qdc);
            vandle_barTest_.push_back(bar);
         }
      }

      dT_ = (t_beta - t_ion)/1e6;
      dr_ = sqrt((ion_x_-beta_x_)*(ion_x_-beta_x_)+(ion_y_-beta_y_)*(ion_y_-beta_y_));
      fOutputTree->Fill();
      dE_=-999;
      ToF_=-999;
      Zed_=-999;
      AMass_=-999;
      ion_x_=-999;
      ion_y_=-999;
      dT_=-99999;
      dr_=-99999;
      //vandle_bar_.clear();
      //vandle_qdc_.clear();
      //vandle_sqdc_.clear();
      //vandle_tof_.clear();
      //vandle_tdiff_.clear();
      vandle_corTof_.clear();
   }

   return kTRUE;
}

void MergerAnalysis::SlaveTerminate()
{
   // The SlaveTerminate() function is called after all entries or objects
   // have been processed. When running with PROOF SlaveTerminate() is called
   // on each slave server.

   fReader.SetTree((TTree*)nullptr);
   auto savedir = gDirectory;
   fOutputFile->cd();
   fOutputTree->Write();
   fOutput->Add(fProofFile);
   fOutputTree->SetDirectory(0);
   fOutputFile->Close();
   gDirectory = savedir;
}

void MergerAnalysis::Terminate()
{
   // The Terminate() function is the last function to be called during
   // a query. It always runs on the client, it can be used to present
   // the results graphically or save the results to file.

}
