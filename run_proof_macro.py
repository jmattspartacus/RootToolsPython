import ROOT
import re
from glob import glob
import sys


if __name__ != "__main__":
    from RootToolsPython import *
else:
    from parsing import *


def build_and_run_macro(
    InputDir: str,
    OutputDir: str,
    SelectorPath: str,
    macroName: str,
    treeName: str,
    workers: int,
    dryrun: bool,
    print_output: bool = False
):
    files = glob(InputDir + "*.root")
    if workers > 1:
        workerLine = f'\tTProof *proof = TProof::Open("workers={workers}");\n\tproof->SetParameter("PROOF_UseMergers", 1);\n'
    else: 
        workerLine = ""
    with open(f"{macroName}ProofMacro.C", "w+") as fp:
        #fp.write(f"void {macroName}ProofMacro()\n")
        fp.write("{\n")
        fp.write("\tgROOT->SetBatch(1);\n")
        fp.write(workerLine)
        
        for inputFile in files:
            outpath = OutputDir + inputFile.split("/")[-1]
            fp.write("\t{\n")
            fp.write(f'\t\tTChain *tree = new TChain("{treeName}");\n')
            fp.write(f'\t\ttree->Add("{inputFile}");\n')
            if workers > 1:
                fp.write(f"\t\ttree->SetProof();\n")
            fp.write(f'\t\ttree->Process("{SelectorPath}+", "{outpath}");\n')
            fp.write("\t}\n")
        fp.write("    gApplication->Terminate();")
        fp.write("}")
    # compile the macro
    cpp_code = ""
    with open(f"{macroName}ProofMacro.C", "r") as fp:
        cpp_code = "".join(fp.readlines())
    try:
        if dryrun:
            if print_output:
                print("Dry run, no macro execution")
            return
        ROOT.gInterpreter.ProcessLine(cpp_code)
        getattr(ROOT, macroName)()
    except Exception as e:
        print("Threw an exception while trying to compile or run the macro!")
        print(e)

if __name__ == "__main__":
    inputDir = parse_string_arg(sys.argv, "input", "Input directory: $argval")
    outputDir = parse_string_arg(sys.argv, "output", "Output Directory: $argval")
    selectorPath = parse_string_arg(sys.argv, "selector", "Selector set to: $argval")
    macroName = parse_string_arg(sys.argv, "macroName", "Macro name set to: $argval")
    treeName = parse_string_arg(sys.argv, "treename", "TreeName in file: $argval" , "OutputTree")
    workers = parse_int_arg(sys.argv, "workers", "Workers set to: $argval", 8, kill_on_fail=False, min_value=1, max_value=32)
    dry_run = parse_boolean(sys.argv, "dry")
    build_and_run_macro(inputDir, outputDir, selectorPath, macroName, treeName, workers, dry_run, True)