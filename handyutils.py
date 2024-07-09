import math
import ROOT
from typing import Tuple
import time

def sethistlabels(
    histtitle: str, 
    xlabel: str, 
    ylabel: str, 
    hist: ROOT.TH1) -> None:
    hist.SetTitle(histtitle+ ";" + xlabel + ";" + ylabel)
    
def setlogx(can: ROOT.TCanvas, yes: int = 1) -> None:
    can.GetPad(0).SetLogx(yes)
    
def setlogy(can: ROOT.TCanvas, yes: int = 1) -> None:
    can.GetPad(0).SetLogy(yes)

def setlogz(can: ROOT.TCanvas, yes: int = 1) -> None:
    can.GetPad(0).SetLogz(yes)



def halflife_to_decay_constant(
    halflife: float, 
    input_units = 1e-3, # input units in seconds
    output_units: float = 1.0 # divisions of time the final constant should be in
) -> float:
    ln2 = math.log(2.0)
    if halflife == 0 or input_units == 0:
        return 0
    return output_units * ln2 / (halflife * input_units)

def decay_constant_to_halflife(
    decayconstant: float, 
    input_units: float  = 1e-3,
    output_units: float = 1.0
) -> float:
    if decayconstant == 0 or input_units == 0:
        return 0
    ln2 = math.log(2.0)
    return (ln2 * output_units) / (decayconstant * input_units)

def get_exponent(num: float) -> float:
    ct = 0
    if(num == float('inf')):
        return float('inf')
    if(num == 0):
        return -float("inf")
    if(num < 0):
        num *= -1
    if num >= 10:
        while(num >= 10):
            num /= 10
            ct += 1
    elif num < 1:
        while(num < 1):
            num *= 10
            ct -= 1
    return ct

def get_standard_uncertainty(num: float, uncertainty: float, eps = 1e-24) -> Tuple[float, float, float]:
    exponent = get_exponent(uncertainty)
    divexp = math.pow(10, exponent)
    divexp = divexp if divexp != 0 else 1
    if exponent < 0:
        num -= ((num + eps) % divexp) + eps
    else:
        num -= num % 1
    if exponent < 0:
        uncertainty -= ((uncertainty + eps) % divexp) + eps
        uncertainty *= math.pow(10, -exponent)
    else:
        uncertainty -= ((uncertainty + eps) % 1) + eps

    return (num, uncertainty, exponent if exponent > 0 else - exponent)

def get_standard_uncertainty_str(num, uncertainty, eps=1e-24):
    unc = list(get_standard_uncertainty(num, uncertainty, eps))
    for i in range(len(unc)):
        if math.isinf(unc[i]):
            unc[i] = 1
    return "{0:.{1}f} ({2:.0f})".format(unc[0], unc[2], unc[1])




import io
from contextlib import redirect_stdout

def capture_stdout_for_func(func, args=None) -> str:
    with io.StringIO() as buf, redirect_stdout(buf):
        if args is not None:
            func(*args)
        else:
            func()
        output = buf.getvalue()
    return output



def check_root_fit_success(fitresultstr) -> bool:
    return "CONVERGED" in fitresultstr


def table_to_tex(table, columnar = True):
    ret = []
    if columnar:
        for i in range(len(table[0])):
            ret.append("")

        for i in range(len(table[0])):
            for j in range(len(table)):
                if j < len(table) - 1:
                    ret[i] += f"{table[j][i]} &"
                else:
                    ret[i] += f"{table[j][i]}\\\\"
    else:
        maxlen = 0
        for i in table:
            maxlen = maxlen if len(i) < maxlen else len(i)
        for i in table:
            tline = ""
            for j in range(maxlen):
                if j < len(i) and j < maxlen - 1:
                    tline += f"{i[j]}&"
                elif j < len(i):
                    tline += f"{i[j]}\\\\"
                elif j < maxlen - 1:
                    tline += "&"
                else:
                    tline += "\\\\"
            ret.append(tline)
    return ret

def time_me(func, args=None, print_out=False):
    start = time.time()
    if args is None:
        func()
    else:
        func(*args)
    end = time.time()
    time_seconds = end - start
    time_minutes = time_seconds // 60
    time_seconds -= time_minutes * 60
    time_hours = time_minutes // 60
    time_minutes -= time_hours * 60
    time_days = time_hours // 24
    time_hours -= time_days * 24
    if print_out:
        print(f"Total run time: {int(time_days)}:{int(time_hours):02d}:{int(time_minutes):02d}:{int(time_seconds):.03f}")
    return (time_days, time_hours, time_minutes, time_seconds)