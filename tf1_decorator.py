from enum import Enum, IntEnum
import ROOT
import math
from . import handyutils
class TF1TypeEnum(IntEnum):
    CONST         = 0
    LINEAR        = 1
    EXP           = 2
    CONSTEXP      = 3
    LINCONSTEXP   = 4
    GAUSS         = 5
    CONSTGAUSS    = 6
    LINCONSTGAUSS = 7



class RootTF1Decorator:
    def __init__(self, name: str, functype: TF1TypeEnum, x_units: str):
        if not isinstance(functype, TF1TypeEnum):
            raise ValueError(f"functype must be {TF1TypeEnum}, got {type(TF1TypeEnum)}")
        self.functype = functype
        self.name     = name
        self.funcobj  = ROOT.TF1(name, self.get_function_str(), "SQLM", "")
        self.x_units  = x_units
        


    def get_label(self, parameter_num: int, include_name: bool = False) -> ROOT.TText:
        if not isinstance(parameter_num, int):
            raise TypeError("Parameter number must be an integer")
        if parameter_num < 0 or parameter_num > self.funcobj.GetParNumber() - 1:
            raise ValueError(f"Parameter number must be in the range 0 to {self.funcobj.GetParNumber() - 1}")
        val = self.funcobj.GetParameter(parameter_num)
        err = self.funcobj.GetParError(parameter_num)
        unc = f"{self.funcobj.GetParName(parameter_num) + ':' if include_name else ''}" +handyutils.get_standard_uncertainty_str(val, err) + f" {self.x_units}"
        ret = ROOT.TText(val, self.funcobj.Eval(x=val, y=0, z=0, t=0), unc)
        return ret
        

    def get_function_str(self) -> str:
        funcs = [
            "[0]", 
            "[0] + ([1] * x)", 
            "[0] * exp(x * [1])", 
            "[0] + [1] * exp(x * [2])",
            "[0] + ([1] * x) + [2] * exp(x * [3])", 
            "gaus(0)", 
            "[0] + gaus(1)", 
            "[0] + ([1] * x) + gaus(2)"
        ]
        return funcs[int(self.functype)]

