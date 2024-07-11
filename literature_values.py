import csv
import sys
import re
from . import handyutils
from typing import Tuple
from . import util

data_dir=__file__.replace(__file__.split(util.plat_path_sep())[-1], "data")

class Moller:
    def __init__(self, parent) -> None:
        self.data = {}
        self.Load()
        self.IsotopeStrToZNTuple = parent.IsotopeStrToZNTuple

    def Load(self) -> None:
        moller_unique_headers = set()
        
        from glob import glob
        import csv
        files = glob(util.platpath(f"{data_dir}/moller2019/*.csv"))
        for i in files:
            with open(i, "r") as fp:
                reader = csv.reader(fp, delimiter=",")
                header = next(reader)
                ignore = set()
                while header[0][0] == "#":
                    header= next(reader)
                for idx in range(len(header)):
                    if header[idx] in moller_unique_headers:
                        ignore.add(idx)
                    else:
                        moller_unique_headers.add(header[idx])
                zidx = ""
                aidx = ""
                for k in range(len(header)):
                    if header[k] == "A":
                        aidx = int(k)
                    if header[k] == "Z":
                        zidx = int(k)
                for row in reader:
                    if row[0][0] == "#":
                        continue
                    key = (int(row[zidx]), int(row[aidx]) - int(row[zidx]))
                    if key not in self.data:
                        self.data[key] = {}
                    for j in range(len(row)):
                        if j not in ignore:
                            self.data[key][header[j]] = row[j]

    def GetPNn(self, isotope: str, num: int) -> float:
        t_isotope = self.IsotopeStrToZNTuple(isotope)
        if t_isotope in self.data:
            key = "P{}n".format(num)
            if key in self.data[t_isotope]:
                return float(self.data[t_isotope][key])
            else:
                raise ValueError("Isotope exist but {} is not specified for it".format(key))
        else:
            raise ValueError("Isotope {} with key {} not found!".format(isotope, t_isotope))
    

class Nudat:
    def __init__(self, parent) -> None:
        self.data = {}
        self.IsotopeStrToZNTuple = parent.IsotopeStrToZNTuple
        with open(util.platpath(f"{data_dir}/nudat/nuclei_halflives.csv"), "r") as fp:
            reader = csv.reader(fp, delimiter=",")
            next(reader)
            for row in reader:
                try:
                    halflife    = float('inf') if row[2] == 'STABLE' else float(row[2])
                    uncertainty = 0 if row[2] == 'STABLE' or row[3] == '' else float(row[3])
                    if (int(row[1]),int(row[0])) not in self.data:
                        self.data[(int(row[1]),int(row[0]))] = {}
                    self.data[(int(row[1]),int(row[0]))]['halflife'] = halflife
                    self.data[(int(row[1]),int(row[0]))]['uncertainty'] = uncertainty
                except:
                    print(row)
                    sys.exit()
    
    def GetDecayConstant(self, isotope: str) -> float:
        return handyutils.halflife_to_decay_constant(self.GetHalflife(isotope),input_units=1.0)
         

    def GetHalflife(self, isotope: str) -> float:
        key = self.IsotopeStrToZNTuple(isotope)
        if not key in self.data:
            err = "Isotope {} with key {} does not exist in the dataset!".format(isotope, key)
            raise ValueError(err)
        if 'halflife' in self.data[key]:
            return self.data[key]['halflife']
        else:
            err = "Isotope {} exists, but does not have known halflife".format(isotope)
            raise ValueError(err)
    
    def GetUncertainty(self, isotope: str) -> float:
        key = self.IsotopeStrToZNTuple(isotope)
        if not key in self.data:
            err = "Isotope {} with key {} does not exist in the dataset!".format(isotope, key)
            raise ValueError(err)
        if 'halflife' in self.data[key]:
            return self.data[key]['uncertainty']
        else:
            err = "Isotope {} exists, but does not have known halflife".format(isotope)
            raise ValueError(err)

class LiteratureValues:
    def __init__(self) -> None:
        self.elements = {}
        self.nudat = Nudat(self)
        self.moller = Moller(self)
        with open(f"{data_dir}/nucleiSymbols.csv") as fp:
            reader = csv.reader(fp, delimiter=",")
            next(reader)
            for row in reader:
                self.elements[row[1].replace(" ", "")] = int(row[0])
        
    

    def IsotopeStrToZNTuple(self, isotope: str) -> Tuple[int, int]:
        element = re.search("([a-zA-Z]+)", isotope)
        mass_number_str = re.search("(\d+)", isotope)
        if mass_number_str is not None and element is not None:
            mass_number = int(mass_number_str.group(1))
            if element.group(1) in self.elements:
                return (self.elements[element.group(1)], mass_number - self.elements[element.group(1)])
                    
            raise ValueError("{} is not an element".format(element.group(1)))
        raise ValueError("Failed to find valid match in '{}'".format(isotope))

    def ZNTupleToIsotopeStr(self, zn: Tuple[int, int]) -> str:
        ret = "{}{}"
        for i in self.elements.keys():
            if self.elements[i] == zn[0]:
                return ret.format(i, zn[0]+zn[1])
        raise ValueError("The ZN tuple provided does not match an isotope!")
    
    def IsotopeStrToBdaughter(self, isotope: str) -> str:
        zn = list(self.IsotopeStrToZNTuple(isotope))
        zn[0] += 1
        zn[1] -= 1
        return self.ZNTupleToIsotopeStr(zn)

    def IsotopeStrToBnDaughter(self, isotope: str) -> str:
        zn = list(self.IsotopeStrToZNTuple(isotope))
        zn[0] += 1
        zn[1] -= 2
        return self.ZNTupleToIsotopeStr(zn)
    
    def IsotopeStrToB2nDaughter(self, isotope: str) -> str:
        zn = list(self.IsotopeStrToZNTuple(isotope))
        zn[0] += 1
        zn[1] -= 3
        return self.ZNTupleToIsotopeStr(zn)

if __name__ == "__main__":
    testobj = LiteratureValues()
    #print(testobj.elements)
    #print(testobj.data[(12, 24)])
    print(testobj.nudat.GetDecayConstant("Mg36"))
    print(testobj.nudat.GetHalflife("Mg36"))
    print(testobj.nudat.GetUncertainty("Mg36"))

    
    print(testobj.IsotopeStrToZNTuple("Mg36"))
    print(testobj.ZNTupleToIsotopeStr((12, 24)))