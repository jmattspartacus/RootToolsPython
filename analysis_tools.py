import ROOT
import os
import sys
import random
import time
try:
    random.seed(time.clock())
except:
    random.seed(random.random())
import string
import itertools
import math
import numbers
try:
    from matplotlib import pyplot
    matplotlibexists = True
except:
    matplotlibexists = False
from glob import glob
import datetime
from .handyutils import *
from typing import List, Union, Callable

# want silent fail
try:
    from tqdm import tqdm
    tqdmexists = True
except:
    tqdmexists = False

numpyexists = True
try:
    import numpy
    numpyexists = True
except:
    numpyexists = False

try:
    ROOT.EnableImplicitMT()
except:
    pass

from .root_tree_fields import *



def gauss_func_str(starting_param_number: int = 0):
    if not isinstance(starting_param_number, int):
        raise TypeError("starting parameter number must be an integer")
    if starting_param_number < 0 or starting_param_number > 1<<31 - 2:
        raise ValueError("Invalid starting parameter number chosen")
    return f"[{starting_param_number}] * exp(-(x-[{starting_param_number + 1}])*(x-[{starting_param_number + 1}])/2./[{starting_param_number + 2}]/[{starting_param_number + 2}])"

def get_clover_fields(addback = False):
    if addback:
        clover_time_field   = clover_addback_relative_time
        clover_energy_field = clover_addback_energy
    else:
        clover_time_field   = clover_relative_time
        clover_energy_field = clover_energy
    return clover_time_field, clover_energy_field 


def prep_canvas(name="graphbox", title="graphbox", width = 800, height=600):
    return ROOT.TCanvas(name, title, width, height)

def calculate_bins(binlow, binhigh, binwidth):
    return int((binhigh - binlow) / binwidth)

# first prep an empty canvas
#if not ROOT.gROOT.IsBatch():
#    can = ROOT.TCanvas("graphbox", "graphbox", 800, 600)

def do_as_batch(func, args):
    ROOT.gROOT.SetBatch(True)
    ret = func(*args)
    ROOT.gROOT.SetBatch(False)
    return ret

def makeandfillhist1(field, numbins, low, high, chain, histtitle="default global; default x; default y", histname = "default-h1", cut = "", opt = ""):
    hist = ROOT.TH1D(histname, histtitle, numbins, low, high)
    chain.Draw(field + ">>" + histname, cut, opt)
    return hist

def appendhist1(field, chain, histname = "default-h1", cut = "", opt = ""):
    chain.Draw(field + ">>+" + histname, cut, opt)
    
def sethistlabels(histtitle="", xlabel="", ylabel="", hist=None):
    hist.SetTitle(histtitle+ ";" + xlabel + ";" + ylabel)
    
def setlogx(canvas, yes = 1):
    canvas.GetPad(0).SetLogx(yes)
    
def setlogy(canvas, yes = 1):
    canvas.GetPad(0).SetLogy(yes)

def setlogz(canvas, yes = 1):
    canvas.GetPad(0).SetLogz(yes)

def remove_all_copies(remove_me, thing):
    while True:
        try:
            thing.remove(remove_me)
        except ValueError:
            break
        except TypeError:
            break

def mkdir_p(dest):
    try:
        os.makedirs(dest)
    except:
        return

if matplotlibexists:
    def py_hist_from_root(isotope, chain, binwidth, binlow, binhigh, cut, bgcut, bgsub=True):
        if binhigh < binlow:
            raise ValueError("The high bin cannot be less than the low bin!")
        if binwidth <= 0:
            raise ValueError("Binwidth must be positive!")

        num_bins = int((binhigh - binlow) / binwidth)

        syssearch_clover_Ehist1 = makeandfillhist1("clover_E", num_bins, binlow, binhigh,
                                    chain,
                                    histtitle=f"signal {cut}",
                                    histname = f"signal {isotope}",
                                    cut = cut,
                                    opt = "col")
        if bgsub:
            syssearch_clover_Ehist3 = makeandfillhist1("clover_E", num_bins, binlow, binhigh,
                                        chain,
                                        histtitle=f"background {bgcut};",
                                        histname = f"{isotope} background",
                                        cut = bgcut,
                                        opt = "col")
            syssearch_clover_Ehist1.Add(syssearch_clover_Ehist3, -1)

        t_xs=[]
        t_ys=[]
        maxmult = 0
        for kk in range(1, num_bins + 1):
            tbin = syssearch_clover_Ehist1.GetBinCenter(kk) - binwidth
            if tbin < 100:
                continue
            t_xs.append(tbin)
            mult = syssearch_clover_Ehist1.GetBinContent(kk)
            t_ys.extend([tbin]*int(mult))
            if mult > maxmult:
                maxmult = mult
        pyplot.hist(t_ys, t_xs, histtype='step', linewidth=0.4)

