#include <cmath>
#include <algorithm>
#include <vector>
#include <iostream>

/// @brief Calculate the ft for the indicated transition
/// @param zed Proton number of the mother nucleus
/// @param qbeta Energy available for the beta decay (keV)
/// @param dqbeta Uncertainty in the energy available for the beta decay
/// @param hl Halflife of the mother state (ms)
/// @param dhl Uncertainty in the halflife of the mother state
/// @param br Branching ratio of the daughter state (fractional)
/// @param dbr Uncertainty in th branching ratio of the daughter state
/// @param ft Returned logft value
/// @param dftl Lefthand side of the uncertainty in the logft
/// @param dfth Righthand side of the uncertainty in the logft
std::vector<double> CalcFt(int zed, double qbeta, double dqbeta, double hl, double dhl, double br, double dbr){

    auto FermiIntegral = [](int Zed, double Emax){//integration of Fermi function, energy in keV
        double logf=0;
        double evalCoeff[4]={0};
        double coeff [16] ={-17.2,7.9015,-2.54,0.28482,3.31368,-2.06273,0.703822,-0.075039,-0.364018,0.387961,-0.142528,0.016,0.0278071,-0.026519,0.0098854,-0.00113772};
        evalCoeff[0]=coeff[0]+coeff[1]*log(Zed)+coeff[2]*pow(log(Zed),2)+coeff[3]*pow(log(Zed),3);
        evalCoeff[1]=coeff[4]+coeff[5]*log(Zed)+coeff[6]*pow(log(Zed),2)+coeff[7]*pow(log(Zed),3);
        evalCoeff[2]=coeff[8]+coeff[9]*log(Zed)+coeff[10]*pow(log(Zed),2)+coeff[11]*pow(log(Zed),3);
        evalCoeff[3]=coeff[12]+coeff[13]*log(Zed)+coeff[14]*pow(log(Zed),2)+coeff[15]*pow(log(Zed),3);
        logf = evalCoeff[0]+evalCoeff[1]*log(Emax)+evalCoeff[2]*pow(log(Emax),2)+evalCoeff[3]*pow(log(Emax),3);
        return logf;
    };
    try{
        double f=pow(10, FermiIntegral(zed,qbeta));
        double fp=pow(10, FermiIntegral(zed,qbeta+dqbeta));
        double fm=pow(10, FermiIntegral(zed,qbeta-dqbeta));
        if(dqbeta==0){
        fp=f;
        fm=f;
        }
        double dfh=fp-f;
        double dfl=f-fm;
        //double df=sqrt(abs(f-fp)*abs(f-fm));
        double ft=f*hl/1000./br;
        //if(dbr>0.9*br){
        //   dbr=0.9*br;
        //}
        double dfth1 = dfh*hl/1000./br;
        double dfth2 = f*dhl/1000./br;
        double brmin = br-dbr;
        if(brmin<=0){
        brmin=1e-5;
        }
        double dfth3 = f*hl/1000.*(1/brmin-1/br);
        double dfth=sqrt(pow(dfth1,2)+pow(dfth2,2)+pow(dfth3,2));
        double dftl1 = dfl*hl/1000./br;
        double dftl2 = f*dhl/1000./br;
        double brmax = std::min(1., br+dbr);
        double dftl3 = f*hl/1000.*(1/br-1/brmax);
        double dftl=sqrt(pow(dftl1,2)+pow(dftl2,2)+pow(dftl3,2));
        if(dftl>=ft){
        dftl=ft;
        }
        return {ft, dftl, dfth};
    }
    catch (const std::exception& ex) {
        std::cout << ex.what() << std::endl;
    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    } catch (...) {
        std::cout << "Threw an unhandled exception!" << std::endl;
    }
    return {0,0,0};
}
