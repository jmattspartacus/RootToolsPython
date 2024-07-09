#include <TMath.h>

const int NumOfBars=48;
double VANDLEZ0[NumOfBars]={0};
double VANDLETheta[NumOfBars]={0};
double VANDLERadians[NumOfBars]={0};
double VANDLEXOffset[NumOfBars]={0};
const double speedOfLight=29.9792458;

void ReadVandleSetup(const char* filename){//read the vandle Z0 and XOffset from timeCal
   std::ifstream f(filename);
   std::string line;
   while (std::getline(f, line)) {
      if(line.find("#")!=string::npos){
         continue;
      }
      std::istringstream ss1(line);
      int barNum;
      double vandleZ0;
      double vandleX0;
      ss1 >> barNum >> vandleZ0 >> vandleX0;
      //cout<<"bar: "<<barNum<<", Z0 = "<<vandleZ0<<", X0 = "<<vandleX0<< std::endl;
      VANDLEZ0[barNum]=vandleZ0;
      VANDLEXOffset[barNum]=vandleX0;
   }
   f.close();
   for(int i=0; i<NumOfBars; i++){
      VANDLETheta[i]=-88.22+3.75*(NumOfBars-1-i);
      VANDLERadians[i]=VANDLETheta[i]*TMath::Pi()/180.;
   }
}