def extract_curve_from_root_hist(isotope, field, histtitle, chain, binwidth, binlow, binhigh, cut, bgcut, keep_negative = True, bgsub=True):
    if binhigh < binlow:
        raise ValueError("The high bin cannot be less than the low bin!")
    if binwidth <= 0:
        raise ValueError("Binwidth must be positive!")

    num_bins = int((binhigh - binlow) / binwidth)
    
    signal = makeandfillhist1(field, num_bins, binlow, binhigh,
                                chain,
                                histtitle=f"signal {cut}",
                                histname = f"signal {isotope}",
                                cut = cut,
                                opt = "col")
    if bgsub:
        background = makeandfillhist1(field, num_bins, binlow, binhigh,
                                    chain,
                                    histtitle=f"background {bgcut};",
                                    histname = f"{isotope} background",
                                    cut = bgcut,
                                    opt = "col")
        signal.Add(background, -1)
    
    t_xs=[]
    t_ys=[]
    for kk in range(1, num_bins + 1):
        tbin = signal.GetBinCenter(kk) - binwidth
        if tbin < 100:
            continue
        mult = signal.GetBinContent(kk)
        if mult < 0 and not keep_negative:
            continue
        t_xs.append(tbin)
        t_ys.append(int(mult))
    return (t_xs, t_ys)

def draw_general_hist(
    chain=None, plotisotope="32Na", x_label="Clover energy (keV)", y_label="Counts minus background",
    x_field="clover_E", bin_width=2.0, x_low=0.0, x_high=1000.0, histtitle="32Na",
    bg_sub=True, signal_cut = "1 == 1", background_cut = "1 == 1", showstats=False, opt="col", field_is_background=False, background_start= -1000):
    if type(chain) != ROOT.TChain:
        raise TypeError("chain must be a ROOT.TChain")
    # number of bins for the histogram
    e_bins = int(abs(x_high - x_low) / bin_width)
    
    # need to build this here instead of the format string
    t_bg = "with bg subtraction" if bg_sub else ""
    
    sig_hist = makeandfillhist1(x_field, e_bins, x_low, x_high,
                                        chain,
                                        histtitle=f"signal {plotisotope};",
                                        histname = f"{plotisotope} signal",
                                        cut = signal_cut,
                                        opt = opt)
    if bg_sub:
        # this is never visible, so we can ignore the title and stuff
        bglow = background_start if field_is_background else x_low
        bghigh = background_start + (x_high - x_low) if field_is_background else x_high
        bg_hist = makeandfillhist1(x_field, e_bins, bglow, bghigh,
                                        chain,
                                        histtitle=f"background {plotisotope};",
                                        histname = f"{plotisotope} background",
                                        cut = background_cut,
                                        opt = opt)
        sig_hist.Add(bg_hist, -1)
        
        sethistlabels(f"{histtitle} {t_bg}", x_label, y_label, sig_hist)
        if not showstats:
            sig_hist.SetStats(False)
            bg_hist.SetStats(False)
        return sig_hist, bg_hist
    else:
        sethistlabels(f"{histtitle} {t_bg}", x_label, y_label, sig_hist)
        if not showstats:
            sig_hist.SetStats(False)
        return sig_hist


