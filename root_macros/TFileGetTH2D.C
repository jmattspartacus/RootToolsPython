#include "TH2D.h"
#include "TFile.h"

#include <string>


TH2D *TFileGetTH2D(const std::string &histtitle, TFile &f){
    if(histtitle.size() == 0){return nullptr;}
    TH2D *h = nullptr;
    f.GetObject(histtitle.c_str(), h);
    return h;
}