{
    void GetFieldFromEventsInChain(TCut &cut, TChain &chain, TString &filename, TString &fieldtoget, TString &fieldunits)
    {
        int maxbin = chain.GetEntries();
        double field = 0;
        chain.SetBranchAddress(fieldtoget, &field);
        double dE;
        double ToF;
        double beta_x;
        double beta_y;
        double ion_x;
        double ion_y;
        double Zed;
        double AMass;
        double betaQdcHighGain;
        double betaQdcLowGain;
        double betaEnergyHighGain;
        double betaEnergyLowGain;
        double fit_energy;
        double dT;
        double dr;
        double clover_mult;
        double clover_E;
        double clover_T;
        double cloverGG_E1;
        double cloverGG_T1;
        double cloverGG_E2;
        double cloverGG_T2;
        double clover_ch;
        double clover_bato;
        double cloverAB_mult;
        double cloverAB_E;
        double cloverAB_T;
        double cloverABGG_E1;
        double cloverABGG_T1;
        double cloverABGG_E2;
        double cloverABGG_T2;
        double cloverAB_ch;
        double cloverAB_bato;
        double vandle_mult;
        double vandle_tof;
        double vandle_qdc;
        double vandle_sqdc;
        double vandle_tdiff;
        double vandle_bar;
        double vandle_corTof;

        chain.SetBranchAddress("dE", &dE);
        chain.SetBranchAddress("ToF", &ToF);
        chain.SetBranchAddress("beta_x", &beta_x);
        chain.SetBranchAddress("beta_y", &beta_y);
        chain.SetBranchAddress("ion_x", &ion_x);
        chain.SetBranchAddress("ion_y", &ion_y);
        chain.SetBranchAddress("Zed", &Zed);
        chain.SetBranchAddress("AMass", &AMass);
        chain.SetBranchAddress("betaQdcHighGain", &betaQdcHighGain);
        chain.SetBranchAddress("betaQdcLowGain", &betaQdcLowGain);
        chain.SetBranchAddress("betaEnergyHighGain", &betaEnergyHighGain);
        chain.SetBranchAddress("betaEnergyLowGain", &betaEnergyLowGain);
        chain.SetBranchAddress("fit_energy", &fit_energy);
        chain.SetBranchAddress("dT", &dT);
        chain.SetBranchAddress("dr", &dr);
        chain.SetBranchAddress("clover_mult", &clover_mult);
        chain.SetBranchAddress("clover_E", &clover_E);
        chain.SetBranchAddress("clover_T", &clover_T);
        chain.SetBranchAddress("cloverGG_E1", &cloverGG_E1);
        chain.SetBranchAddress("cloverGG_T1", &cloverGG_T1);
        chain.SetBranchAddress("cloverGG_E2", &cloverGG_E2);
        chain.SetBranchAddress("cloverGG_T2", &cloverGG_T2);
        chain.SetBranchAddress("clover_ch", &clover_ch);
        chain.SetBranchAddress("clover_bato", &clover_bato);
        chain.SetBranchAddress("cloverAB_mult", &cloverAB_mult);
        chain.SetBranchAddress("cloverAB_E", &cloverAB_E);
        chain.SetBranchAddress("cloverAB_T", &cloverAB_T);
        chain.SetBranchAddress("cloverABGG_E1", &cloverABGG_E1);
        chain.SetBranchAddress("cloverABGG_T1", &cloverABGG_T1);
        chain.SetBranchAddress("cloverABGG_E2", &cloverABGG_E2);
        chain.SetBranchAddress("cloverABGG_T2", &cloverABGG_T2);
        chain.SetBranchAddress("cloverAB_ch", &cloverAB_ch);
        chain.SetBranchAddress("cloverAB_bato", &cloverAB_bato);
        chain.SetBranchAddress("vandle_mult", &vandle_mult);
        chain.SetBranchAddress("vandle_tof", &vandle_tof);
        chain.SetBranchAddress("vandle_qdc", &vandle_qdc);
        chain.SetBranchAddress("vandle_sqdc", &vandle_sqdc);
        chain.SetBranchAddress("vandle_tdiff", &vandle_tdiff);
        chain.SetBranchAddress("vandle_bar", &vandle_bar);
        chain.SetBranchAddress("vandle_corTof", &vandle_corTof);

        std::ofstream out(filename);
        out << fieldtoget << "(" << fieldunits << ")" << "\n";
        auto cuttitle = cut.GetTitle();
        for (int i = 0; i < maxbin; i++)
        {   
            if(i % 10000 == 0)
            {
                std::cout << i << " of " << maxbin << "\t\r" << std::flush;
            }
            chain.GetEntry(i);
            if(chain.Query("", cuttitle, "", 1, i)->GetRowCount() == 0)
            {
                continue;
            }
            out << field << "\n";
            //chain.Print();
            //std::cout << i << " " << maxbin << std::endl;
            //break;
        }
        out.close();
    }
    TChain chain("OutputTree");
    chain.Add("/SCRATCH/DScratch5/e19044/vandle/simpleROOT/29F_mergerTest_r10.root");
    TString unitString("ms");
    TString fieldtoget("dT");
    TString addbackFile("addbacktimes.txt");
    TString noaddbackFile("noaddbacktimes.txt");
    TCut addbackCut("cloverAB_T < 500 && cloverAB_T > 0 && dT > 0 && dT < 5 && dr < 0.35&& betaEnergyLowGain>0 && betaEnergyLowGain<600 && cloverAB_E > 172 && cloverAB_E < 177");
    TCut noAddbackCut("clover_T < 500 && clover_T > 0 && dT > 0 && dT < 5 && dr < 0.35&& betaEnergyLowGain>0 && betaEnergyLowGain<600 && clover_E > 172 && clover_E < 177");
    GetFieldFromEventsInChain(addbackCut, chain, addbackFile, fieldtoget, unitString);
    GetFieldFromEventsInChain(noAddbackCut, chain, noaddbackFile, fieldtoget, unitString);
}