def draw_clover_hist(
    chain=None, plotisotope="32Na",
    energy_bin_width=2.0, energy_low=0.0, energy_high=1000.0,
    time_low=10.0, time_high=2e5, time_units = "ns",
    bg_sub=True, bg_high=-1000,
    pidcut = "", additional_cut = "", simple = False):
    clover_corrected_time_field, clover_energy_field = get_clover_fields()
    bg_low = bg_high - abs(time_high - time_low)
    pidcutstr = pidcut + ' && ' if pidcut != "" else ""
    additional_cutstr = " && " + additional_cut if additional_cut != "" else ""
    x_label="Clover energy (keV)"
    y_label = f"Counts{' minus background' if bg_sub else ''}"
    t_bg = "with bg subtraction" if bg_sub else ""
    hist_title = f"{plotisotope} counts for {clover_corrected_time_field} > {time_low} ({time_units}) {t_bg}"
    signalcut = f"{pidcutstr}{clover_corrected_time_field}  > {time_low} && {clover_corrected_time_field} < {time_high} && {clover_energy_field} < {energy_high} && {clover_energy_field} > {energy_low}{additional_cutstr}"
    backgroundcut       = f"{pidcutstr}{clover_corrected_time_field} > {bg_low} && {clover_corrected_time_field} < {bg_high} && {clover_energy_field} < {energy_high} && {clover_energy_field} > {energy_low}{additional_cutstr}"
    return draw_general_hist(chain, plotisotope, 
        signal_cut=signalcut, background_cut=backgroundcut, histtitle=hist_title, 
        x_field=clover_energy_field, bin_width=energy_bin_width, x_low=energy_low, x_high=energy_high,
        x_label=x_label, y_label=y_label, bg_sub=bg_sub)
    

def overlay_py_hists(isotopes, histtitle, chain, binwidth, binlow, binhigh, pid_cut, bglow, bghigh, tlow, thigh, bgsub=True):
    if binhigh < binlow:
        raise ValueError("The high bin cannot be less than the low bin!")
    if binwidth <= 0:
        raise ValueError("Binwidth must be positive!")

    for i in isotopes:
        do_as_batch(py_hist_from_root, [i, histtitle, chain, binwidth, binlow, binhigh, pid_cut, bglow, bghigh, tlow, thigh, bgsub])
    pyplot.legend(isotopes)

# create a cut based on the predefined clover time and energy fields and the values chosen for the gate
def gamma_cut(time_low, time_high, energy_high, energy_low, addback=False):
    clover_time_field, clover_energy_field = get_clover_fields(addback)
    return f"{clover_time_field} > {time_low} && {clover_time_field} < {time_high} && {clover_energy_field} > {energy_low} && {clover_energy_field} < {energy_high}"





def draw_decay_curve(chain, time_low, time_high, bin_width, time_field, cut="", opt="", histtitle="default global; default x; default y", histname = "default-h1") -> int:
    # if we return the number of entries we can do nice stuff later
    res = makeandfillhist1(time_field, calculate_bins(time_low, time_high, bin_width), time_low, time_high, chain, histtitle=histtitle, histname=histname, cut = cut, opt=opt)
    return res



# do_this should be a function/lambda that takes the arguments in order provided by each combination of options
def do_all_combinations(do_this, show_counter=False, *args):
    for i in args:
       if type(i) is not list:
            raise TypeError("All arguments should be lists")
    if len(args) == 0:
        raise ValueError("Arguments should be provided!")
    inputs = list(itertools.product(*args))
    if show_counter and tqdmexists:
        for i in tqdm(range(len(inputs))):
            t_input = inputs[i]
            do_this(*t_input)
    else:
        for i in inputs:
            do_this(*i)
    

def set_hist_x_range(hist, x_low, x_high):
    hist.SetAxisRange(x_low, x_high, "X")

def set_hist_y_range(hist, y_low, y_high):
    hist.SetAxisRange(y_low, y_high, "Y")

def set_hist_bounds(hist, x_low, x_high, y_low, y_high):
    set_hist_x_range(hist, x_low, x_high)
    set_hist_y_range(hist, y_low, y_high)



def beta_gamma_coincidence_cut(gamma_window_width: float, beta_window_width: float, beta_background_start, radius: float = 0.5, gamma_window_start: float = 0, beta_window_start: float = 0, addback: bool = False, additional_cut: str = "") -> Tuple[str, str]:
    # signal gammas need to occur for betas in the peak of the decay curve
    sig_cut = f"{beta_gated_gamma(addback)} < {gamma_window_width + gamma_window_start} && " \
              f"{beta_gated_gamma(addback)} > {gamma_window_start} && " \
              f"{beta_decay_relative_time} > {beta_window_start} && " \
              f"{beta_decay_relative_time} < {beta_window_start + beta_window_width} && " \
              f"{beta_correlation_radius_func} < {radius}" \
              f"{'&&' if len(additional_cut) > 0 else ''} {additional_cut}"
    # background gamma don't have to be in the peak of the decay curve
    bg_cut  = f"{beta_gated_gamma(addback)} < {gamma_window_width + gamma_window_start} && " \
              f"{beta_gated_gamma(addback)} > {gamma_window_start} && " \
              f"{beta_decay_relative_time} > {beta_background_start} && " \
              f"{beta_decay_relative_time} < {beta_background_start + beta_window_width} && " \
              f"{beta_correlation_radius_func} < {radius}"\
              f"{'&& ' if len(additional_cut) > 0 else ''}{additional_cut}"
    return sig_cut, bg_cut

