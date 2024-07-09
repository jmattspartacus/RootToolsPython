from .root_macro_interfaces import PyEnableImplicitMT
from .analysis_tools import calculate_bins, get_random_str
from . import quiet_root
from .binning import *
import multiprocessing
import ROOT
from typing import List



def makeandfillhist1(field, binning: Binning, chain, histtitle="default global; default x; default y", histname = "default-h1", cut = "", opt = ""):
    hist = ROOT.TH1D(histname, histtitle, binning.get_num_bins(), binning.bin_low, binning.bin_high)# type: ignore
    chain.Draw(field + ">>" + histname, cut, opt)
    return hist

def makeandfillhist2(field, binning: List[Binning], chain, histtitle="default global; default x; default y", histname = "default-h1", cut = "", opt = ""):
    hist = ROOT.TH2D(histname, histtitle, 
                        binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high,
                        binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high)# type: ignore
    chain.Draw(field + ">>" + histname, cut, opt)
    return hist

def makeandfillhist3(field, binning: List[Binning], chain, histtitle="default global; default x; default y", histname = "default-h1", cut = "", opt = ""):
    hist = ROOT.TH2D(histname, histtitle, 
                        binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high,
                        binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high,
                        binning[2].get_num_bins(), binning[2].bin_low, binning[2].bin_high)# type: ignore
    chain.Draw(field + ">>" + histname, cut, opt)
    return hist







def fill_hist_thread_1D(
    arg
    ):
    with quiet_root.Quiet(ROOT.kFatal) as _: #type: ignore
        tree_name: str = arg[0]
        file: str = arg[1]
        field: str = arg[2]
        num_bins: int = arg[3]
        bin_low: float = arg[4]
        bin_high: float = arg[5]
        cut: str = arg[6]
        t_local_chain = ROOT.TChain(tree_name) #type: ignore
        t_local_chain.Add(file)
        histname=get_random_str(32)
        t_local_hist = ROOT.TH1D(histname, histname, num_bins, bin_low, bin_high) #type: ignore
        t_local_chain.Draw(f"{field}>>{histname}", cut, "goff")
        return t_local_hist
    
def fill_hist_thread_2D(
    arg
    ):
    with quiet_root.Quiet(ROOT.kFatal) as _: #type: ignore
        tree_name: str    = arg[0]
        file: str         = arg[1]
        field: str        = arg[2]
        x_num_bins: int   = arg[3]
        x_bin_low: float  = arg[4]
        x_bin_high: float = arg[5]
        cut: str          = arg[6]
        y_num_bins: int   = arg[7]
        y_bin_low: float  = arg[8]
        y_bin_high: float = arg[9]
        t_local_chain = ROOT.TChain(tree_name) #type: ignore
        t_local_chain.Add(file)
        histname=get_random_str(32)
        t_local_hist = ROOT.TH2D(histname, histname, x_num_bins, x_bin_low, x_bin_high, y_num_bins, y_bin_low, y_bin_high) #type: ignore
        t_local_chain.Draw(f"{field}>>{histname}", cut, "goff")
        return t_local_hist
    
def fill_hist_thread_3D(
    arg
    ):
    with quiet_root.Quiet(ROOT.kFatal) as _: #type: ignore
        tree_name: str    = arg[0]
        file: str         = arg[1]
        field: str        = arg[2]
        x_num_bins: int   = arg[3]
        x_bin_low: float  = arg[4]
        x_bin_high: float = arg[5]
        cut: str          = arg[6]

        y_num_bins: int   = arg[7]
        y_bin_low: float  = arg[8]
        y_bin_high: float = arg[9]

        z_num_bins: int   = arg[7+3]
        z_bin_low: float  = arg[8+3]
        z_bin_high: float = arg[9+3]

        t_local_chain = ROOT.TChain(tree_name) #type: ignore
        t_local_chain.Add(file)
        histname=get_random_str(32)
        t_local_hist = ROOT.TH3D(histname, histname, 
                                 x_num_bins, x_bin_low, x_bin_high, 
                                 y_num_bins, y_bin_low, y_bin_high, 
                                 z_num_bins, z_bin_low, z_bin_high) #type: ignore
        t_local_chain.Draw(f"{field}>>{histname}", cut, "goff")
        return t_local_hist


