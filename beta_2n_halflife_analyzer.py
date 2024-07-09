import re
import ROOT
import os
import pathlib
from .binning import Binning
from .handyutils import *
from typing import List, Tuple, Union
from . import literature_values
from .root_hist_decorator import RootHistDecorator

class Beta_2N_Analyzer:
    def __init__(
        self,
        name: str,
        fitname: str,
        halflife_names: Tuple[str, str, str, str],
        # (value, fixed?)
        halflife_info: Tuple[
            Tuple[float, bool], 
            Tuple[float, bool], 
            Tuple[float, bool], 
            Tuple[float, bool], 
        ],
        fit_low: float = -1e8,
        fit_high: float = 1e8,
        A0_start: float = 10,
        background: float = 10,
        P_n_guess: float = 0.8,
        P_2n_guess: float = 0.1,
        time_units: float = 1e-9,
        P_n_as_parameter: bool = False,
        mother_activity_override: str = None,
        beta_daughter_activity_override: str = None,
        n_daughter_activity_override: str = None,
        n2_daughter_activity_override: str = None,
        include_background_fit:bool = True,
        fix_background: bool = False,
        background_err: float = 0,
    ) -> None:
        # param 0 A0
        # param 1 background
        # param 2 P_n
        # param 3 P_2n
        # param 4 decay constant 1
        # param 5 decay constant 2
        # param 6 decay constant 3
        # param 7 decay constant 4
        if type(P_n_guess) is not float or P_n_guess < 0:
            P_n_guess = 0.8
        
        if type(P_2n_guess) is not float or P_2n_guess < 0:
            P_2n_guess = 0.1
        
        self.initial_parameters= [
            A0_start, background, P_n_guess, P_2n_guess, halflife_info[0][0],
            halflife_info[1][0], halflife_info[2][0], halflife_info[3][0]
        ]
        self.name = name
        self.fitname = fitname
        self.fit_low = fit_low
        self.fit_high = fit_high
        self.time_units = time_units
        self.most_recent_fit_result = "Never Fit"

        # original Beta 2N implementation
        # [0] => A_0
        # [1] => lambda_beta^38Mg
        # [2] => lambda_beta^38Al
        # [3] => lambda_beta^37Al
        # [4] => Background
        # [5] => P_n
        # [6] => lambda_beta^36Al
        # [7] => P_2n
        #Mg38Activity =      "[0] * [1] * exp(-1 * [1] * x * {})".format(time_units)
        #Mg38_Al38Activity = "[0]*(1 - [5] - [7]) * (([1]*[2])/([2]-[1]))* (exp(-1 * [1]*x*{}) - exp(-1 * [2]*x*{}))".format(time_units, time_units)
        #Mg38_Al37Activity = "[0]*[5]* (([1]*[3])/([3]-[1])) *             (exp(-1 * [1]*x*{}) - exp(-1 * [3]*x*{}))".format(time_units, time_units)
        #Mg38_Al36Activity = "[0]*[7]* (([1]*[6])/([6]-[1])) *             (exp(-1 * [1]*x*{}) - exp(-1 * [6]*x*{}))".format(time_units, time_units)
        #Mg38Activitystr = "(x > 0) * (" + Mg38Activity + "+" + Mg38_Al38Activity + "+" + Mg38_Al37Activity + "+" +  Mg38_Al36Activity + ")+ [4]"
        
        #Mapping
        # [0] => [0]
        # [1] => [4]
        # [2] => [5]
        # [3] => [6]
        # [4] => [1]
        # [5] => [2]
        # [6] => [7]
        # [7] => [3]

        # general 2N implementation
        # [0] => A0
        # [1] => Background
        # [2] => P_n
        # [3] => P_2n
        # [4] => Lambda_Mother
        # [5] => Lambda_Daughter
        # [6] => Lambda_N_daughter
        # [7] => Lambda_2N_daughter
        chainmotherdefault = "[0] * [4] * exp(-1 * [4] * x * {0})".format(time_units)
        daughterdefault    = "[0] * (1 - [2] - [3]) * (([4]*[5])/([5]-[4])) * (exp(-1 * [4]*x*{0}) - exp(-1 * [5]*x*{0}))".format(time_units)
        ndaughterdefault   = "[0] * [2] *             (([4]*[6])/([6]-[4])) * (exp(-1 * [4]*x*{0}) - exp(-1 * [6]*x*{0}))".format(time_units)
        n2daughterdefault  = "[0] * [3] *             (([4]*[7])/([7]-[4])) * (exp(-1 * [4]*x*{0}) - exp(-1 * [7]*x*{0}))".format(time_units)


        self.ChainMotherActivity = chainmotherdefault if mother_activity_override        is None else mother_activity_override
        self.DaughterActivity    = daughterdefault    if beta_daughter_activity_override is None else beta_daughter_activity_override
        self.NdaughterActivity   = ndaughterdefault   if n_daughter_activity_override    is None else n_daughter_activity_override
        self.N2daughterActivity  = n2daughterdefault  if n2_daughter_activity_override   is None else n2_daughter_activity_override
        total_activity_str = "(x > 0.0) * (" + self.ChainMotherActivity + "+" +  self.DaughterActivity + "+" + self.NdaughterActivity + "+" + self.N2daughterActivity + ")" + ("+ [1]" if include_background_fit else "")
        self.func_obj = ROOT.TF1(fitname, total_activity_str, fit_low, fit_high)
        self.func_obj.SetParName(0, "A0")
        
        self.func_obj.SetParName(1, "Background")
        if fix_background:
            self.func_obj.FixParameter(1, background)
        else:
            self.func_obj.SetParameter(1, background)
        self.func_obj.SetParError(1, background_err)

        self.func_obj.SetParName(2, "P_n")
        self.func_obj.SetParName(3, "P_2n")
        self.func_obj.SetParLimits(0, 0, 10000)
        for i in range(4, 8):
            if isinstance(halflife_info[i-4][0], tuple):
                if halflife_info[i-4][1]:
                    self.func_obj.FixParameter(i, halflife_info[i-4][0][0])
                    self.func_obj.SetParError(i,  halflife_info[i-4][0][1])
                else:
                    self.func_obj.SetParameter(i, halflife_info[i-4][0][0])
                    self.func_obj.SetParError(i,  halflife_info[i-4][0][1])
                    self.func_obj.SetParLimits(i, 0, 2000)
            else:
                if halflife_info[i-4][1]:
                    self.func_obj.FixParameter(i, halflife_info[i-4][0])
                else:
                    self.func_obj.SetParameter(i, halflife_info[i-4][0])
                    self.func_obj.SetParLimits(i, 0, 2000)
            
            self.func_obj.SetParName(i, halflife_names[i-4])
        if P_n_as_parameter:
            self.func_obj.SetParameter(2, P_n_guess)
            self.func_obj.SetParameter(3, P_2n_guess)
            self.func_obj.SetParLimits(2, 0, 1)
            self.func_obj.SetParLimits(3, 0, 1)
        else:
            self.func_obj.FixParameter(2, P_n_guess)
            self.func_obj.FixParameter(3, P_2n_guess)

    def SetMotherHalflife(self, val: float, lim_up: float = None, lim_down: float = None) -> None:
        if lim_up is not None and lim_down is not None:
            self.func_obj.SetParLimits(4, lim_down, lim_down)
        self.func_obj.SetParameter(4, val)

    def SetA0(self, val: float) -> None:
        if val <= 0.0:
            return
        self.func_obj.SetParameter(0, val)
        self.initial_parameters[0] = val

    def BuildSubActivities(self, 
                           includeBackground: bool = True, 
                           debugcallback = lambda a : (), 
                           include_cov:bool = True, 
                           separate_background_func: bool = True):
        if self.most_recent_fit_result == "Never Fit":
            return
        if not isinstance(includeBackground, bool):
            includeBackground = True
        backgroundterm = " + [1]" if includeBackground else ""
        chainmother = ROOT.TF1(self.name+"chainmother", "(x >= 0) * " + self.ChainMotherActivity + backgroundterm, self.fit_low, self.fit_high)
        daughter1   = ROOT.TF1(self.name+"daughter1",   "(x >= 0) * " + self.DaughterActivity    + backgroundterm, self.fit_low, self.fit_high)
        Ndaughter   = ROOT.TF1(self.name+"Ndaughter",   "(x >= 0) * " + self.NdaughterActivity   + backgroundterm, self.fit_low, self.fit_high)
        N2daughter  = ROOT.TF1(self.name+"2Ndaughter",  "(x >= 0) * " + self.N2daughterActivity  + backgroundterm, self.fit_low, self.fit_high)
        ret = [chainmother, daughter1, Ndaughter, N2daughter]
        if separate_background_func:
            Background  = ROOT.TF1(self.name+"Background",  "[1]", self.fit_low, self.fit_high)
            Background.SetParName(1, "Constant Background")
            Background.SetParameter(1, self.func_obj.GetParameter(1))
            Background.SetParError(1, self.func_obj.GetParError(1))
            ret.append(Background)
        
        debugcallback("Getting fit covariance")
        bigcovmat: ROOT.TMatrixD = self.most_recent_fit_result.GetCovarianceMatrix()
        
        for k in range(4):
            func = ret[k]
            # build list of parameters that each sub function has
            # this supresses errors
            debugcallback(f"Getting parameter indices for {func.GetName()}")
            debugcallback(f"with title {func.GetTitle()}")
            matches = re.findall(r"\[(\d+)\]",func.GetTitle())
            idxs = [int(j) for j in matches]
            debugcallback("Deciding subactivity covariance rank")
            covmat_rank = max(idxs if len(idxs) > 0 else [0]) + 1
            debugcallback(f"Covariance rank {covmat_rank}")
            debugcallback(f"Npar {func.GetNpar()}")
            debugcallback("Init sub covariance")
            if include_cov:
                covmat = ROOT.TMatrixD(covmat_rank, covmat_rank)
                dbgstr = ""
                for x in idxs:
                    for y in idxs:
                        covmat[x][y] = bigcovmat[x][y]
                for x in range(covmat_rank):
                    for y in range(covmat_rank):
                        dbgstr += f"{covmat[x][y]:.3f}, "
                    dbgstr += "\n"
                debugcallback(f"matrix array\n[\n{dbgstr}]")
                ret.append(covmat)
            debugcallback("Assigning subactivity parameters")
            for j in idxs:
                # background
                if j == 1 and separate_background_func:
                    func.SetParameter(j, 0)    
                else:
                    func.SetParameter(j, self.func_obj.GetParameter(j))
                func.SetParError(j, self.func_obj.GetParError(j))
                func.SetParName(j, self.func_obj.GetParName(j))
            debugcallback(f"Integral {func.Integral(self.fit_low, self.fit_high)}")

        return ret


    def CalculateResiduals(
            self, 
            other_hist: ROOT.TH1I,
            low=-1e8,
            high=1e8,
            numbins=200,
        ) -> None:
        t_hist = ROOT.TH1I("residual_temp_hist", "histtitle", numbins, low, high)
        for i in range(numbins):
            center = t_hist.GetBinCenter(i)
            y_val = self.func_obj.Eval(center)
            t_hist.SetBinContent(i, y_val)
        other_hist.Add(t_hist, -1)
        del(t_hist)
        

    def PlotComponents(
        self,
        hist: ROOT.TH1 = None, 
        include_total: bool = True
    ) -> None:
        subact = self.BuildSubActivities()
        if hist is not None:
            hist.Draw()
        col = 2
        if include_total:
            self.func_obj.Draw("SAME")
            col += 1
        for i in subact:
            #print(i.GetName(), i.GetTitle())
            i.SetLineColor(col)
            col += 1
            i.Draw("SAME")



    def Fit(
        self, 
        hist: ROOT.TH1, 
        opt: str = "SQLM", 
        fit_low_override: float = None, 
        fit_high_override: float = None
    ) -> None:
        if fit_low_override is None:
            fit_low_override = self.fit_low
        else:
            self.fit_low = fit_low_override
        if fit_high_override is None:
            fit_high_override = self.fit_high
        else:
            self.fit_high = fit_high_override
        if isinstance(hist, ROOT.TH1):
            result = hist.Fit(self.fitname, opt, "", fit_low_override, fit_high_override)
            self.most_recent_fit_result = result
            return result
        elif isinstance(hist, RootHistDecorator):
            result = hist.hist.Fit(self.fitname, opt, "", fit_low_override, fit_high_override)
            self.most_recent_fit_result = result
            return result

    def SetBackground(self, val: float, fixed_bg: bool = True) -> None:
        if val < 0:
            return
        if fixed_bg:
            self.func_obj.FixParameter(1, val)
        else:
            self.func_obj.SetParameter(1, val)
        self.initial_parameters[1] = val

    def Reset(self) -> None:
        for i in range(8):
            if self.func_obj.GetParError(i) == 0:
                self.func_obj.FixParameter(i, self.initial_parameters[i])
            else:
                self.func_obj.SetParameter(i, self.initial_parameters[i])

    def save_fit_parameters(
        self,
        isotope: str,
        num_fit_bins: int,
        path: str, 
        correlation_radius: float,
        overwrite: bool = False
    ) -> None:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        summary_str = "{}, correlation radius: {}\n".format(isotope, correlation_radius)
        summary_str += "\tfit_low (s): {}, fit_high (s): {}\n".format(self.fit_low * self.time_units, self.fit_high * self.time_units)
        chi_sq = param_err = self.func_obj.GetChisquare()
        summary_str += "\tChisquare: {:.3E}\n".format(chi_sq)
        nchan = 0
        for i in range(8):
            if self.func_obj.GetParError(i) > 1e-15:
                nchan += 1
        dof = num_fit_bins - nchan 
        summary_str += "\tFree Parameters: {}\n".format(nchan)
        summary_str += "\tBins in Fit: {}\n".format(num_fit_bins)
        summary_str += "\tDOF: {}\n".format(dof)
        summary_str += "\tChisquare / DOF: {: E}\n".format(chi_sq/dof if dof > 0 else -1)
        for i in range(8):
            param = self.func_obj.GetParName(i)
            param_val = self.func_obj.GetParameter(i)
            param_err = self.func_obj.GetParError(i)
            summary_str += "\t{}: \n\t\tvalue: {: E}, error: {}".format(param, param_val, "{: E}".format(param_err) if param_err > 0 else "fixed value")
            if "lambda" in param.lower():
                # since a fixed halflife has "zero" error, we have to do this to prevent div by zero issues
                halflife=decay_constant_to_halflife(param_val, input_units=1.0)
                percent_relative_err = "{:.3f}%".format((param_err / param_val) * 100.0) if param_err > 0 else "fixed value"
                relative_error = "fixed value" if param_err == 0 or param_val == 0 else "{: E}".format((param_err / param_val) * halflife)
                summary_str += "\n\t\tT1/2 (s): {: E}, Percent Relative Error: {}, Relative Error: {}".format(
                    halflife, 
                    percent_relative_err,
                    relative_error
                )

            summary_str += "\n"
        summary_str+="Most Recent Fit Result:\n"
        summary_str+= "{}".format(self.most_recent_fit_result)
        # save a copy of the old fit parameters
        if os.path.exists(path + "/r{:.3f}parameters.txt".format(correlation_radius)) and not overwrite:
            contents = ""
            with open(path + "/r{:.3f}parameters.txt".format(correlation_radius), "r") as rp:
                contents = rp.readlines()
            cpy = 0
            while os.path.exists(path + "/r{:.3f}parameters_old_{}.txt".format(correlation_radius, cpy)):
                cpy += 1
            with open(path + "/r{:.3f}parameters_old_{}.txt".format(correlation_radius, cpy), "w+") as fp: 
                fp.writelines(contents)
        with open(path + "/r{:.3f}parameters.txt".format(correlation_radius), "w+") as fp:
            fp.write(summary_str)


    @staticmethod
    def build_from_literature( 
        isotope, 
        name,
        fit_low: float,
        fit_high: float,
        Pn_override: float = None, 
        P2n_override: float = None,
        Lambda_override: float = None,
        A0_start_override: Tuple[float, float, float, float] = None,
        time_units: float = 1e-9):
        lit_vals = literature_values.LiteratureValues()
        pn  = Pn_override if Pn_override is not None else lit_vals.moller.GetPNn(isotope, 1)
        p2n = P2n_override if P2n_override is not None else lit_vals.moller.GetPNn(isotope, 2)
        
        m_lambda = Lambda_override if Lambda_override is not None else lit_vals.nudat.GetDecayConstant(isotope)
        A0_start = A0_start_override if A0_start_override is not None else 0.5
    
        zn         = lit_vals.IsotopeStrToZNTuple(isotope)
        daughter   = lit_vals.ZNTupleToIsotopeStr((zn[0] + 1, zn[1] - 1))
        ndaughter  = lit_vals.ZNTupleToIsotopeStr((zn[0] + 1, zn[1] - 2))
        n2daughter = lit_vals.ZNTupleToIsotopeStr((zn[0] + 1, zn[1] - 3))
        ret = Beta_2N_Analyzer(
            isotope,
            fitname=name,
            halflife_names=(
                "lambda_beta^{}".format(isotope), 
                "lambda_beta^{}".format(daughter), 
                "lambda_beta^{}".format(ndaughter), 
                "lambda_beta^{}".format(n2daughter)
            ),
            halflife_info=(
                (m_lambda, False),# we're letting this float to determine if it's accurate
                (lit_vals.nudat.GetDecayConstant(daughter), True),
                (lit_vals.nudat.GetDecayConstant(ndaughter), True),
                (lit_vals.nudat.GetDecayConstant(n2daughter), True)
            ), 
            P_n_guess=pn,
            P_2n_guess=p2n,
            fit_low=fit_low,
            fit_high=fit_high,
            A0_start=A0_start,
            time_units=time_units
        )
        return ret