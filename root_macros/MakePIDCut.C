#include <TCutG.h>

void MakePIDCut(TCutG *cutg, const char* cutname){
   std::string filename = std::string(cutname);
   filename.insert(0,"CUT/");
   filename.append(".txt");
   std::ofstream myfile;
   myfile.open(filename.c_str());
   myfile<<cutname<< std::endl;
   int NumOfPoints = cutg->GetN();
   myfile<<NumOfPoints<< std::endl;
   double *x = cutg->GetX();
   double *y = cutg->GetY();
   for(int i=0; i<NumOfPoints; i++){
      myfile<<x[i]<<" "<<y[i]<< std::endl;
   }
   myfile.close();
}
