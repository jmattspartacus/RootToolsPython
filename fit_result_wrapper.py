import typing
import math
from .analysis_tools import sigma_to_fwhm

class FitResultSummary1D:
    def __init__(self, location: float, width: float, counts: float, fitlow: float, fithigh: float, fitintegral: float, fiterrorintegral: float) -> None:
        self.location = location
        self.width    = width
        self.counts   = counts
        self.fitlow   = fitlow
        self.fithigh  = fithigh
        self.fitintegral = fitintegral
        self.fiterrorintegral = fiterrorintegral
        

 
    def as_list(self):
        return [self.location, self.width, self.counts, self.fitlow, self.fithigh, self.fitintegral, self.fiterrorintegral]

    def copy(self):
        return FitResultSummary1D(*self.as_list())
    
    def __str__(self) -> str:
        return f"({self.as_list()})"


class FitResultWrapper:
    def __init__(self, func, text, summary: FitResultSummary1D, fitresult, bad_fit, covmat) -> None:
        self.func = func
        self.text = text
        self.summary = summary
        self.fitresult = fitresult
        self.bad_fit = bad_fit
        self.covariance_matrix = covmat
        

    def draw(self, drawoptions = "same", text_size: float = -1) -> None:
        if text_size > 0:
            self.text.SetTextSize(text_size)    
        self.text.Draw(drawoptions)
        self.func.Draw(drawoptions)

    def get_summary(self) -> FitResultSummary1D:
        return self.summary.copy()

    def get_count(self, warn_if_bad: bool = True) -> float:
        if self.bad_fit and warn_if_bad:
            print(f"Fit result has bad_fit flag, consider not using it")
        return self.summary.counts

    def get_error(self, warn_if_bad: bool = False) -> float:
        if self.bad_fit and warn_if_bad:
            print(f"Fit result has bad_fit flag, consider not using it")
        return self.summary.fiterrorintegral

    def get_error_lin_const_gauss(self, warn_if_bad: bool = False) -> float:
        if self.bad_fit and warn_if_bad:
            print(f"Fit result has bad_fit flag, consider not using it")
        # parameter 4 is sigma
        errSigma = math.pow(self.func.GetParError(4) / self.func.GetParameter(4), 2)
        # parameter 2 is amplitude
        errAmplitude   = math.pow(self.func.GetParError(2) / self.func.GetParameter(2), 2)
        return math.sqrt(errSigma + errAmplitude) * self.get_count()
    

    def get_fwhm(self, warn_if_bad: bool = False) -> float:
        if self.bad_fit and warn_if_bad:
            print(f"Fit result has bad_fit flag, consider not using it")
        return sigma_to_fwhm(abs(self.func.GetParameter(4)))
    



class MultiFitResult:
    def __init__(self) -> None:
        self.fits: typing.Dict[typing.Hashable, FitResultWrapper] = {}

    def add_fit_result(self, fitkey: typing.Hashable, fit: FitResultWrapper) -> None:
        self.fits[fitkey] = fit

    def get_result(self, key: typing.Hashable) -> typing.Union[FitResultWrapper, None]:
        if key in self.fits.keys():
            return self.fits[key]
        
    def get_count(self, key: typing.Hashable, warn_if_bad: bool = True) -> float:
        if key in self.get_keys():
            return self.fits[key].get_count(warn_if_bad)
        raise KeyError(f"key {key} does not exist")
    
    def get_error(self, key: typing.Hashable, warn_if_bad: bool = True) -> float:
        if key in self.get_keys():
            return self.fits[key].get_error(warn_if_bad)
        raise KeyError(f"key {key} does not exist")

    def get_error_lin_const_gauss(self, key: typing.Hashable, warn_if_bad: bool = True) -> float:
        if key in self.get_keys():
            return self.fits[key].get_error_lin_const_gauss(warn_if_bad)
        raise KeyError(f"key {key} does not exist")
    
    def get_fwhm(self, key: typing.Hashable, warn_if_bad: bool = True) -> float:
        if key in self.get_keys():
            return self.fits[key].get_fwhm(warn_if_bad)
        raise KeyError(f"key {key} does not exist")
        

    def draw(self, drawoptions = "same", text_size: float = -1) -> None:
        for i in self.fits:
            self.fits[i].draw(drawoptions, text_size)

    def get_summary(self, key: typing.Hashable) -> FitResultSummary1D:
        if key in self.get_keys():
            return self.fits[key].summary
        raise KeyError(f"key {key} does not exist")
        
    def get_summaries(self) -> typing.List[FitResultSummary1D]:
        ret = []
        for i in self.fits:
            ret.append(self.fits[i].get_summary())
        return ret

    def get_fit_results(self) -> list:
        ret = []
        for i in self.fits:
            ret.append(self.fits[i].fitresult)
        return ret

    def get_texts(self) -> list:
        ret = []
        for i in self.fits:
            ret.append(self.fits[i].text)
        return ret

    def get_func(self, key: typing.Hashable): 
        if key not in self.fits:
            raise KeyError(f"key {key} does not exist")
        return self.fits[key].func
    
    def get_funcs(self) -> list:
        ret = []
        for i in self.fits:
            ret.append(self.fits[i].func)
        return ret
    
    def get_keys(self) -> typing.List[typing.Hashable]:
        return [i for i in self.fits.keys()]

    def get_good_fit_keys(self) -> typing.List[typing.Hashable]:
        ret = []
        for i in self.get_keys():
            if not self.fits[i].bad_fit:
                ret.append(i)
        return ret

    def collect_good(self) -> typing.List[FitResultWrapper]:
        return [self.fits[i] for i in self.get_good_fit_keys()]