def nano_to_mili(*args):
    if len(args) == 0:
        raise ValueError("An argument must be supplied")
    if len(args) > 1:
        return [i * 1e-6 for i in args]
    return args[0] * 1e-6

def nano_to_micro(*args):
    if len(args) == 0:
        raise ValueError("An argument must be supplied")
    if len(args) > 1:
        return [i * 1e-3 for i in args]
    return args[0] * 1e-3

def mili_to_nano(*args) -> Union[float, List[float]]:
    if len(args) == 0:
        raise ValueError("An argument must be supplied")
    if len(args) > 1:
        return [float(i * 1e6) for i in args]
    return args[0] * 1e6

def micro_to_nano(*args):
    if len(args) == 0:
        raise ValueError("An argument must be supplied")
    if len(args) > 1:
        return [i * 1e3 for i in args]
    return args[0] * 1e3


def check_datadir(isotope="", log=None):
    if log is None:
        tlog = open("log.txt", "a")
    else:
        tlog = log
    # we want to check whether the data is available
    data_dir = os.environ["E19044_SIMPLE_ROOT"] if "E19044_SIMPLE_ROOT" in os.environ else "../data/"
    if 'E19044_DATA' in os.environ:
        tlog.write("Using environment variable!\n")
    else:
        tlog.write("Using default directory!\n")

    # we want to get the isotope names
    filenames = glob(data_dir+f"/{isotope}_mergerTest_r10.root")
    if len(filenames) == 0:
        tlog.write("failed to glob files!\n")
        
    if log is None:
        tlog.close()
    return filenames, data_dir

def formatted_datetime(date):
    return f"{date.date()} {date.time()}"

def duration_d_h_m(start, now):
    diff = now - start
    seconds = diff.total_seconds()
    
    day_in_second = 24 * 3600
    days = seconds // day_in_second
    seconds -= days * day_in_second
    
    hours = seconds // 3600
    seconds -= hours * 3600

    minutes = seconds // 60
    seconds -= 60 * minutes
    return f"{days:.0f}d, {hours:.0f} h, {minutes:.0f} m, {seconds:.1f} s"


def get_hist_max_y(hist, scale_factor = 1.0):
    return hist.GetBinContent(hist.GetMaximumBin()) * scale_factor

def auto_set_hist_y_range(hist, scale_factor = 1.1, hist_min = 0):
    set_hist_y_range(hist, hist_min, get_hist_max_y(hist, scale_factor))


def prep_chain(isotope=""):
    log = open("interactive_log.txt", "w+")

    files, data_dir = check_datadir(isotope, log)

    chain = ROOT.TChain(merged_tree_name)
    chain.Add(data_dir+f"/{isotope}_mergerTest_r10.root")
    return chain, log, data_dir, files

def extract_curves_and_average(isotope, field, chain, 
    binwidth, binlow, binhigh, 
    averaging_field, averaging_window_width, averaging_start, averaging_end,
    cut):
    if binhigh < binlow:
        raise ValueError("The high bin cannot be less than the low bin!")
    if binwidth <= 0:
        raise ValueError("Binwidth must be positive!")

    num_bins = int((binhigh - binlow) / binwidth)
    t_xs= [0] * num_bins
    t_ys= [0] * num_bins
    num_hists = int((averaging_end - averaging_start) / averaging_window_width)
    for i in range(num_hists):
        t_cut = f"{averaging_field} > {averaging_start + averaging_window_width * i} && {averaging_field} < {averaging_start + averaging_window_width * (i+1)}"
        signal = makeandfillhist1(field, num_bins, binlow, binhigh,
                                chain,
                                histtitle=f"signal {cut}",
                                histname = f"signal {isotope}",
                                cut = cut + f" && {t_cut}",
                                opt = "col")
        
        for kk in range(1, num_bins + 1):
            tbin = signal.GetBinCenter(kk) - binwidth
            if tbin < 100:
                continue
            mult = signal.GetBinContent(kk)
            t_xs[kk]  = tbin
            t_ys[kk] += int(mult)
    for i in range(len(t_ys)):
        t_ys[i] = t_ys[i] / num_hists 
    return (t_xs, t_ys)




