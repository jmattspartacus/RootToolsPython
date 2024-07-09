#include "TH3D.h"
#include "TFile.h"

#include <string>

TH3D *TFileGetTH3D(const std::string &histtitle, TFile &f){
    if(histtitle.size() == 0){return nullptr;}
    TH3D *h = nullptr;
    f.GetObject(histtitle.c_str(), h);
    return h;
}