import json
import numpy
from . import util





def gamma_efficiency_by_isotope(energy, isotope, fractional=False, addback=True, front=False, custom_config_name=False, quenching_factor=0.4):
    # keep this local
    def GammaEfficiencyFitFunc(E, p0, p1, p2, p3, p4, p5, p6, p7, p8, p9) -> float:
        par = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9]
        a = numpy.float_power(E, par[0])
        ret = numpy.zeros(numpy.shape(a))
        #print(ret, a)
        logE = numpy.log(E)
        for i in range(1, 9):
            #print(math.pow(logE, i), ",", ret)
            ret += par[i] * numpy.float_power(logE, i - 1)
            #print(math.pow(logE, i), ",", ret)
        return ret * a
    
    # Treat lut like a lazy static
    if getattr(gamma_efficiency_by_isotope, "lut", None) is None:
        basepath = util.plat_path_join(util.plat_path_spl(__file__)[:-1])+util.plat_path_sep()
        ff = util.platpath("data/e19044/efficiency_fits_by_isotope.json")
        with open(util.platpath(f"{basepath}{ff}"), "r") as fp:
            tsrt = "".join(fp.readlines())
        gamma_efficiency_by_isotope.lut = json.loads(tsrt)
    
    if isotope in gamma_efficiency_by_isotope.lut:
        if custom_config_name:
            val = gamma_efficiency_by_isotope.lut[isotope][custom_config_name]
        elif front:
            val = gamma_efficiency_by_isotope.lut[isotope]["front"]
        else:
            val = gamma_efficiency_by_isotope.lut[isotope]["inside"] 
        pars = val[f"fit_par_{'addback' if addback else 'singles'}"]
        return GammaEfficiencyFitFunc(energy, * pars) * (1/100 if fractional else 1) * quenching_factor
    else:
        msg = f"Isotope {isotope} not in list of isotopes! Check that it exists and has been simulated!"
        raise KeyError(msg)
    
if __name__ == "__main__":
    from matplotlib import pyplot
    from parsing import *

    def graph_efficiencies(inval):
        e = inval.split()[1:]
        isotope = e[0]
        useaddback = "addback" in e
        high = parse_int_arg(e, "high", "", 5000, kill_on_fail=False, min_value=100, max_value=5000) 
        low  = parse_int_arg(e, "low",  "", 0,    kill_on_fail=False, min_value=0,   max_value=high)
        step  = parse_int_arg(e, "step",  "", 100,    kill_on_fail=False, min_value=0,   max_value=high - low)
        energies = [100 + i for i in range(low, high, step)]
        try:
            eff =[gamma_efficiency_by_isotope(k, isotope, addback=useaddback) for k in energies]
        except Exception as e:
            raise e

        pyplot.plot(energies, eff)
        pyplot.xlabel("Energy (keV)")
        pyplot.ylabel("Uncorrected Efficiency (%)")
        pyplot.xlim((low-10, high + 10))
        pyplot.show()
    inval = ''
    quitvals = ['end', 'stop', 'exit', "q", "quit"]

    def efficiency_calc(inval):
        e = inval.split()[1:]
        if len(e) < 2:
            print("Usage: eff energy1,energy2 isotopes <options>")
            return
        energies = e[0].split(",")
        isotope = e[1]
        useaddback = "addback" in e
        fractional = "frac" in e
        for i in energies:
            print(f"Efficiency for {i} keV is {gamma_efficiency_by_isotope(float(i), isotope, fractional=fractional, addback=useaddback):.2f}% for {isotope} {'with addback' if useaddback else 'without addback'}")
    while True:
        inval = input(">>")
        commands = {
            "graph":graph_efficiencies,
            "eff":efficiency_calc
        }
        com = inval.split()[0]
        if com in commands:
            try: 
                commands[com](inval)
            except Exception as e:
                print("Command threw an exception")
                print(e)
        elif inval.lower() in quitvals:
            break
    
        else:
            print("Not a command")
