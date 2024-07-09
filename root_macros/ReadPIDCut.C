#include <TCutG.h>

TCutG *ReadPIDCut(const char* filename){
   string line;
   fstream f(filename);
   if(f.is_open()){
      getline(f, line);
      string cutname(line);
      getline(f, line);
      std::stringstream ss (line);
      int NumOfPoints;
      ss >> NumOfPoints;
      TCutG *cutg = new TCutG(cutname.c_str(), NumOfPoints);
      cutg->SetVarX("ToF");
      cutg->SetVarY("dE");
      cutg->SetTitle("Graph");
      cutg->SetFillStyle(1000);
      for(int i=0; i<NumOfPoints; i++){
         getline(f, line);
         std::stringstream ss2 (line);
         double x, y;
         ss2 >> x >> y;
         cutg->SetPoint(i, x, y);
      }
      f.close();
      return cutg;
   }
   return nullptr;
}