def subtract_tuplehist(hist_a, hist_b):
    if(len(hist_a) != len(hist_b)):
        raise ValueError("Histograms must have the same dimension")
    for i in range(len(hist_a)):
        if(len(hist_a[i]) != len(hist_b[i])):
            raise ValueError("Histogram coordinates must have the same dimension!")
    rethist = [[0] * len(hist_a[0]), [0] * len(hist_a[1])]
    for i in range(len(hist_a[0])):
        # check that the bin centers are close
        if(hist_a[i][0] - hist_b[i][0] < 1e-6):
            rethist[i][0] = hist_a[i][0]
            rethist[i][1] = hist_a[i][1] - hist_b[i][1]
        else:
            raise ValueError("Tried to subtract histogram with non matching bins!")
    return rethist


def get_random_str(n):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def get_average_root_hist(isotope, field, chain, histtitle,
    binwidth, binlow, binhigh, 
    averaging_field, averaging_window_width, averaging_start, averaging_end,
    cut):
    if binhigh < binlow:
        raise ValueError("The high bin cannot be less than the low bin!")
    if binwidth <= 0:
        raise ValueError("Binwidth must be positive!")

    num_bins = int((binhigh - binlow) / binwidth)
    num_hists = int((averaging_end - averaging_start) / averaging_window_width)
    num_hists += 1 if (num_hists * averaging_window_width) + averaging_start < averaging_end else 0
    #print(f"Numhists: {num_hists}")
    hist = ""
    # quick and dirty silencing the warnings
    for i in range(num_hists):
        t_cut = f"{averaging_field} > {averaging_start + averaging_window_width * i} && {averaging_field} < {averaging_start + averaging_window_width * (i+1)}"
        #print(f"Avg num {i} ", cut + f" && {t_cut}")
        
        randomstr = get_random_str(100)
        signal = makeandfillhist1(field, num_bins, binlow, binhigh,
                                chain,
                                histtitle=f"signal {cut} {randomstr}",
                                histname = f"signal {isotope} {randomstr}",
                                cut = cut + f" && {t_cut}",
                                opt = "col")
        if i == 0:
            hist = signal
            sethistlabels(histtitle, field, "Counts", hist)
        else:
            hist.Add(signal, 1.0)
    hist.Scale(1.0 / num_hists)    
    return hist


def GammaEfficiencySingle(E) -> float:

    par = [  9.21812310e-01, -1.11413952e+02,  1.10874105e+02, 
        -4.69736304e+01,  1.09975808e+01, -1.53803784e+00,
         1.28566216e-01, -5.95030769e-03,  1.17662117e-04 ]

    #par = [-1.3173, -2.16543e4, 1428.57, 609.787, 76.4709, 0, -3.99319, 0, 0.0482672]
    if numpyexists:
        a = numpy.float_power(E, par[0])
        ret = numpy.zeros(numpy.shape(E))
        #print(ret, a)
        logE = numpy.log(E)
        for i in range(1, 9):
            #print(math.pow(logE, i), ",", ret)
            ret += numpy.multiply(par[i], numpy.float_power(logE, i-1))
            #print(math.pow(logE, i), ",", ret)
        return ret * a
    else:
        a = math.pow(E, par[0])
        ret = 0
        #print(ret, a)
        logE = math.log(E)
        for i in range(1, 9):
            #print(math.pow(logE, i), ",", ret)
            ret += par[i]* math.pow(logE, i-1)
            #print(math.pow(logE, i), ",", ret)
        return ret * a


def GammaEfficiencySingleFractional(E):
    return GammaEfficiencySingle(E) / 100.0


def gaussian_area(sigma, amplitude):
    return amplitude * sigma * math.sqrt(2 * math.pi)

