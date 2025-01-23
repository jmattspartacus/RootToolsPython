from .analysis_tools import GammaEfficiencyAddBackFractional, add_errors_in_quadrature
from .gamma_efficiency_by_isotope import *
import math
from typing import List, Tuple, Hashable, Union


class IgammaScheme:
    def __init__(self, 
                 isotope: str, 
                 mother_decays: float, 
                 mother_decay_err: float, 
                 radius: Union[float , str], 
                 tmax: float, 
                 use_per_isotope_efficiency: bool = True, 
                 preferred_efficiency_curve: str = ""
                ) -> None:
        self.scheme = {}
        self.isotope = isotope
        self.mother_decays = mother_decays
        self.mother_decays_err = mother_decay_err
        self.radius = radius
        self.tmax = tmax
        self.use_per_isotope_efficiency = use_per_isotope_efficiency
        self.preferred_isotope_efficiency = preferred_efficiency_curve if preferred_efficiency_curve != "" else isotope

    def add_levels(self, lvls: List[Tuple[Hashable, float, float, float, Union[str, float], float]]) -> None:
        for i in lvls:
            self.add_level(*i)

    def add_level(self, key: Hashable, peak: float, counts: float, error: float, literature: Union[str, float], fwhm: float) -> None:
        self.scheme[key] = {
            "pk" : peak,
            "counts" : counts,
            "err" : error,
            "lit" : literature,
            "fwhm" : fwhm,
        }

    def __str__(self) -> str:
        postfix = f"\tUsing efficiency curve from {self.preferred_isotope_efficiency}\n" if self.preferred_isotope_efficiency != self.isotope else ""
        ret =f"{self.isotope} I_gamma for {self.mother_decays} mother decays for radius {self.radius}, for dT < {self.tmax}\n{postfix}"
        # for each key, build the string for that line
        for i in self.scheme:
            val = self.scheme[i]
            i_gamma = self.__igamma_after_efficiency(val)
            error = add_errors_in_quadrature(*[
                (self.mother_decays, self.mother_decays_err), 
                (val["counts"], val["err"])]
            ) * i_gamma
            
            ret += f"\t{val['pk']:>8.2f} keV {self.get_counts(i):>10.0f} cts {self.__fhwm_phrase(i)} measured {i_gamma*100:>7.3f}% pm {error*100:>7.3f}% literature {val['lit']}\n"
        return ret

    def get_igamma_relative(self, key: Hashable, refline: Hashable = None) -> Tuple[Hashable, float, float, float, float]:
        eff = lambda energy: gamma_efficiency_by_isotope(energy, self.preferred_isotope_efficiency, True)
        if refline is None or refline not in self.scheme:
            refline = self.get_most_intense()
        pk = self.get_peak(key)
        
        if key == refline:
            cts = self.__igamma_after_efficiency(key)
            errterm = math.sqrt(
                (self.mother_decays_err * self.mother_decays_err) / (self.mother_decays * self.mother_decays) + 
                (self.get_err(key) / self.get_counts(key)) * (self.get_err(key) / self.get_counts(key))
            ) * cts
            return (key, pk, cts, errterm, 100)
        premult = eff(refline) / self.get_counts(refline)
        ierr =  eff(refline) / self.get_err(refline)
        tmult = lambda E: self.get_counts(key) * premult / eff(E)
        terr = lambda E: self.get_err(key) * ierr / eff(E)
        try:
            litrel = self.get_lit(key) / self.get_lit(refline)
        except:
            litrel = 0
        return (key, pk, tmult(pk), terr(pk), litrel)
    

    def get_igammas(self) -> List[Tuple[float, float, float]]:
        ret = []
        for i in self.scheme:
            val = self.scheme[i]
            cts = self.__igamma_after_efficiency(val)
            error = add_errors_in_quadrature(*[
                (self.mother_decays, self.mother_decays_err), 
                (val["counts"], val["err"])]
            )
            ret.append((i, cts, error))
        return ret

    def get_igamma(self, key: Hashable) -> Tuple[Hashable, float, float, float]:
        val = self.scheme[key]
        i_gamma = self.__igamma_after_efficiency(val)
        # calculate fractional error of i_gamma and then multiply by i_gamma
        error = add_errors_in_quadrature(*[
            (self.mother_decays, self.mother_decays_err), 
            (val["counts"], val["err"])]
        )
        
        #print("Igamma calculation compare error calcs err:", error, "igamma:", i_gamma, "total_err:", i_gamma * error, "cts:", val["counts"], "ctserr:", val["err"])
        return (key, self.get_peak(key), i_gamma, error * i_gamma)
    
    
    def get_rel_str(self, include_fwhm: bool = False) -> str:
        postfix = f"\tUsing efficiency curve from {self.preferred_isotope_efficiency}\n" if self.preferred_isotope_efficiency != self.isotope else ""
        ret =f"{self.isotope} I_gamma relative for {self.mother_decays} mother decays for radius {self.radius}, for dT < {self.tmax}\n{postfix}"
        refline = self.get_most_intense()
        fwhm_phrase = self.__fhwm_phrase(refline) if include_fwhm else ""
        ret += f"\t{self.scheme[refline]['pk']:>6.2f} keV {fwhm_phrase} most intense with literature absolute intensity {self.scheme[refline]['lit']}%\n"
        for i in self.scheme.keys():
            if i == refline:
                continue
            rel = self.get_igamma_relative(i)
            fwhm_phrase = self.__fhwm_phrase(i) if include_fwhm else""
            ret += f"\t{rel[1]:>6.2f} keV {fwhm_phrase} measured {rel[2] * 100:.3f}% pm {rel[3]:.3f}% literature intensity {rel[4] * 100:.2f}%\n"
        return ret
    
    def print_rel(self, include_fwhm: bool = False) -> None:
        print(self.get_rel_str(include_fwhm=include_fwhm))


    def get_most_intense(self) -> Hashable:
        maxkey = 0
        maxitensity = 0
        for i in self.scheme:
            intensity = self.__igamma_after_efficiency(self.scheme[i])
            if intensity > maxitensity:
                maxitensity = intensity
                maxkey = i
        return maxkey
    
    def get_counts(self, key: Hashable) -> float:
        return self.scheme[key]['counts']

    def get_err(self, key: Hashable) -> float:
        return self.scheme[key]['err']
    
    def get_peak(self, key: Hashable) -> float:
        return self.scheme[key]['pk']
    def get_fwhm(self, key: Hashable) -> float:
        return self.scheme[key]['fwhm']
    
    def get_lit(self, key: Hashable) -> float:
        val = self.scheme[key]['lit']
        if isinstance(val, str):
            return float(val.replace("<", "").replace(">", "").replace("?", "0"))
        return self.scheme[key]['lit']

    def get_igammas_rel(self) -> List[Tuple[float, float, float]]:
        ret = []
        refline = self.get_most_intense()
        ret.append(self.get_igamma_relative(refline))
        for i in self.scheme:
            if i == refline:
                continue
            ret.append(self.get_igamma_relative(i))
        return ret

    def get_igamma_diffs(self) -> List[Tuple[float, float, float]]:
        ret = []
        for i in self.scheme:
            val = self.scheme[i]
            cts = self.__igamma_after_efficiency(val)
            ret.append((i, cts - float(val['lit'].replace("<", "").replace(">", "").replace("?", "0"))))
        return ret

    def get_igamma_lit(self) -> List[Tuple[float, float, float]]:
        ret = []
        for i in self.scheme:
            val = self.scheme[i]
            ret.append((i, float(val['lit'].replace("<", "").replace(">", "").replace("?", "0"))))
        return ret

    def __igamma_after_efficiency(self, val) -> float:
        #I_gamma = n_gamma / (efficiency_gamma * n_beta)
        if self.use_per_isotope_efficiency:
            try:
                return val["counts"] / (
                    gamma_efficiency_by_isotope(val["pk"], self.preferred_isotope_efficiency, addback=True, fractional=True) *
                    self.mother_decays
                )
            except Exception as e:
                print("Threw an exception, using fallback efficiency")
                print(e)
        return val["counts"] / (GammaEfficiencyAddBackFractional(val["pk"]) * self.mother_decays)

    def get_i_betas(self, scheme: List[Tuple[Hashable, List[Hashable], List[Hashable], float]]) -> List[Tuple[Hashable, float, float, float, float]]:
        # input validation is done per line in get_i_beta()
        ret = []
        for i in scheme:
            ret.append(self.get_i_beta(i))
        return ret
    
    def get_i_beta(self, scheme: Tuple[Hashable, List[Hashable], List[Hashable], float]) -> Tuple[Hashable, float, float, float, float]:
        # first verify that all keys exist
        if len(scheme) != 4:
                raise ValueError("All schemes elements must have length of 3")
        # key for this scheme
        if scheme[0] not in self.scheme:
            raise KeyError(f"All keys must exist in the provided scheme, scheme head {scheme[0]} not found")
        # key for each "feeding" transition
        for j in scheme[1]:
            if j not in self.scheme:
                raise KeyError(f"All keys must exist in the provided scheme, scheme feed {j} not found")
        # key for each transition that is fed by this transition
        for j in scheme[2]:
            if j not in self.scheme:
                print(type(j), j)
                raise KeyError(f"All keys must exist in the provided scheme, scheme draw {j} not found")
        # grab the key from the scheme, usually it's just the energy we started fitting the peak with.
        key  = scheme[0]
        head = self.get_peak(key)
        feed_total = 0.0
        # this tracks the feeding amount and the errors (amt, err) for each index
        feed_track = []
        # calculate the total amount of feeding by summing the intensity of all the gammas
        # we think might be daughter states of the state producing this line
        for j in scheme[1]:
            ig = self.get_igamma(j)
            feed_track.append((ig[2], ig[3]))
            feed_total += ig[2]
        # now we subtract the intensities of states that might be parent states 
        # of this state
        for j in scheme[2]:
            ig = self.get_igamma(j)
            feed_track.append((ig[2], ig[3]))
            feed_total -= ig[2]
        feed_total_err = add_errors_in_quadrature(*feed_track)
        return (key, head, feed_total, feed_total_err * feed_total, scheme[3])
        
    def __fhwm_phrase(self, key: Hashable) -> str:
        return f'fwhm={self.get_fwhm(key):>6.2f}'

    def print_i_betas(self, scheme: List[Tuple[Hashable, List[Hashable], List[Hashable], float]], include_fwhm: bool = False) -> None:
        t = self.get_i_betas(scheme)
        if t is None:
            return
        postfix = f"\tUsing efficiency curve from {self.preferred_isotope_efficiency}\n" if self.preferred_isotope_efficiency != self.isotope else ""
        ret =f"{self.isotope} I_beta for {self.mother_decays} mother decays for radius {self.radius}, for dT < {self.tmax}\n{postfix}"
        for i in t:
            fwhm_phrase = self.__fhwm_phrase(i[0]) if include_fwhm else""
            ret += f"\t{i[1]:>8.2f} keV {fwhm_phrase} measured {i[2] * 100:>6.3f}% pm {i[3] * 100:>6.3f}% literature intensity {i[4]:>6.3f}%\n"
        print(ret)