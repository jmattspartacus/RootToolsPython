import ROOT
import os
from typing import Dict, Union

macro_fpath = "/".join(__file__.split("/")[:-1])+"/"
macro_files = [
    "root_macros/ReadPIDCut.C",
    "root_macros/MakePIDCut.C",
    "root_macros/PyEnableImplicitMT.C",
    "root_macros/CalcFt.C",
    "root_macros/TFileGetTH1D.C",
    "root_macros/TFileGetTH2D.C",
    "root_macros/TFileGetTH3D.C",
]
macro_files = [macro_fpath + i for i in macro_files]

def load_cpp_file(file: str) -> None:
    if not os.path.exists(file):
        print(f"Failed to find {file}")
        return
    try:
        cpp_code = ""
        with open(i, "r") as fp:
            cpp_code = "".join(fp.readlines())
        ROOT.gInterpreter.ProcessLine(cpp_code)
    except Exception as e:
        if __name__ == "__main__":
            raise e    
        print("Failed to load cpp file!")
        print(e)

for i in macro_files:
    load_cpp_file(i)

def ReadPIDCut(filepath: str) -> ROOT.TCutG or None:
    try:
        abspath = os.path.abspath(filepath)
    except Exception as e:
        print("Failed to expand path into absolute path!")
        print(e)
        return None
        
    ret = None
    try:
        ret = ROOT.ReadPIDCut(filepath)
    except Exception as e:
        print("ROOT threw an exception!")
        print(e)

    # ReadPIDCut returns a nullptr for a failed load
    if ret:
        return ret
    return None

def MakePIDCut(filepath: str, cut: ROOT.TCutG) -> None:
    if not isinstance(cut, ROOT.TCutG):
        raise TypeError("cut MUST be a ROOT.TCutG")
    if not isinstance(filepath, str):
        raise TypeError("filepath MUST be a string")
    try:
        abspath = os.path.abspath("/".join(filepath.split("/")[:-1])) +"/" + filepath.split("/")[-1]
    except Exception as e:
        print("Failed to expand path into absolute path!")
        print(e)
        return
    try:
        ROOT.MakePIDCut(cut, abspath)
    except Exception as e:
        print("ROOT threw an exception!")
        print(e)

def PyEnableImplicitMT(num_workers: int) -> None:
    if not isinstance(num_workers, int):
        raise TypeError("EnableImplicitMT expects an integer!")
    try:
        ROOT.PyEnableImplicitMT(num_workers)
    except Exception as e:
        if __name__ == "__main__":
            raise(e)
        print("ROOT threw an exception while trying to set number of threads!")
        print(e)



def CalcFt(Z: int, 
           q_beta: float,
           d_q_beta: float,
           mother_halflife: float,
           d_mother_halflife: float,
           branching_ratio: float,
           d_branching_ratio: float) -> Dict[str, float]:
    """Calculates the ft value for a transition, all types are strict

    Args:
        Z (int): Proton number of the mother nucleus
        q_beta (float): Energy available for the beta decay (keV)
        d_q_beta (float): Uncertainty in q_beta (keV)
        mother_halflife (float): Halflife of the mother state (ms)
        d_mother_halflife (float): Uncertainty of the halflife of the mother state (ms)
        branching_ratio (float): Branching ratio of the daughter state (fractional)
        d_branching_ratio (float): Uncertainty in the branching ratio of the daughter state (fractional)

    Raises:
        TypeError: If Z is not an int
        TypeError: If any of the other arguments are not floats

    Returns:
        Dict[str, float]: A dict of the ft value as well as upper and lower uncertainties
    """
    if not isinstance(Z, int):
        raise TypeError("Z must be an integer!")
    args = [q_beta, d_q_beta, mother_halflife, d_mother_halflife, branching_ratio, d_branching_ratio]
    arg_strs = ["q_beta", "d_q_beta", "mother_halflife", "d_mother_halflife", "branching_ratio", "d_branching_ratio"]
    for i in range(len(args)):
        t_arg = args[i]
        if not isinstance(t_arg, float):
            raise TypeError(f"{arg_strs[i]} must be a float! Got a {type(t_arg)}")
    try:
        ret = ROOT.CalcFt(Z, q_beta, d_q_beta, mother_halflife, d_mother_halflife, branching_ratio, d_branching_ratio)
        return {
            "ft" :     float(ret[0]),
            "d_ft_l" : float(ret[1]),
            "d_ft_r" : float(ret[2])
        }
    except Exception as e:
        print("CalcFt threw an exception in C++!")
        raise(e)
        

def TFileGetHist(file: ROOT.TFile, histtitle: str, dims: int) -> Union[ROOT.TH1D, ROOT.TH2D, ROOT.TH3D]:
    if not isinstance(file, ROOT.TFile):
        raise TypeError("File must be a TFile!")
    if not isinstance(histtitle, str):
        raise TypeError("histtitle must be a string!")
    if not isinstance(dims, int):
        raise TypeError("dims must be an integer in the range (1-3)")
    if dims < 0  or dims > 3:
        raise ValueError("dims must be an integer in the range (1-3)")
    try:
        if dims == 1:
            ret = ROOT.TFileGetTH1D(histtitle, file)
            return ret
        elif dims == 2:
            ret = ROOT.TFileGetTH2D(histtitle, file)
            return ret
        elif dims == 3:
            ret = ROOT.TFileGetTH3D(histtitle, file)
            return ret
        return None
    except Exception as e:
        print(e)
        raise(e)