def integrate_range(hist, low, high):
    nbins   = hist.GetNbinsX()
    lowbin  = hist.FindBin(low)
    highbin = hist.FindBin(high)
    if (lowbin == 0 or highbin == 0 or lowbin > nbins or highbin > nbins):
        raise ValueError("Bins must be in the histogram's range!")
    return hist.Integral(lowbin, highbin)

def background_subtract_hists(a, b):
    if a is not ROOT.TH1:
        raise TypeError(f"Argument a is of type {type(a)} expected {ROOT.TH1}")
    if b is not ROOT.TH1:
        raise TypeError(f"Argument b is of type {type(b)} expected {ROOT.TH1}")
    if a.GetNBinsX() != b.GetNBinsX():
        raise ValueError("Histograms must have the same number of bins!")
    tbins = a.GetNBinsX()
    for i in range(1, tbins + 1):
        a.SetBinContent(i, a.GetBinContent(i) - b.GetBinContent(i))

def background_subtract_flat(a: ROOT.TH1, b: numbers.Number, minbin: int = -1, maxbin: int = 1<<63):

    if a is not ROOT.TH1:
        raise TypeError(f"Argument a is of type {type(a)} expected {ROOT.TH1}")
    if not isinstance(b, numbers.Number):
        raise TypeError(f"Argument b is of type {type(b)} expected a Number!")
    if a.GetNBinsX():
        raise ValueError("Histograms must have the same number of bins!")
    tbins = a.GetNBinsX()
    # skip zero because the 0 bin is overflow
    tminbin = 1 if minbin < 1 else min(min(minbin, maxbin), tbins)

    tmaxbin = tbins + 1 if maxbin == 1<<63 else min(max(minbin, maxbin), tbins)
    for i in range(tminbin, tmaxbin):
        a.SetBinContent(i, a.GetBinContent(i) - b)

def mean_of_hist(hist: ROOT.TH1, range_low: float = -float('inf'), range_high: float = float('inf')) -> Tuple[float, float]:
    if hist is not ROOT.TH1:
        raise TypeError(f"Argument hist is of type {type(hist)} expected {ROOT.TH1}")
    if not isinstance(range_low, numbers.Number):
        raise TypeError(f"Argument range_low is of type {type(range_low)} expected a Number!")
    if not isinstance(range_low, numbers.Number):
        raise TypeError(f"Argument range_low is of type {type(range_low)} expected a Number!")
    if range_high < float('inf') or range_low > range_low + 1:
        set_hist_x_range(hist, range_low, range_high)
    mean = hist.GetMean()
    stddev = hist.GetStdDev()
    if range_high < float('inf') or range_low > range_low + 1:
        set_hist_x_range(hist, 0, 0)
    return mean, stddev


def beta_cut(timeLow: float = 0, timeWidth: float = 4, radius: float = 0.3, energyLow: float = 0, energyHigh: float = 600):
    return f"{beta_decay_relative_time} > {timeLow} && {beta_decay_relative_time} < {timeLow + timeWidth} && {beta_correlation_radius_func} < {radius} && {beta_decay_energy} > {energyLow} && {beta_decay_energy} < {energyHigh}"


    

def GammaEfficiencyAddBack(E) -> float:
    par = [  
         8.96128866e-01, -7.87998001e+01,  7.56353344e+01,
        -3.08630405e+01,  6.95291975e+00, -9.35052693e-01,
         7.51237951e-02, -3.34040409e-03,  6.34403866e-05
    ]
    #par = [1.00800970e+00, -3.10544139e+00, -4.72490093e+00,  5.74930365e+00,
    #    -2.33217555e+00,  4.80585376e-01, -5.45955994e-02,  3.27165800e-03,
    #    -8.11156667e-05]
    if numpyexists:
        a = numpy.float_power(E, par[0])
        ret = numpy.zeros(numpy.shape(E))
        logE = numpy.log(E)
        for i in range(1, 9):
            ret += numpy.multiply(par[i], numpy.float_power(logE, i - 1))
        return ret * a
    else:
        a = math.pow(E, par[0])
        ret = 0
        logE = math.log(E)
        for i in range(1, 9):
            ret += par[i] * math.pow(logE, i - 1)
        return ret * a

def GammaEfficiencyAddBackFractional(E) -> float:
    return GammaEfficiencyAddBack(E) / 100.0



