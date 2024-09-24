import numbers
import ROOT
import typing
from typing import Tuple, List, Union, Mapping
from .handyutils import *
from .fit_result_wrapper import *
from .serialization import *
from .analysis_tools import gaussian_area, get_random_str
from .multi_thread_hist_fill import *
from .binning import *
from .root_macro_interfaces import *
import os
import json
import hashlib
import pathlib

cached_chains: Mapping[str, Mapping[str, Union[List[str], str]]] = {}




class RootHistDecoratorMultiD:
    def __init__(self, 
            field: str, 
            chain: Union[ROOT.TChain, Tuple[str, List[str]]], # type: ignore
            xbinning: Binning, 
            ybinning: Binning = Binning(0, 0, 0), 
            zbinning: Binning = Binning(0, 0, 0), 
            histtitle: str = "default global", 
            xlabel: str = "xlabel", 
            ylabel: str = "ylabel", 
            zlabel: str = "zlabel", 
            histname: str = "default-h", 
            cut: str = "", 
            opt: str = "", 
            showstats: bool = False, 
            autodraw: bool = False, 
            build_hist: bool = True, 
            num_workers: int = 16, 
            cache_location: str = "./cached_data/hists/", 
            force_rebuild: bool = False
        ):
        """

        Args:
            field (str): The branch of the tree or chain being used to fill the histogram
            chain (Union[ROOT.TChain, Tuple[str, List[str]]]): the chain being used to fill the histogram, 
            or a list of files containing root trees that can be used to fill the tree
            xbinning (Binning, optional): Binning used for the x axis.
            ybinning (Binning, optional): Binning used for the y axis if applicable. Defaults to Binning(0, 0, 0).
            zbinning (Binning, optional): Binning for the z axis if applicable. Defaults to Binning(0, 0, 0).
            histtitle (str, optional): Title of the histogram, needs to be unique, as root uses this on it's backend to store and retrieve the histogram. Defaults to "default global".
            xlabel (str, optional): label for the x axis. Defaults to "xlabel".
            ylabel (str, optional): label for the y axis. Defaults to "ylabel".
            zlabel (str, optional): label for the z axis if applicable. Defaults to "zlabel".
            histname (str, optional): name of the histogram, this is shown at the top of the panel when drawing by default. Defaults to "default-h".
            cut (str, optional): The cut applied to select events to fill the histogram. Defaults to "".
            opt (str, optional): draw options used for drawing the histogram. Defaults to "".
            showstats (bool, optional): If true, the statistics of the histogram are shown, they are not always accurate reflecation of the histogram. Defaults to False.
            autodraw (bool, optional): if true, the histogram will be drawn anytime something is changed. Defaults to False.
            build_hist (bool, optional): if true, the histogram is filled immediately when the constructor is called. Defaults to True.
            num_workers (int, optional): number of threads used to fill the histogram if it is a multithreaded build candidate. Defaults to 16.
            cache_location (str, optional): the location that cached copies of the histogram are saved when filled, if already built, this is the location that rebuild_hist looks for the cached histogram. Defaults to "./cached_data/hists/".
            force_rebuild (bool, optional): If true this will cause the histogram to be refilled even if it's already been made and cached. Defaults to False.

        Raises:
            ValueError: Raised when the dimension of the histogram is determined to be more than 3 because it's not supported.
        """
        if num_workers < 1 or not isinstance(num_workers, int):
            num_workers = 1
        self.num_fill_workers = num_workers
        fspl = field.split(":")
        if len(fspl) > 3:
            raise ValueError("RootHistDecoratorMultiD does not support more than 3D histograms at this time")
        self.dimension = len(fspl)
        self.xfield = fspl[0]
        self.yfield = fspl[1] if self.dimension > 1 else "none"
        self.zfield = fspl[2] if self.dimension > 2 else "none"

        self.field     = field
        self.chain     = chain
        self.cut       = cut
        thistname      = (histname + '.')[:-1]

        # want to generate a random name if the name is default
        # this is to prevent clobbering the object's in root's 
        # internal directory system
        if thistname == "default-h":
            thistname = get_random_str(100)

        self.canvas         = ROOT.TCanvas(thistname+"canvas", thistname+"canvas", 800, 600)# type: ignore
        self.histname       = thistname
        self.histtitle      = histtitle
        self.xlabel         = xlabel
        self.ylabel         = ylabel
        self.zlabel         = zlabel
        self.histchain      = chain
        
        self.binning        = [ xbinning, ybinning, zbinning ]
        self.num_bins       = [i.get_num_bins() for i in self.binning]
        self.ranges: list[Tuple[float, float]]         = [(0,0), (0,0), (0,0)]
        self.default_ranges: list[Tuple[float, float]]   = [(0,0), (0,0), (0,0)]
        self.show_stats     = showstats
        self.autodraw       = autodraw
        self.draw_options   = opt
        self.peaks          = {}
        self.cache_location = cache_location
        self.histfile = None
        self.cache_loaded = False
        if build_hist:
            self.rebuild_hist(False, force_rebuild=False)
            
    @staticmethod
    def from_dict(d):
        field = d["field"] if "field" in d else None
        chain = d["chain"] if "chain" in d else None
        xbinning = d["xbinning"] if "xbinning" in d else None
        ybinning = d["ybinning"] if "ybinning" in d else Binning(0, 0, 0)
        zbinning = d["zbinning"] if "zbinning" in d else Binning(0, 0, 0)
        histtitle = d["histtitle"] if "histtitle" in d else "default global"
        xlabel = d["xlabel"] if "xlabel" in d else "xlabel"
        ylabel = d["ylabel"] if "ylabel" in d else "ylabel"
        zlabel = d["zlabel"] if "zlabel" in d else "zlabel"
        histname = d["histname"] if "histname" in d else "default-h"
        cut = d["cut"] if "cut" in d else ""
        opt = d["opt"] if "opt" in d else ""
        showstats = d["showstats"] if "showstats" in d else False
        autodraw = d["autodraw"] if "autodraw" in d else False
        build_hist = d["build_hist"] if "build_hist" in d else True
        num_workers = d["num_workers"] if "num_workers" in d else 16
        cache_location = d["cache_location"] if "cache_location" in d else "./cached_data/hists/"
        force_rebuild = d["force_rebuild"] if "force_rebuild" in d else False
        a=[field, chain, xbinning, ybinning, zbinning, 
           histtitle, xlabel, ylabel, zlabel, histname, 
           cut, opt, showstats, autodraw, build_hist, 
           num_workers, cache_location, force_rebuild]
        if field is None or chain is None or xbinning is None:
            return None
        return RootHistDecoratorMultiD(*a)
    
    def get_is_cached_and_hash(self, path) -> Tuple[bool, str]:
        hashstring = "".join([
            self.histname, 
            self.field, 
            str(self.cut), 
            f"Binning(x={self.binning[0]},y={self.binning[1]},z={self.binning[2]})",
            self.histtitle, 
            self.xlabel, 
            self.ylabel, 
            self.zlabel
        ])
        hashvalue = hashlib.md5(bytes(hashstring.encode("ascii")), usedforsecurity=False).hexdigest()
        return os.path.exists(path+hashvalue+".root"), hashvalue


    def set_log_scale_y(self, enable: bool) -> None:
        setlogy(self.canvas, 1 if enable else 0)
        self.check_autodraw()


    def get_mean(self) -> float:
        """Returns the mean of the histogram on the currently displayed range

        Returns:
            float: the mean of the histogram on the currently displayed range
        """
        return self.hist.GetMean()

    def get_stddev(self) -> float:
        """Returns the standard devation of the mean of the histogram on the currently displayed range

        Returns:
            float: the standard deviation of the mean of the histogram on the currently displayed range
        """
        return self.hist.GetStdDev()

    def add_peak(self, name: str, label: str, approximate_location: numbers.Number, fit_func_name: str, fit_func_str: str, fit_low: numbers.Number, fit_high: numbers.Number) -> None:
        """Adds a peak to the list of peaks that are retained by the RootHistDecoratorMultiD and fits it to the histogram

        Args:
            name (str): Name of the peak
            label (str): The label shown on the peak when draw() is called
            approximate_location (numbers.Number): The rough location of the peak
            fit_func_name (str): Name of the function used for the fit.
            fit_func_str (str): String that defines the function (ex. gaus(0) + [2]* x)
            fit_low (numbers.Number): Lower bound for the fit
            fit_high (numbers.Number): Upper bound for the fit
        """
        if self.dimension > 1:
            raise ValueError("add_peak is intended for user with 1D histograms!")
        fit_func = ROOT.TF1(fit_func_name, fit_func_str, fit_low, fit_high)# type: ignore
        self.peaks[name] = (approximate_location, label, fit_func)
        self.hist.Fit(fit_func.GetName(), fit_low, fit_high)
        self.check_autodraw()

    def get_bin_low(self, axis: int):
        if axis < 0 or axis > 2:
            raise ValueError("Axis must be in the range 0-2")
        return self.binning[axis].bin_low
    
    def get_bin_high(self, axis: int):
        if axis < 0 or axis > 2:
            raise ValueError("Axis must be in the range 0-2")
        return self.binning[axis].bin_high
    
    def get_bin_width(self, axis: int):
        if axis < 0 or axis > 2:
            raise ValueError("Axis must be in the range 0-2")
        return self.binning[axis].bin_width
    
    def get_num_bins(self, axis: int):
        if axis < 0 or axis > 2:
            raise ValueError("Axis must be in the range 0-2")
        return self.binning[axis].get_num_bins()

    def is_chain_multithread_candidate(self) -> bool:
        return len(self.chain.GetListOfFiles()) > 2 and self.num_fill_workers > 1

    def rebuild_hist(self, checkdraw=True, force_rebuild=False):
        """Reconstructs the internal histogram. Necessary whenever major changes to the histogram are made, such as the binning, the field being plotted, etc.

        Args:
            checkdraw (bool, optional): Should we check whether we autodraw? If true draws after building. Defaults to True.
        """
        exists, _ = self.get_is_cached_and_hash(self.cache_location)
        if self.histfile is not None:
            # prevent file ptr errors
            self.histfile.Close()
        self.cache_loaded = False
        if not exists or force_rebuild:
            self.hist = multi_thread_hist_fill_KD_chain(self.chain, self.field, self.binning, self.dimension, self.num_fill_workers, self.histname, self.histtitle, self.cut)
            self.cache_hist()
        # load cached hist even on rebuild because 
        # SaveAs does something funky with
        # the histogram making it CPPYYNONE
        # which causes something like nullptr deref when 
        self.load_cached()
    
        for i in range(self.dimension):
            self.ranges[i]         = (self.binning[i].bin_low, self.binning[i].bin_high)
            self.default_ranges[i] = (self.binning[i].bin_low, self.binning[i].bin_high)
        # if we're in 1D, we need to retain the default y axis values
        if self.dimension == 1:
            self.ranges[1]         = (self.hist.GetMinimum(), self.hist.GetMaximum())
            self.default_ranges[1] = (self.hist.GetMinimum(), self.hist.GetMaximum())
        # if we're in 2D, we need to retain the default z axis values
        elif self.dimension == 2:
            self.ranges[2]         = (self.hist.GetMinimum(), self.hist.GetMaximum())
            self.default_ranges[2] = (self.hist.GetMinimum(), self.hist.GetMaximum())
        elif self.dimension > 3:
            raise ValueError("Somehow tried to build a histogram of dimension > 3, which is not currently implemented")
        self.set_hist_labels(self.histtitle, self.xlabel, self.ylabel)
        self.redo_fits()
        if checkdraw:
            self.check_autodraw()

    def get_mean_on_range(self, range_low: float, range_high: float) -> float:
        """Gets the average value of bins on the range specified.

        Args:
            range_low (float): Lowest x to include in the range
            range_high (float): Highest x to include in the range

        Raises:
            TypeError: range_low must be a number
            TypeError: range_high must be a number

        Returns:
            float: mean value of the bins on the range specified
        """
        if self.dimension > 1:
            raise ValueError("get_mean_on_range not implemented for dimension > 1")
        if not isinstance(range_low, numbers.Number):
            raise TypeError(f"Argument range_low is of type {type(range_low)} expected a Number!")
        if not isinstance(range_high, numbers.Number):
            raise TypeError(f"Argument range_high is of type {type(range_high)} expected a Number!")
        self.set_x_range(range_low, range_high)
        ret = self.hist.GetMean()
        self.set_x_range(self.ranges[0][0], self.ranges[0][1])
        return ret

    def reset_x_range(self):
        """Resets the x range of the histogram to it's value at creation
        """
        self.set_x_range(self.default_ranges[0][0] + 1, self.default_ranges[0][1] - 1)

    def reset_y_range(self):
        """Resets the y range of the histogram to it's value at creation
        """
        self.set_y_range(self.default_ranges[1][0] + 1, self.default_ranges[1][1] - 1)

    def reset_z_range(self):
        """Resets the z range of the histogram to it's value at creation
        """
        self.set_z_range(self.default_ranges[2][0] + 1, self.default_ranges[2][1] - 1)

    def set_x_range(self, range_low: float, range_high: float) -> None:
        """Sets the range of the x axis of the histogram to the values given

        Args:
            range_low (float): The lower end of the range
            range_high (float): The higher end of the range
        """
        self.set_axis_range(range_low, range_high, 0)

    def set_y_range(self, range_low: float, range_high: float) -> None:
        """Sets the range of the y axis of the histogram to the values given

        Args:
            range_low (float): The lower end of the range
            range_high (float): The higher end of the range
        """
        self.set_axis_range(range_low, range_high, 1)
        
    def set_z_range(self, range_low: float, range_high: float) -> None:
        """Sets the range of the z axis of the histogram to the values given

        Args:
            range_low (float): The lower end of the range
            range_high (float): The higher end of the range
        """
        self.set_axis_range(range_low, range_high, 2)

    def set_axis_range(self, range_low: float, range_high: float, axis: int) -> None:
        """Sets the range of the given axis to the given range, if low/high are flipped,
        they'll be corrected. 

        Args:
            range_low (float): The lower end of the range
            range_high (float): The upper end of the range
            axis (int): The axis we're setting the range for

        Raises:
            TypeError: raised if x_low is not a number
            TypeError: raised if x_high is not a number
            TypeError: raised if axis is not an integer
            ValueError: raised if axis < 0 or if axis is not less than dimension.
        """
        if not isinstance(range_low, numbers.Number):
            raise TypeError(f"Argument x_low is of type {type(range_low)} expected a Number!")
        if not isinstance(range_high, numbers.Number):
            raise TypeError(f"Argument x_high is of type {type(range_high)} expected a Number!")
        if not isinstance(axis, int):
            raise TypeError(f"Argument axis is of type {type(axis)} expected integer!")
        if axis < 0 or axis > self.dimension:
            raise ValueError("Cannot set the range of an axis that does not exist")
        axis_str = ["X", "Y", "Z"][axis]
        self.ranges[axis] = (min(range_low, range_high), max(range_low, range_high))
        self.hist.SetAxisRange(self.ranges[axis][0], self.ranges[axis][1], axis_str)
        self.check_autodraw()
        

    def set_hist_bounds(self, bounds: List[Tuple[float, float]]) -> None:
        """Allows you to simultaneously set the bounds of all axes in the histogram

        Args:
            bounds (List[Tuple[float, float]]): _description_
        """
        for i in range(max(len(bounds), 3)):
            self.set_axis_range(bounds[i][0], bounds[i][1], i)
        self.check_autodraw()

    def check_autodraw(self) -> None:
        """Checks autodraw and draws it if it is true.
        """
        self.hist.SetStats(self.show_stats)
        if self.autodraw:
            self.draw()

    def background_subtract_hists(self, otherhist: ROOT.TH1): # type: ignore
        """Performs a background subtraction from this histogram, using a ROOT.TH1

        Args:
            otherhist (ROOT.TH1): The histogram being subtracted.

        Raises:
            TypeError: Other must be a ROOT.TH1
            ValueError: The binning must be the same in order to meaningfully subtract them.
        """
        if not isinstance(otherhist, ROOT.TH1):# type: ignore
            raise TypeError(f"Argument other is of type {type(otherhist)} expected {ROOT.TH1}")# type: ignore
        if self.hist.GetNbinsX() != otherhist.GetNbinsX():
            raise ValueError("Histograms must have the same number of bins!")
        if self.dimension > 1:
            raise ValueError("Background subtraction for histograms with >1D not yet supported")
        tbins = self.hist.GetNbinsX()
        for i in range(1, tbins + 1):
            self.hist.SetBinContent(i, self.hist.GetBinContent(i) - otherhist.GetBinContent(i))
        self.hist.Sumw2()
        self.check_autodraw()

    def background_subtract_hists(self, otherhist: 'RootHistDecoratorMultiD', scale: float):
        """Subtracts another RootHistDecoratorMultiD's histogram from this one's histogram, can be scaled to reflect weighting,etc

        Args:
            otherhist (RootHistDecoratorMultiD): RootHistDecoratorMultiD object to subtract from this one
            scale (float): Weighting of the subtraction, (ex 2. would subtract 2 times other from this one)

        Raises:
            TypeError: other must be a RootHistDecoratorMultiD
            ValueError: Binning must be the same to have a meaningful subtraction.
        """
        if not isinstance(otherhist, RootHistDecoratorMultiD):
            raise TypeError(f"Argument other is of type {type(otherhist)} expected {RootHistDecoratorMultiD}")
        if self.hist.GetNbinsX() != otherhist.hist.GetNbinsX():
            raise ValueError("Histograms must have the same number of bins!")
        tbins = self.hist.GetNbinsX()
        for i in range(1, tbins + 1):
            self.hist.SetBinContent(i, self.hist.GetBinContent(i) - otherhist.hist.GetBinContent(i) * scale)
        self.hist.Sumw2()
        self.check_autodraw()

    def background_subtract_flat(self, b: float) -> None:
        """Subtracts a flat amount from each bin in the histogram.

        Args:
            b (float): Amount to subtract from each bin.

        Raises:
            TypeError: amount must be a number
        """
        if not isinstance(b, numbers.Number):
            raise TypeError(f"Argument b is of type {type(b)} expected a Number!")
        tbins = self.hist.GetNbinsX()
        for i in range(1, tbins):
            self.hist.SetBinContent(i, self.hist.GetBinContent(i) - b)
        self.hist.Sumw2()
        self.check_autodraw()

    def get_max_y(self) -> float:
        """gets the weight of the histogram bin with the largest weight

        Returns:
            float: The weight of the bin with the most weight.
        """
        return self.hist.GetBinContent(self.hist.GetMaximumBin())

    def get_bin_val_for_coordinate(self, val) -> float:
        if self.dimension == 1:
            return self.hist.GetBinContent(self.hist.FindBin(val))
        elif self.dimension < 4:
            return self.hist.GetBinContent(self.hist.FindBin(*val))
        else:
            raise ValueError("Tried to get a bin value for a histogram of dimension more than 3, which is unsupported")
            

    def get_max_bin_center(self) -> float:
        """gets the location of the histogram bin with the largest weight

        Returns:
            float: The location of the bin with the most weight.
        """
        return self.hist.GetBinCenter(self.hist.GetMaximumBin())


    def auto_scale_y(self, hist_min: float = 0.0, scale_factor: float = 1.1):
        """Sets the y range to set the min at the given value, and scales the max y to 
        be scale * maxy

        Args:
            hist_min (float, optional): The lowest value to show on the y axis. Defaults to 0.0.
            scale_factor (float, optional): How much of the max y should the max y shown be?. Defaults to 1.1.

        Raises:
            TypeError: hist_min must be a number
            TypeError: scale_factor must be a number
        """
        if not isinstance(hist_min, numbers.Number):
            raise TypeError(f"Argument hist_min is of type {type(hist_min)} expected a Number!")
        if not isinstance(scale_factor, numbers.Number):
            raise TypeError(f"Argument scale_factor is of type {type(scale_factor)} expected a Number!")
        self.set_y_range(hist_min, self.get_max_y() * scale_factor)
        self.check_autodraw()
    
    def set_draw_options(self, new_options: str) -> None:
        """Sets the retained draw options for drawing the histogram

        Args:
            new_options (str): draw options to use when drawing the histogram by default after this
        """
        self.draw_options = new_options
        self.check_autodraw()

    def draw(self, options_override: str = "", cd: bool = True): 
        """Draws the histogram on the internal canvas, using the given draw options if provided, else uses the default options.

        Args:
            options_override (str, optional): Specify drawing options to allow multiple histograms on the same plot for instance. Defaults to "".
        """
        draw_same = "same" in options_override.lower()
        try:
            if self.canvas is None:
                random_name = random_string(32)
                self.canvas = ROOT.TCanvas(random_name+"_title", random_name+"_name", 800, 480)
            if cd and not draw_same:
                self.canvas.cd()
        except Exception as e:
            random_name = random_string(32)
            self.canvas = ROOT.TCanvas(random_name+"_title", random_name+"_name", 800, 480)
        finally:
            if cd and not draw_same:
                self.canvas.cd()
        if options_override == "":
            self.hist.Draw(self.draw_options)
        else:
            self.hist.Draw(options_override)
        if not draw_same:
            self.canvas.Draw()

    def set_cut(self, cut: str, force_rebuild_hist=False) -> None:
        """Sets the cut used to select events from the chain, and subsequently rebuilds the histogram.

        Args:
            cut (str): The cut used to select the events.
        """
        self.cut = cut
        self.rebuild_hist(force_rebuild=force_rebuild_hist)

    def set_hist_name(self, name: str, force_rebuild_hist=False) -> None:
        """Sets the name of the histogram

        Args:
            name (str): New histogram name.
        """
        self.histname = name
        self.rebuild_hist(force_rebuild=force_rebuild_hist)

    def set_hist_title(self, newtitle: str) -> None:
        """Sets the title of the histogram

        Args:
            title (str): New histogram title.
        """
        self.hist.SetTitle(newtitle)

    def set_xlabel(self, label: str) -> None:
        """Sets the label for the x axis

        Args:
            label (str): New label for the x axis.
        """
        self.hist.GetXaxis().SetTitle(label)

    def set_ylabel(self, label: str) -> None:
        """Sets the label for the y axis

        Args:
            label (str): New label for the y axis.
        """
        self.hist.GetYaxis().SetTitle(label)

    def set_center_xlabel(self, center: bool = True) -> None:
        """Sets the label for the x axis to be centered or not

        Args:
            center (bool, optional): Whether we center the x axis. Defaults to True.
        """
        self.hist.GetXaxis().CenterTitle(center)

    def set_center_ylabel(self, center: bool = True) -> None:
        """Sets the label for the y axis to be centered or not

        Args:
            center (bool, optional): Whether we center the y axis. Defaults to True.
        """
        self.hist.GetYaxis().CenterTitle(center)

    def set_hist_labels(self, histtitle: str ="", xlabel: str="", ylabel: str="") -> None:
        """Sets the histogram title, and x and y labels simultaneously

        Args:
            histtitle (str, optional): New title for the histogram. Defaults to "".
            xlabel (str, optional): New label for the x axis. Defaults to "".
            ylabel (str, optional): New label for the y axis. Defaults to "".
        """
        histtitle = self.histtitle if histtitle == "" else histtitle
        xlabel = self.xlabel if xlabel == "" else xlabel
        ylabel = self.ylabel if ylabel == "" else ylabel

        self.hist.SetTitle(histtitle+ ";" + xlabel + ";" + ylabel)
        self.check_autodraw()

    def integrate_range(self, low: float = -float("inf"), high: float = float('inf'), discard_negative: bool = True, give_err: bool =False) -> Union[float,  Tuple[float, float]]:
        """Integrates the histogram over a range, if provided.

        Args:
            low (float, optional): Lower bound for the integration. Defaults to -float("inf").
            high (float, optional): Upper bound for the integration. Defaults to float('inf').
            discard_negative (bool, optional): If true, any bins that are negative are discarded in the integration. Defaults to True.

        Returns:
            float: _description_
        """
        if self.dimension > 1:
            raise ValueError("integrate range not implemented for dimension > 1!")
        minbin, maxbin = self.get_bins_for_edges(low, high)
        # if we're not discarding negative bins, then we can use the standard integration
        if not discard_negative:
            if give_err:
                err = ROOT.Double()
                val = self.hist.IntegralAndError(minbin, maxbin, err)
                return val, err
            else:
                return self.hist.Integral(minbin, maxbin)
        else:
            accumulator_err = 0
            accumulator = 0
            for i in range(minbin, maxbin + 1):
                binval = self.hist.GetBinContent(i)
                binerr = self.hist.GetBinError(i)
                accumulator += (binval > 0) * binval
                accumulator_err += (binval > 0) * binerr
            if give_err:
                return accumulator, accumulator_err
            else:
                return accumulator


    def redo_fits(self):
        """Refits all retained peaks in the RootHistDecoratorMultiD
        """
        for i in self.peaks:
            self.hist.Fit(i[2], i[2].GetXmin(), i[2].GetXmax())

    def get_per_bin_average(self, discard_negative: bool = False, give_err: bool = False):
        """Gets the average value of the bins on the current x range

        Args:
            discard_negative (bool, optional): If true, negative bins are ignored in the average. Defaults to False.

        Returns:
            _type_: _description_
        """
        if self.dimension > 1:
            raise ValueError("get_per_bin_average not implemented for dimension > 1!")
        integral = self.integrate_range(self.ranges[0][0], self.ranges[0][1], discard_negative=discard_negative, give_err=give_err)
        numbins = calculate_bins(self.ranges[0][0], self.ranges[0][1], self.binning[0].bin_width)
        if give_err:
            return integral[0] / numbins, integral[1] / numbins
        else:
            return integral / numbins

    def try_fit_peaks_lin_const_gauss(self, trypk: typing.List[typing.Tuple[float, float, str, float, bool]], funcnamebase: str, fitting_options: str = "QLSM") -> MultiFitResult:
        """Takes a list of candidate peaks and tries to fit each of them using a function that is a gaussian plus linear and constant term.

        Args:
            trypk (typing.List[typing.Tuple[float, float, str]]): Candidate peaks to be fit
            funcnamebase (str): Base name of the function
            fitting_options (str, optional): Options used for the fitting, generally for histograms you should at least keep L to do log likelyhood fitting. Defaults to "QLSM".

        Returns:
            MultiFitResult: Summary of all the fits is stored here.
        """
        if self.dimension > 1:
            raise ValueError("try_fit_peaks_lin_const_gauss is not currently supported for multidimensional histograms!")
        pks = MultiFitResult()
        for i in range(len(trypk)):
            pk = trypk[i][0]
            diff = trypk[i][1]
            fixpk = trypk[i][4]
            fitlow = pk - diff
            fithigh = pk + diff
            self.set_x_range(pk - 100, pk + 100)

            funcname = f"linconstfit{pk}{funcnamebase}"
            linconstfuncpk = ROOT.TF1(funcname, "gaus(2) + [0] + ([1] * x)", fitlow, fithigh) # type: ignore
            linconstfuncpk.SetParameter(2, 5)
            if fixpk:
                #print("Fix pk at", pk, "with diff", diff, "with caption ", trypk[i][2])
                linconstfuncpk.FixParameter(3, pk)
            else:
                linconstfuncpk.SetParameter(3, pk)
            linconstfuncpk.SetParameter(4, diff)
            
            fitresult = self.hist.Fit(funcname, fitting_options, "H", fitlow, fithigh)
            pkcenter = linconstfuncpk.GetParameter(3)
            pkerr    = get_standard_uncertainty_str(
                pkcenter, 
                linconstfuncpk.GetParError(3)
            )
            text = ROOT.TLatex(linconstfuncpk.GetParameter(3), linconstfuncpk.GetParameter(2), f"{pkerr} keV {trypk[i][2]}") # type: ignore
            self.auto_scale_y()
            text.Draw("same")

            pks.add_fit_result(
                pk,
                FitResultWrapper(
                    linconstfuncpk, 
                    text,
                    FitResultSummary1D(linconstfuncpk.GetParameter(3), linconstfuncpk.GetParError(3), abs(gaussian_area(linconstfuncpk.GetParameter(4), linconstfuncpk.GetParameter(2))), fitlow, fithigh, linconstfuncpk.Integral(fitlow, fithigh), linconstfuncpk.IntegralError(fitlow, fithigh)),
                    fitresult,
                    abs(linconstfuncpk.GetParameter(4)) > diff,
                    fitresult.GetCovarianceMatrix()
                )
            )
            
        self.autodraw = True
        self.reset_x_range()
        self.auto_scale_y()
            
        return pks
    
    def get_bins_for_edges(self, low: float = -float("inf"), high: float = float('inf')) -> Tuple[int, int]:
        """Gets the two bins that are closest to the provided values. Can be used to help with doing for loops over ranges of bins.

        Args:
            low (float, optional): lowest x value. Defaults to -float("inf").
            high (float, optional): highest x value. Defaults to float('inf').

        Raises:
            TypeError: Must be a number to be meaningful
            TypeError: Must be a number to be meaningful

        Returns:
            Tuple[int, int]: Returns the low edge bin and high edge bin
        """
        if self.dimension > 1:
            func_name = "get_bins_for_edges"
            raise ValueError(f"{func_name} is not currently supported for multidimensional histograms!")
        if not isinstance(low, numbers.Number):
            raise TypeError(f"Argument low is of type {type(low)} expected a Number!")
        if not isinstance(high, numbers.Number):
            raise TypeError(f"Argument high is of type {type(high)} expected a Number!")
        low = low if(low < self.ranges[0][0]) else self.ranges[0][0]
        high = high if(high < self.ranges[0][1]) else self.ranges[0][1]
        nbins   = self.hist.GetNbinsX()
        lowbin  = self.hist.FindBin(low)

        # edge bins contain garbage that's outside the histogram range
        if lowbin == 0:
            lowbin += 1
        highbin = self.hist.FindBin(high)
        if highbin >= nbins + 1:
            highbin -= 1
            
        minbin: int = min(lowbin, highbin)
        maxbin: int = max(lowbin, highbin)
        return (minbin, maxbin)

    def get_bin_values_hist(self, low: float = -float("inf"), high: float = float('inf'), discard_negative: bool = True) -> List[float]:
        """Gets a histogram of the bins, returned as a list of the centers, with multiplicity being the weight of the respective bins.

        Args:
            low (float, optional): Lowest x value to get. Defaults to -float("inf").
            high (float, optional): Highest x value to get. Defaults to float('inf').
            discard_negative (bool, optional): If true, skips bins that are negative. Defaults to True.

        Returns:
            _type_: Output histogram
        """
        if self.dimension > 1:
            func_name = "get_bin_values_hist"
            raise ValueError(f"{func_name} is not currently supported for multidimensional histograms!")
        minbin, maxbin = self.get_bins_for_edges(low, high)
        ret = []
        for i in range(minbin, maxbin + 1):
            binctr = self.hist.GetBinCenter(i)
            binval = self.hist.GetBinContent(i)
            if binval < 0 and discard_negative:
                continue
            ret.extend([binctr] * binval)
        return ret
    
    def get_bin_values_pairs(self, low: float = -float("inf"), high: float = float('inf'), discard_negative: bool = True) -> List[Tuple[float, float]]:
        """Gets a list of the bins with their weights.

        Args:
            low (float, optional): Lowest x value to get. Defaults to -float("inf").
            high (float, optional): Highest x value to get. Defaults to float('inf').
            discard_negative (bool, optional): If true, skips bins that are negative. Defaults to True.

        Returns:
            _type_: _description_
        """
        if self.dimension > 1:
            func_name = "get_bin_values_pairs"
            raise ValueError(f"{func_name} is not currently supported for multidimensional histograms!")
        minbin, maxbin = self.get_bins_for_edges(low, high)
        ret = []
        for i in range(minbin, maxbin + 1):
            binctr = self.hist.GetBinCenter(i)
            binval = self.hist.GetBinContent(i)
            if binval < 0 and discard_negative:
                continue
            ret.append((binctr, binval))
        return ret

    def get_x_for_max_y(self) -> float:
        """Gets the center of the bin with the largest y value on the current range

        Returns:
            float: Center of the bin with the largest y value on the range.
        """
        return self.hist.GetBinCenter(self.hist.GetMaximumBin())

    def save_to_file(self, path: str, overwrite: bool = False) -> None:
        if os.path.exists(path) and not overwrite:
            raise FileExistsError(f"{path} exists, if you want to overwrite, use 'overwrite=True'")
            return
        
        supported_formats = ["json"]
        fileext = path.split(".")[-1].lower()
        if fileext not in supported_formats:
            raise ValueError(f"{fileext} is not a supported file format, choose from {supported_formats}")
            return
        if fileext == "json":
            self.__save_to_json(path)
            
        else:
            raise NotImplementedError(f"{fileext} is a supported format, but implementation is not defined.")

    def __save_to_json(self, path: str) -> None:
        outdict = {
                "x_range" : self.x_range,
                "field" : self.field,
                "chain_files" : [i.GetTitle() for i in self.chain.GetListOfFiles()], # type: ignore
                "cut" : self.cut,
                "canvas_name" : self.canvas.GetTitle(),
                "histname" : self.histname,
                "histtitle" : self.histtitle,
                "xlabel" : self.xlabel,
                "ylabel" : self.ylabel,
                "histchain" : self.histchain,
                "bin_width" : self.bin_width,
                "binlow" : self.binning[0].bin_low,
                "binhigh" : self.binning[0].bin_high,
                "num_bins" : self.num_bins,
                "show_stats" : self.show_stats,
                "autodraw" : self.autodraw,
                "draw_options" : self.draw_options,
                "peaks" : self.peaks,
                "y_range" : self.y_range,
                "y_range_default" : self.y_range_default,
                "hist_path":f"{path.replace(path.split('.')[-1], 'root')}"
            }
        save_as_json(outdict, path, indent=1)
        self.hist.SaveAs(outdict["hist_path"])

    @staticmethod
    def __load_from_json(path: str) -> 'RootHistDecoratorMultiD':
        reqkeys = [
                "x_range",
                "field",
                "chain_files",
                "cut",
                "canvas_name",
                "histname",
                "histtitle",
                "xlabel",
                "ylabel",
                "histchain",
                "bin_width",
                "binlow",
                "binhigh",
                "num_bins",
                "show_stats",
                "autodraw",
                "draw_options",
                "peaks",
                "y_range",
                "y_range_default",
                "hist_path"
            ]
        indict = load_from_json(path)
        for i in reqkeys:
            if i not in indict:
                raise KeyError(f"Required key {i} not found in serialized object!")
    
        

    # field: str, bin_width: float, low: float, high: float, 
    #         chain: Union[ROOT.TChain, Tuple[str, List[str]]], # type: ignore
    #         histtitle: str="default global", xlabel: str ="xlabel", ylabel: str = "ylabel",
    #         histname: str = "default-h1", cut: str = "", opt: str = "", 
    #         showstats: bool = False, autodraw: bool = False, build_hist: bool =True
        
    @staticmethod
    def construct_from_histogram(
        field:     str,
        chain:     ROOT.TChain, # type: ignore
        histogram: ROOT.TH1D, # type: ignore
        title:     str  = "",
        xlabel:    str  = "",
        ylabel:    str  = "",
        name:      str  = "",
        opt:       str  = "",
        cut:       str  = "",
        showstats: bool = False, 
        autodraw:  bool = False
    ) -> 'RootHistDecoratorMultiD':
        dims = len(field.split(":"))
        numbins = histogram.GetNbinsX()
        low     = histogram.GetXaxis().GetXmin()
        high    = histogram.GetXaxis().GetXmax()
        bin_width = (high - low) / numbins
        xbinning = Binning(bin_width, low, high)
        if dims > 1:
            numbins = histogram.GetNbinsY()
            low     = histogram.GetYaxis().GetYmin()
            high    = histogram.GetYaxis().GetYmax()
            bin_width = (high - low) / numbins
            _ybinning = Binning(bin_width, low, high)
        else:
            _ybinning = Binning(0,0,0)
        if dims > 2:
            numbins = histogram.GetNbinsY()
            low     = histogram.GetYaxis().GetYmin()
            high    = histogram.GetYaxis().GetYmax()
            bin_width = (high - low) / numbins
            _zbinning = Binning(bin_width, low, high)
        else:
            _zbinning = Binning(0, 0, 0)
        if dims > 3:
            raise ValueError("Cannot handle histograms of dimension > 3")
        xlabel = histogram.GetXaxis().GetTitle() if xlabel == "" else xlabel
        ylabel = histogram.GetYaxis().GetTitle() if ylabel == "" else ylabel
        title  = histogram.GetTitle() if title == "" else title
        name   = histogram.GetName() if name == "" else name
        ret    = RootHistDecoratorMultiD(field, chain, xbinning, ybinning=_ybinning, zbinning=_zbinning,
                                           histtitle=title, xlabel=xlabel, 
                                          ylabel=ylabel, histname=name, opt=opt, cut=cut, 
                                          showstats=showstats, autodraw=autodraw, build_hist=False)
        ret.hist = histogram
        ret.check_autodraw()
        return ret
    
    @staticmethod
    def load_from_file(path: str) -> 'RootHistDecoratorMultiD':
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} does not exist!")
            
        
        supported_formats = ["json"]
        fileext = path.split(".")[-1].lower()
        if fileext not in supported_formats:
            raise ValueError(f"{path} is not a supported file format, choose from {supported_formats}")

    
        if fileext == "json":
            return RootHistDecoratorMultiD.__load_from_json(path)
        else:
            raise NotImplementedError(f"{fileext} is a supported format, but implementation is not defined.")
        

    def split(self, ranges):
        ret = []
        # expect (low, high, name)
        for i in ranges:
            if self.dimension == 1:
                thist = ROOT.TH1D(i[2], i[2], calculate_bins(i[0], i[1], self.binning[0].bin_width), i[0], i[1])

                binlow = self.hist.FindBin(i[0])
                binhigh = self.hist.FindBin(i[1])
                print(i[2], binlow, binhigh)
                ct = 0
                for bin in range(binlow, binhigh):
                    thist.SetBinContent(ct, self.hist.GetBinContent(bin))
                    ct += 1
            else:
                raise NotImplementedError("split not implemented for dimension > 1")
            
            t = RootHistDecoratorMultiD.construct_from_histogram(self.field, 
                                                                 self.chain, thist, i[2], self.xlabel, self.ylabel, i[2], self.draw_options,
                                                                 self.cut, self.show_stats, self.autodraw
                                                                 )
            t.autodraw = False
            t.set_xlabel(self.xlabel)
            t.set_ylabel(self.ylabel)
            ret.append(t)
        return ret
    
    def dump_to_csv(self, filepath: str, overwrite: bool = False) -> None:
        if os.path.exists(filepath) and not overwrite:
            raise ValueError("Tried to write to a file that exists without giving the overwrite flag!")
        xrng = [i for i in self.ranges[0]]
        yrng = [i for i in self.ranges[1]]
        self.reset_x_range()
        bins = self.get_bin_values_pairs()
        self.set_x_range(*xrng)
        self.set_y_range(*yrng)
        with open(filepath, "w+") as fp:
            fp.write(f"{self.xfield}, counts\n")
            for i in bins:
                fp.write(", ".join([str(j) for j in i])+"\n")

    def project_onto_x(self, title: str = "projection") -> 'RootHistDecoratorMultiD':
        return self.project_onto_axis("x", title)
    def project_onto_y(self, title: str = "projection") -> 'RootHistDecoratorMultiD':
        return self.project_onto_axis("y", title)
    def project_onto_z(self, title: str = "projection") -> 'RootHistDecoratorMultiD':
        return self.project_onto_axis("z", title)

    def project_onto_axis(self, axis: str, title: str = "projection") -> 'RootHistDecoratorMultiD':
        if self.dimension > 3 or self.dimension < 0:
            raise ValueError("Cannot project an N>3 or N<0 dimensional histogram")
        rhist = {
            "x": self.hist.ProjectionX,
            "y": self.hist.ProjectionY if self.dimension > 1 else self.hist.ProjectionX,
            "z": self.hist.ProjectionZ if self.dimension > 2 else self.hist.ProjectionX
        }[axis]()
        axis_idx = {
            1:{"x" : 0},
            2:{"y" : 0, "x" : 1},
            3:{"z" : 0, "y" : 1, "x" : 2},
        }[self.dimension][axis]
        rtitle  = self.histtitle + f"_{axis}_{title}"
        rname   = self.histname  + f"_{axis}_{title}"
        rhist.SetTitle(rtitle)
        rhist.SetName(rname)
        if self.dimension == 1:
            ret = RootHistDecoratorMultiD.construct_from_histogram(
                self.field,
                self.chain,
                self.hist, 
                self.histtitle+"_copy",
                self.xlabel,
                self.ylabel,
                self.histname+"_copy",
                self.draw_options,
                self.cut,
                self.show_stats,
                self.autodraw
            )
        else:
            ret = RootHistDecoratorMultiD.construct_from_histogram(
                self.field.split(":")[axis_idx],
                self.chain,
                rhist, 
                rtitle,
                self.xlabel,
                self.ylabel,
                rname,
                self.draw_options,
                self.cut,
                self.show_stats,
                self.autodraw
            )
        ret.binning  = [i for i in self.binning]
        ret.num_bins = [i.get_num_bins() for i in self.binning]
        ret.default_ranges = [i for i in self.default_ranges]
        ret.cache_location = self.cache_location
        ret.histfile = None
        return ret
    
    def cache_hist(self) -> None:
        _, hashvalue = self.get_is_cached_and_hash(self.cache_location)
        # this is just the directory, not the file location
        if not os.path.exists(self.cache_location):
            pathlib.Path(self.cache_location).mkdir(parents=True, exist_ok=True)
        # always cache on rebuild
        self.hist.SaveAs(self.cache_location+hashvalue+".root")

    def load_cached(self) -> None:
        _, hashvalue = self.get_is_cached_and_hash(self.cache_location)
        # this is just the directory and not the file location
        if os.path.exists(self.cache_location+hashvalue+".root") and not self.cache_loaded:
            self.cache_loaded = True
            self.histfile = ROOT.TFile.Open(self.cache_location+hashvalue+".root")
            self.hist = TFileGetHist(self.histfile, self.histname, self.dimension)