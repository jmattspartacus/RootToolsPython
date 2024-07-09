import numbers
import ROOT
import typing
from typing import Tuple, List, Union, Mapping
from .handyutils import *
from .fit_result_wrapper import *
from .serialization import *
from .analysis_tools import gaussian_area, get_random_str
from .multi_thread_hist_fill import multi_thread_hist_fill_1D_chain
from .binning import *
import os
import json

cached_chains: Mapping[str, Mapping[str, Union[List[str], str]]] = {}




class RootHistDecorator:
    def __init__(self, 
            field: str, bin_width: float, low: float, high: float, 
            chain: Union[ROOT.TChain, Tuple[str, List[str]]], # type: ignore
            histtitle: str="default global", xlabel: str ="xlabel", ylabel: str = "ylabel",
            histname: str = "default-h1", cut: str = "", opt: str = "", 
            showstats: bool = False, autodraw: bool = False, build_hist: bool =True, num_workers: int = 16
        ):
        if num_workers < 1 or not isinstance(num_workers, int):
            num_workers = 1
        self.num_fill_workers = num_workers
        self.x_range = [low, high]
        self.field     = field
        self.chain     = chain
        self.cut       = cut
        thistname = (histname + '.')[:-1]
        if thistname == "default-h1":
            thistname = get_random_str(100)
        self.canvas = ROOT.TCanvas(thistname+"canvas", thistname+"canvas", 800, 600)# type: ignore
        self.histname  = thistname
        self.histtitle = histtitle
        self.xlabel    = xlabel
        self.ylabel    = ylabel
        if isinstance(chain, ROOT.TChain):  # type: ignore
            if not chain.GetName() in cached_chains: # type: ignore
                print()
        else:
            print()
        
        self.histchain = chain
        self.bin_width = bin_width
        self.binlow    = low
        self.binhigh   = high
        self.num_bins  = self.calculate_bins(low, high, bin_width)
        self.show_stats = showstats
        self.autodraw  = autodraw
        self.draw_options = opt
        self.peaks = {}
        if build_hist:
            self.rebuild_hist(False)
            self.y_range = [self.hist.GetMinimum(), self.hist.GetMaximum()]
            self.y_range_default = [self.hist.GetMinimum(), self.hist.GetMaximum()]
        else:
            self.y_range = [0, 0]
            self.y_range_default = [0, 0]


    def set_log_scale_y(self, enable: bool) -> None:
        setlogy(self.canvas, 1 if enable else 0)
        self.check_autodraw()


    def calculate_bins(self, binlow: float, binhigh: float, bin_width: float) -> int:
        """Calculates the number of bins given the extremal bin edges and per bin width

        Args:
            binlow (float): The left edge of the leftmost bin
            binhigh (float): The right edge of the rightmost bin
            bin_width (float): The width of each bin

        Returns:
            int: The number of bins in this histogram.
        """
        return int((binhigh - binlow) / bin_width)

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
        """Adds a peak to the list of peaks that are retained by the RootHistDecorator and fits it to the histogram

        Args:
            name (str): Name of the peak
            label (str): The label shown on the peak when draw() is called
            approximate_location (numbers.Number): The rough location of the peak
            fit_func_name (str): Name of the function used for the fit.
            fit_func_str (str): String that defines the function (ex. gaus(0) + [2]* x)
            fit_low (numbers.Number): Lower bound for the fit
            fit_high (numbers.Number): Upper bound for the fit
        """
        fit_func = ROOT.TF1(fit_func_name, fit_func_str, fit_low, fit_high)# type: ignore
        self.peaks[name] = (approximate_location, label, fit_func)
        self.hist.Fit(fit_func.GetName(), fit_low, fit_high)
        self.check_autodraw()


    def rebuild_hist(self, checkdraw=True):
        """Reconstructs the internal histogram. Necessary whenever major changes to the histogram are made, such as the binning, the field being plotted, etc.

        Args:
            checkdraw (bool, optional): Should we check whether we autodraw? If true draws after building. Defaults to True.
        """
        def makeandfillhist1(field, numbins, low, high, chain, histtitle="default global; default x; default y", histname = "default-h1", cut = "", opt = ""):
            hist = ROOT.TH1D(histname, histtitle, numbins, low, high)# type: ignore
            chain.Draw(field + ">>" + histname, cut, opt)
            return hist
        if len(self.chain.GetListOfFiles()) > 2 and self.num_fill_workers > 1:
            self.hist = multi_thread_hist_fill_1D_chain(
                self.chain, self.field, 
                Binning(self.bin_width, self.binlow, self.binhigh), 
                self.num_fill_workers, 
                self.histname, self.histtitle, self.cut)
        else:   
            self.hist = makeandfillhist1(self.field, self.num_bins, self.binlow, self.binhigh, self.chain, self.histtitle, self.histname, self.cut, self.draw_options)
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
        if not isinstance(range_low, numbers.Number):
            raise TypeError(f"Argument range_low is of type {type(range_low)} expected a Number!")
        if not isinstance(range_high, numbers.Number):
            raise TypeError(f"Argument range_high is of type {type(range_high)} expected a Number!")
        self.hist.SetAxisRange(range_low, range_high, "X")
        ret = self.hist.GetMean()
        self.hist.SetAxisRange(self.x_range[0], self.x_range[1], "X")
        return ret

    def reset_y_range(self):
        """Resets the y range shown on the histogram to the default values from it's creation.
        """
        self.set_y_range(self.y_range_default[0], self.y_range_default[1])
        self.check_autodraw()

    def reset_x_range(self):
        """Resets the x range shown on the histogram to the default values from it's creation
        """
        self.set_x_range(self.binlow + 1, self.binhigh - 1)
        self.check_autodraw()

    

    def set_x_range(self, range_low: float, range_high: float) -> None:
        if not isinstance(range_low, numbers.Number):
            raise TypeError(f"Argument x_low is of type {type(range_low)} expected a Number!")
        if not isinstance(range_high, numbers.Number):
            raise TypeError(f"Argument x_high is of type {type(range_high)} expected a Number!")
        self.x_range = [min(range_low, range_high), max(range_low, range_high)]
        self.hist.SetAxisRange(self.x_range[0], self.x_range[1], "X")
        self.check_autodraw()

    def set_y_range(self, range_low: float, range_high: float) -> None:
        if not isinstance(range_low, numbers.Number):
            raise TypeError(f"Argument x_low is of type {type(range_low)} expected a Number!")
        if not isinstance(range_high, numbers.Number):
            raise TypeError(f"Argument x_high is of type {type(range_high)} expected a Number!")
        self.y_range = [min(range_low, range_high), max(range_low, range_high)]
        self.hist.SetAxisRange(range_low, range_high, "Y")
        self.check_autodraw()

    def set_hist_bounds(self, x_low: float, x_high: float, y_low: float, y_high: float) -> None:
        """Simultaneously sets both x and y ranges

        Args:
            x_low (float): lowest x value to show
            x_high (float): highest x value to show
            y_low (float): lowest y value to show
            y_high (float): highest y value to show
        """
        self.set_x_range(x_low, x_high)
        self.set_y_range(y_low, y_high)
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
        tbins = self.hist.GetNbinsX()
        for i in range(1, tbins + 1):
            self.hist.SetBinContent(i, self.hist.GetBinContent(i) - otherhist.GetBinContent(i))
        self.check_autodraw()

    def background_subtract_hists(self, otherhist: 'RootHistDecorator', scale: float):
        """Subtracts another RootHistDecorator's histogram from this one's histogram, can be scaled to reflect weighting,etc

        Args:
            otherhist (RootHistDecorator): RootHistDecorator object to subtract from this one
            scale (float): Weighting of the subtraction, (ex 2. would subtract 2 times other from this one)

        Raises:
            TypeError: other must be a RootHistDecorator
            ValueError: Binning must be the same to have a meaningful subtraction.
        """
        if not isinstance(otherhist, RootHistDecorator):
            raise TypeError(f"Argument other is of type {type(otherhist)} expected {RootHistDecorator}")
        if self.hist.GetNbinsX() != otherhist.hist.GetNbinsX():
            raise ValueError("Histograms must have the same number of bins!")
        tbins = self.hist.GetNbinsX()
        for i in range(1, tbins + 1):
            self.hist.SetBinContent(i, self.hist.GetBinContent(i) - otherhist.hist.GetBinContent(i) * scale)
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
        self.check_autodraw()

    def get_max_y(self) -> float:
        """gets the weight of the histogram bin with the largest weight

        Returns:
            float: The weight of the bin with the most weight.
        """
        return self.hist.GetBinContent(self.hist.GetMaximumBin())


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

    def draw(self, options_override: str = ""): 
        """Draws the histogram on the internal canvas, using the given draw options if provided, else uses the default options.

        Args:
            options_override (str, optional): Specify drawing options to allow multiple histograms on the same plot for instance. Defaults to "".
        """
        self.canvas.cd()
        if options_override == "":
            self.hist.Draw(self.draw_options)
        else:
            self.hist.Draw(options_override)
        self.canvas.Draw()

    def set_cut(self, cut: str) -> None:
        """Sets the cut used to select events from the chain, and subsequently rebuilds the histogram.

        Args:
            cut (str): The cut used to select the events.
        """
        self.cut = cut
        self.rebuild_hist()
        
    def set_field(self, field: str) -> None:
        """Changes the data field represented by the histogram and rebuilds the histogram

        Args:
            field (str): The new field.
        """
        self.field = field
        self.rebuild_hist()

    def set_hist_name(self, name: str) -> None:
        """Sets the name of the histogram

        Args:
            name (str): New histogram name.
        """
        self.histname = name
        self.rebuild_hist()

    def set_hist_title(self, newtitle: str) -> None:
        """Sets the title of the histogram

        Args:
            title (str): New histogram title.
        """
        self.set_hist_labels(newtitle, self.xlabel, self.ylabel)

    def set_xlabel(self, label: str) -> None:
        """Sets the label for the x axis

        Args:
            label (str): New label for the x axis.
        """
        self.set_hist_labels(self.histtitle, label, self.ylabel)

    def set_ylabel(self, label: str) -> None:
        """Sets the label for the y axis

        Args:
            label (str): New label for the y axis.
        """
        self.set_hist_labels(self.histtitle, self.xlabel, label)

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

    def integrate_range(self, low: float = -float("inf"), high: float = float('inf'), discard_negative: bool = True) -> float:
        """Integrates the histogram over a range, if provided.

        Args:
            low (float, optional): Lower bound for the integration. Defaults to -float("inf").
            high (float, optional): Upper bound for the integration. Defaults to float('inf').
            discard_negative (bool, optional): If true, any bins that are negative are discarded in the integration. Defaults to True.

        Returns:
            float: _description_
        """
        minbin, maxbin = self.get_bins_for_edges(low, high)
        # if we're not discarding negative bins, then we can use the standard integration
        if not discard_negative:
            return self.hist.Integral(minbin, maxbin)
        else:
            accumulator = 0
            for i in range(minbin, maxbin + 1):
                binval = self.hist.GetBinContent(i)
                accumulator += (binval > 0) * binval
            return accumulator


    def redo_fits(self):
        """Refits all retained peaks in the RootHistDecorator
        """
        for i in self.peaks:
            self.hist.Fit(i[2], i[2].GetXmin(), i[2].GetXmax())

    def get_per_bin_average(self, discard_negative: bool = False):
        """Gets the average value of the bins on the current x range

        Args:
            discard_negative (bool, optional): If true, negative bins are ignored in the average. Defaults to False.

        Returns:
            _type_: _description_
        """
        integral = self.integrate_range(self.x_range[0], self.x_range[1], discard_negative=discard_negative)
        numbins = self.calculate_bins(self.x_range[0], self.x_range[1], self.bin_width)
        return integral / numbins

    def try_fit_peaks_lin_const_gauss(self, trypk: typing.List[typing.Tuple[float, float, str]], funcnamebase: str, fitting_options: str = "QLSM") -> MultiFitResult:
        """Takes a list of candidate peaks and tries to fit each of them using a function that is a gaussian plus linear and constant term.

        Args:
            trypk (typing.List[typing.Tuple[float, float, str]]): Candidate peaks to be fit
            funcnamebase (str): Base name of the function
            fitting_options (str, optional): Options used for the fitting, generally for histograms you should at least keep L to do log likelyhood fitting. Defaults to "QLSM".

        Returns:
            MultiFitResult: Summary of all the fits is stored here.
        """
        pks = MultiFitResult()
        for i in range(len(trypk)):
            pk = trypk[i][0]
            diff = trypk[i][1]
            fitlow = pk - diff
            fithigh = pk + diff
            self.set_x_range(pk - 100, pk + 100)

            funcname = f"linconstfit{pk}{funcnamebase}"
            linconstfuncpk = ROOT.TF1(funcname, "gaus(2) + [0] + ([1] * x)", fitlow, fithigh) # type: ignore
            linconstfuncpk.SetParName(0, "Constant")
            linconstfuncpk.SetParName(1, "Slope")
            linconstfuncpk.SetParName(2, "Amplitude")
            linconstfuncpk.SetParName(3, "Centroid")
            linconstfuncpk.SetParName(4, "Sigma")

            linconstfuncpk.SetParameter(2, 5)    # Amplitude
            linconstfuncpk.SetParameter(3, pk)   # Centroid
            linconstfuncpk.SetParameter(4, diff) # Sigma
            
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
                    FitResultSummary1D(
                        linconstfuncpk.GetParameter(3), # location is centroid
                        linconstfuncpk.GetParError(3), abs(gaussian_area(linconstfuncpk.GetParameter(4), linconstfuncpk.GetParameter(2))), fitlow, fithigh, linconstfuncpk.Integral(fitlow, fithigh), linconstfuncpk.IntegralError(fitlow, fithigh)),
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
        if not isinstance(low, numbers.Number):
            raise TypeError(f"Argument low is of type {type(low)} expected a Number!")
        if not isinstance(high, numbers.Number):
            raise TypeError(f"Argument high is of type {type(high)} expected a Number!")
        low = low if(low < self.x_range[0]) else self.x_range[0]
        high = high if(high < self.x_range[1]) else self.x_range[1]
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
                "binlow" : self.binlow,
                "binhigh" : self.binhigh,
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
    def __load_from_json(path: str) -> 'RootHistDecorator':
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
    ) -> 'RootHistDecorator':
        numbins = histogram.GetNbinsX()
        low     = histogram.GetXaxis().GetXmin()
        high    = histogram.GetXaxis().GetXmax()
        bin_width = (high - low) / numbins
        xlabel = histogram.GetXaxis().GetTitle() if xlabel == "" else xlabel
        ylabel = histogram.GetYaxis().GetTitle() if ylabel == "" else ylabel
        title  = histogram.GetTitle() if title == "" else title
        name   = histogram.GetName() if name == "" else name
        ret     = RootHistDecorator(field, bin_width, low, high, chain, title, xlabel, ylabel, name, opt=opt, cut=cut, showstats=showstats, autodraw=autodraw, build_hist=False)
        ret.hist = histogram
        ret.y_range_default = [ret.hist.GetMinimum(), ret.hist.GetMaximum()]
        ret.y_range = [ret.hist.GetMinimum(), ret.hist.GetMaximum()]
        ret.check_autodraw()
        return ret
    
    @staticmethod
    def load_from_file(path: str) -> 'RootHistDecorator':
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} does not exist!")
            
        
        supported_formats = ["json"]
        fileext = path.split(".")[-1].lower()
        if fileext not in supported_formats:
            raise ValueError(f"{path} is not a supported file format, choose from {supported_formats}")

    
        if fileext == "json":
            return RootHistDecorator.__load_from_json(path)
        else:
            raise NotImplementedError(f"{fileext} is a supported format, but implementation is not defined.")
        