def Igamma_scheme_to_tex(scheme, isotope, mother_decays, radius, fitResults):
    columns = []
    header_column = [isotope]
    header_column.extend([""]*(len(scheme) - 1))
    infocolumn = [mother_decays, radius, "?"]
    if (len(scheme) - 3) > 0:
        infocolumn.extend([""]*(len(scheme) - 3))
    columns.append(header_column)
    columns.append(infocolumn)
    energycolumn = []
    igexpcol = []
    iglitcol = []
    for i in scheme:
        energycolumn.append(i[0])
        cts = fitResults.get_count(i[0])
        igexpcol.append(f"{cts *100 / (GammaEfficiencyAddBackFractional(i[0]) * mother_decays):.2f}")
        iglitcol.append(i[1])
    columns.append(energycolumn)
    columns.append(igexpcol)
    columns.append(iglitcol)
    for i in columns:
        if len(i) < 3:
            i.extend([""] * (len(scheme) - 3))
    for i in columns:
        print(i)
    return table_to_tex(columns)


def Ibeta_scheme_to_tex(scheme, isotope, mother_decays, radius, fitResults):
    columns = []
    header_column = [isotope]
    header_column.extend([""]*(len(scheme) - 1))
    infocolumn = [mother_decays, radius, "?"]
    if (len(scheme) - 3) > 0:
        infocolumn.extend([""]*(len(scheme) - 3))
    columns.append(header_column)
    columns.append(infocolumn)

    energycolumn = []
    igexpcol = []
    iglitcol = []
    for i in scheme:
        cts = 0
        for j in i[1]:
            cts += fitResults.get_count(j)
        for j in i[2]:
            cts -= fitResults.get_count(j)
        cts = cts / (GammaEfficiencyAddBackFractional(i[0]) * mother_decays)
        igexpcol.append(f"{cts *100 / (GammaEfficiencyAddBackFractional(i[0]) * mother_decays):.2f}")
        iglitcol.append(i[1])

    columns.append(energycolumn)
    columns.append(igexpcol)
    columns.append(iglitcol)
    for i in columns:
        if len(i) < 3:
            i.extend([""] * (len(scheme) - 3))
    for i in columns:
        print(i)
    return table_to_tex(columns)

def add_errors_in_quadrature(*args) -> float:
    """Calculates the resulting fractional error of an arithmetic
    calculation given a list of iterables with the format (value, error)

    Raises:
        ValueError: raised when the input array is empty
        ValueError: raised when the inputs in the array have incorrect lengths

    Returns:
        float: The resulting fractional error of the calculation
    """
    if(len(args) < 1):
        raise ValueError("expected an iterable of non zero length!")
    accum = 0
    for i in args:
        if len(i) != 2:
            raise ValueError("iterables of length 2 expected!")
        # zero value means any error is infinite
        if i[0] == 0:
            continue
        accum += (i[1] / i[0]) * (i[1] / i[0])
    return math.sqrt(accum)

def beta_normalization(isotope: str, radius: str) -> dict:
    f = "../beta_halflives/figures_run_02_09_2023/all_normalizations.txt"
    with open(f) as fp:
        info = [i.split(", ") for i in fp.readlines()]
        header = info[0]
        filtered = [j for j in info if j[0] == isotope and j[1] == radius]
        if len(filtered) > 0:
            keys= [header[i] for i in range(1, len(filtered[0]))]
            values =[float(filtered[0][i]) for i in range(1, len(filtered[0]))]
            return dict(zip(keys, values))
        return {}

def sigma_to_fwhm(sigma) -> float:
    return 2* math.sqrt(2 * math.log(2)) * sigma


