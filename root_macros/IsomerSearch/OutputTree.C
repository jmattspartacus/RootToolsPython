#define OutputTree_cxx
int cloverIndex[12] = {0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2};

#include "OutputTree.h"
#include <TH2.h>
#include <TStyle.h>

void OutputTree::Begin(TTree * /*tree*/)
{
  
   TString option = GetOption();
}

void OutputTree::SlaveBegin(TTree * /*tree*/)
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
   fOutputTree->Branch("dE",&dE_out,"dE/D");
   fOutputTree->Branch("ToF",&ToF_out,"ToF/D");
   fOutputTree->Branch("ion_x",&pos_x_out,"ion_x/D");
   fOutputTree->Branch("ion_y",&pos_y_out,"ion_y/D");
   fOutputTree->Branch("Zed",&Zed_out,"Zed/I");
   fOutputTree->Branch("AMass",&AMass_out,"AMass/I");
   fOutputTree->Branch("fit_energy",&fit_energy_,"fit_energy/D");
   fOutputTree->Branch("clover_mult",&clover_mult_out,"clover_mult/I");
   fOutputTree->Branch("clover_E",&clover_E_out);
   fOutputTree->Branch("clover_rawE",&clover_rawE_out);
   fOutputTree->Branch("clover_T",&clover_T_out);
   fOutputTree->Branch("cloverGG_E1",&clover_GG_E1_out);
   fOutputTree->Branch("cloverGG_T1",&clover_GG_T1_out);
   fOutputTree->Branch("cloverGG_E2",&clover_GG_E2_out);
   fOutputTree->Branch("cloverGG_T2",&clover_GG_T2_out);
   fOutputTree->Branch("clover_ch",&clover_ch_out);
   //fOutputTree->Branch("clover_bato",&clover_bato_);
   fOutputTree->Branch("cloverAB_mult",&clover_AB_mult_out,"cloverAB_mult/I");
   fOutputTree->Branch("cloverAB_E",&clover_AB_E_out);
   fOutputTree->Branch("cloverAB_T",&clover_AB_T_out);
   fOutputTree->Branch("cloverABGG_E1",&clover_GG_AB_E1_out);
   fOutputTree->Branch("cloverABGG_T1",&clover_GG_AB_T1_out);
   fOutputTree->Branch("cloverABGG_E2",&clover_GG_AB_E2_out);
   fOutputTree->Branch("cloverABGG_T2",&clover_GG_AB_T2_out);
   fOutputTree->Branch("cloverAB_ch",&clover_AB_ch_out);
   fOutputTree->SetDirectory(fOutputFile);
   fOutputTree->AutoSave();

   gDirectory = savedir;
   TString option = GetOption();

}

Bool_t OutputTree::Process(Long64_t entry)
{
   fReader.SetLocalEntry(entry);

   dE_out=-999;
   ToF_out=-999;
   Zed_out=-999;
   AMass_out=-999;
   pos_x_out=-999;
   pos_y_out=-999;
   ts_out=-999;
   int NumOfCloverEvent=0;
   int NumOfCloverABEvent=0;
   clover_E_out.clear();
   clover_rawE_out.clear();
   clover_T_out.clear();
   clover_Twc_out.clear();
   clover_ch_out.clear();
   clover_AB_E_out.clear();
   clover_AB_Twc_out.clear();
   clover_AB_T_out.clear();
   clover_AB_ch_out.clear();
   clover_GG_AB_E1_out.clear();
   clover_GG_AB_T1_out.clear();
   clover_GG_AB_E2_out.clear();
   clover_GG_AB_T2_out.clear();
   clover_GG_E1_out.clear();
   clover_GG_T1_out.clear();
   clover_GG_E2_out.clear();
   clover_GG_T2_out.clear();

   dE_out  = *dE;
   ts_out  = *ts;
   ToF_out = *ToF;
   Zed_out = *Zed;
   //bool CloverEvent=false;
   for(unsigned int i=0; i<clover_E.GetSize(); i++){
      clover_E_out.push_back(clover_E.At(i));
      clover_rawE_out.push_back(clover_rawE.At(i));
      clover_T_out.push_back(clover_Twc.At(i));
      clover_ch_out.push_back(clover_ch.At(i));
      int cloverDetNum = clover_ch.At(i);
      NumOfCloverEvent++;
   }
   clover_mult_out=NumOfCloverEvent;
   for(int i=0; i<NumOfCloverEvent; i++){
      for(int j=0; j<NumOfCloverEvent; j++){
         if(i==j) continue;
         clover_GG_E1_out.push_back(clover_E_out[i]);
         clover_GG_T1_out.push_back(clover_T_out[i]);
         clover_GG_E2_out.push_back(clover_E_out[j]);
         clover_GG_T2_out.push_back(clover_T_out[j]);
      }
   }
   //for clover addback
   for(unsigned int i=0; i<clover_E_out.size(); i++){
      if(clover_E_out[i]<10) continue;
      bool NewClover=true;
      int thisClover = cloverIndex[clover_ch_out[i]];
      for(unsigned int j=0; j<clover_AB_E_out.size(); j++){
         int thatClover = cloverIndex[clover_AB_ch_out[j]];
         if(thisClover==thatClover){
            NewClover=false;
            clover_AB_E_out[j]+=clover_E_out[i];
            if(clover_E_out[i]>clover_AB_MaxE_out[j]){
               clover_AB_T_out[j]=clover_T_out[i];
               clover_AB_ch_out[j]=clover_ch_out[i];
               clover_AB_MaxE_out[j]=clover_E_out[i];
            }
            break;
         }
      }
      if(NewClover){
         clover_AB_E_out.push_back(clover_E_out[i]);
         clover_AB_MaxE_out.push_back(clover_E_out[i]);
         clover_AB_ch_out.push_back(clover_ch_out[i]);
         clover_AB_T_out.push_back(clover_T_out[i]);
         //cloverAB_bato_.push_back(clover_bato_[i]);
         NumOfCloverABEvent++;
      }
   }
   clover_AB_mult_out=NumOfCloverABEvent;
   for(int i=0; i<NumOfCloverABEvent; i++){
      for(int j=0; j<NumOfCloverABEvent; j++){
         if(i==j) continue;
         clover_GG_AB_E1_out.push_back(clover_AB_E_out[i]);
         clover_GG_AB_T1_out.push_back(clover_AB_T_out[i]);
         clover_GG_AB_E2_out.push_back(clover_AB_E_out[j]);
         clover_GG_AB_T2_out.push_back(clover_AB_T_out[j]);
      }
   }
  

   fOutputTree->Fill();
   
   
   
   return kTRUE;
}

void OutputTree::SlaveTerminate()
{
   

}

void OutputTree::Terminate()
{
  

}