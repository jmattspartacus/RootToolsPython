#include "TH1D.h"
#include "TFile.h"

#include <string>


TH1D *TFileGetTH1D(const std::string &histtitle, TFile &f){
    if(histtitle.size() == 0){return nullptr;}
    TH1D *h = nullptr;
    f.GetObject(histtitle.c_str(), h);
    return h;
}