def pk_fix_fit(ctr: int, 
               diff: float, 
               fix_pk: float, 
               err_pk: float, 
               fix_sigma: float, 
               gammafitresults, sig_hist_choice, pks):
    """On a line/peak that can be represented as 
    a gaussian on a linear background, this fits the amplitude, 
    with the mean and variance fixed

    Args:
        ctr (int): key used for accessing the fit information and tagging the fitting function
        diff (float): width of the fitting window
        fix_pk (float): centroid of the gaussian
        err_pk (float): error in the centroid
        fix_sigma (float): variance of the gaussian
        gammafitresults (IgammaScheme): object that holds the fitting parameters from previous fits
        sig_hist_choice (RootHistDecoratorMultiD): contains the histogram to be fit
        pks: a list containing information about each peak
    Returns:
        ROOT.TF1: the function used to fit the line/peak
    """
    from .fit_result_wrapper import FitResultWrapper, FitResultSummary1D
    l    = ctr - diff
    r    = ctr + diff
    print("Make func", flush=True)
    constfunc_fit = ROOT.TF1(f"constfuncasd{ctr}", "[0]", l, r)
    print("Fit Background", flush=True)
    _ = sig_hist_choice.hist.Fit(constfunc_fit.GetName(), "SQLM", "", l, r)


    funcname_fit       = f"linconstfit{ctr}"
    linconstfuncpk_fit = ROOT.TF1(funcname_fit, "gaus(2) + [0] + ([1] * x)", l, r) # type: ignore
    linconstfuncpk_fit.SetParName(0, "Constant")
    linconstfuncpk_fit.SetParName(1, "Slope")
    linconstfuncpk_fit.SetParName(2, "Amplitude")
    linconstfuncpk_fit.SetParName(3, "Centroid")
    linconstfuncpk_fit.SetParName(4, "Sigma")

    linconstfuncpk_fit.SetParError(0, constfunc_fit.GetParError(0))
    linconstfuncpk_fit.SetParameter(0, constfunc_fit.GetParameter(0))
    linconstfuncpk_fit.SetParameter(2, 5)             # Amplitude
    linconstfuncpk_fit.FixParameter(3, fix_pk)    # Centroid
    linconstfuncpk_fit.SetParError(3, err_pk)
    linconstfuncpk_fit.SetParameter(4, fix_sigma) # Sigma

    print("Fit Signal", flush=True)

    sig_hist_choice.set_x_range(l-diff, r+diff)
    print(l, r)
    fitresult_fit = sig_hist_choice.hist.Fit(funcname_fit, "SQLM", "H", l, r)
    pkcenter_fit = linconstfuncpk_fit.GetParameter(3)
    print("Getting Standard Uncertainty", flush=True)
    pkerr_fit = get_standard_uncertainty_str(
        fix_pk, 
        err_pk
    )
    print("Drawing", flush=True)
    text_fit = ROOT.TLatex(
        linconstfuncpk_fit.GetParameter(3), 
        linconstfuncpk_fit.GetParameter(2), 
        f"{pkerr_fit} keV {pks[0][2]}") # type: ignore
    sig_hist_choice.auto_scale_y()
    sig_hist_choice.draw()
    linconstfuncpk_fit.Draw("same")
    text_fit.Draw("Same")

    print("Adding Fit Result", flush=True)
    gammafitresults.add_fit_result(
        ctr,
        FitResultWrapper(
            linconstfuncpk_fit, 
            text_fit,
            FitResultSummary1D(
            linconstfuncpk_fit.GetParameter(3), 
            linconstfuncpk_fit.GetParError(3), 
            abs(gaussian_area(linconstfuncpk_fit.GetParameter(4), linconstfuncpk_fit.GetParameter(2))), 
            l, r, 
            linconstfuncpk_fit.Integral(l, r), 
            linconstfuncpk_fit.IntegralError(l, r)),
            fitresult_fit,
            abs(linconstfuncpk_fit.GetParameter(4)) > diff,
            fitresult_fit.GetCovarianceMatrix()
        )
    )
    return linconstfuncpk_fit


def simpson_integration(low: float, high: float, step_size: float, fn: Callable[[float], float], hist_integral: bool) -> float:
    """Uses simpsons 3/8 integration to integrate a function on a range
    see -> https://en.wikipedia.org/wiki/Simpson%27s_rule
    Args:
        low (float): lower range of the integration
        high (float): upper range of the integration
        step_size (float): step size to integrate through
        fn (Callable[[float], float]): function to integrate over
        hist_integral (bool): if the function you're integrating was fit to a histogram, this should be True, 
        this ensuring that the integration returns the correct value
    Returns:
        float: result of the integration
    """
    post = 3.0 / 8.0
    # b - a = 3h -> h = step_size / 3
    h = step_size / 3
    ret = 0.0
    for a in numpy.arange(low, high, step_size):
        ret += fn(a) + 3 * fn(a + h) + 3 * fn(a + 2 * h) + fn(a + step_size )
    if hist_integral:
        ret /= step_size
    return ret * h * post

if __name__ == "__main__":
    args = sys.argv
    from . import parsing
    istestmode = parsing.parse_boolean(args, "test")
    