def multi_thread_hist_fill_1D(
    tree_name: str,
    file_list: List[str],
    field: str,
    binning: Binning,
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH1D: #type: ignore
    PyEnableImplicitMT(num_threads)
    task_list = [[tree_name, i, field, binning.get_num_bins(), binning.bin_low, binning.bin_high, cut] for i in file_list]
    # run this in parallel
    with multiprocessing.Pool(num_threads) as p:
        hists = p.map(fill_hist_thread_1D, task_list)
    # create empty histogram for the results
    hist = ROOT.TH1D(name, title, binning.get_num_bins(), binning.bin_low, binning.bin_high) #type: ignore
    for i in hists:
        hist.Add(i, 1)
    return hist

def multi_thread_hist_fill_2D(
    tree_name: str,
    file_list: List[str],
    field: str,
    binning: List[Binning],
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH2D: #type: ignore
    PyEnableImplicitMT(num_threads)
    task_list = [[tree_name, i, field, binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high, cut, binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high] for i in file_list]
    # run this in parallel
    with multiprocessing.Pool(num_threads) as p:
        hists = p.map(fill_hist_thread_2D, task_list)
    # create empty histogram for the results
    hist = ROOT.TH2D(name, title, binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high, binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high) #type: ignore
    for i in hists:
        hist.Add(i, 1)
    return hist

def multi_thread_hist_fill_3D(
    tree_name: str,
    file_list: List[str],
    field: str,
    binning: List[Binning],
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH3D: #type: ignore
    PyEnableImplicitMT(num_threads)
    task_list = [[
        tree_name, i, field, 
        binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high, cut, 
        binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high,
        binning[2].get_num_bins(), binning[2].bin_low, binning[2].bin_high] for i in file_list]
    # run this in parallel
    with multiprocessing.Pool(num_threads) as p:
        hists = p.map(fill_hist_thread_3D, task_list)
    # create empty histogram for the results
    hist = ROOT.TH3D(name, title, 
                     binning[0].get_num_bins(), binning[0].bin_low, binning[0].bin_high, 
                     binning[1].get_num_bins(), binning[1].bin_low, binning[1].bin_high, 
                     binning[2].get_num_bins(), binning[2].bin_low, binning[2].bin_high,) #type: ignore
    for i in hists:
        hist.Add(i, 1)
    return hist

def multi_thread_hist_fill_1D_chain(
    chain:ROOT.TChain, #type: ignore
    field: str,
    binning: Binning,
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH1D: #type: ignore
    file_list = [i.GetTitle() for i in chain.GetListOfFiles()]
    tree_name = chain.GetName()
    return multi_thread_hist_fill_1D(
        tree_name, file_list, field, 
        binning,
        num_threads, name, title, 
        cut)


def multi_thread_hist_fill_2D_chain(
    chain:ROOT.TChain, #type: ignore
    field: str,
    binning: List[Binning],
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH2D: #type: ignore
    file_list = [i.GetTitle() for i in chain.GetListOfFiles()]
    tree_name = chain.GetName()
    return multi_thread_hist_fill_2D(
        tree_name, file_list, field, 
        binning, 
        num_threads, name, title, 
        cut)

def multi_thread_hist_fill_3D_chain(
    chain:ROOT.TChain, #type: ignore
    field: str,
    binning: List[Binning],
    num_threads: int,
    name: str = "HistNameDefault",
    title: str = "HistTitleDefault",
    cut: str = ""
) -> ROOT.TH2D: #type: ignore
    file_list = [i.GetTitle() for i in chain.GetListOfFiles()]
    tree_name = chain.GetName()
    return multi_thread_hist_fill_3D(
        tree_name, file_list, field, 
        binning, 
        num_threads, name, title, 
        cut)


def is_chain_multithread_candidate(num_workers: int, chain: ROOT.TChain) -> bool:
    return len(chain.GetListOfFiles()) > 2 and num_workers > 1

def multi_thread_hist_fill_KD_chain(
        chain: ROOT.TChain,
        field: str,
        binning: List[Binning],
        dimension: int,
        num_threads: int,
        name: str = "HistNameDefault",
        title: str = "HistTitleDefault",
        cut: str = ""
    ):
        if is_chain_multithread_candidate(num_threads, chain):
            file_list = [i.GetTitle() for i in chain.GetListOfFiles()]
            tree_name = chain.GetName()
            if dimension == 1:
                return multi_thread_hist_fill_1D(
                    tree_name, file_list, field, 
                    binning[0], 
                    num_threads, name, title, 
                    cut)
            elif dimension == 2:
                return multi_thread_hist_fill_2D(
                    tree_name, file_list, field, 
                    binning[:2], 
                    num_threads, name, title, 
                    cut)
            elif dimension == 3:
                return multi_thread_hist_fill_3D(
                    tree_name, file_list, field, 
                    binning, 
                    num_threads, name, title, 
                    cut)
            else:
                raise ValueError("Histograms of dimension > 3 are not supported at this time!")
        else:
            if dimension == 1:
                return makeandfillhist1(field, binning[0], chain, title, name, cut, "goff")
            elif dimension == 2:
                return makeandfillhist2(field, binning[:2], chain, title, name, cut, "goff")
            elif dimension == 3:
                return makeandfillhist2(field, binning, chain, title, name, cut, "goff")
            else:
                raise ValueError("Histograms of dimension > 3 are not supported at this time!")