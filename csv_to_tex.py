from typing import List


def convert_to_formatted_type(ival: str, fstr: str):
  try:
    type_val = str
    t_fstr = "{}"
    if "float" in fstr:
      t_fstr = fstr.replace("float", "")
      type_val = float
    elif "int" in fstr:
      t_fstr = fstr.replace("int", "")
      type_val = int
    rval = type_val(ival)
    return t_fstr.format(rval)
  # do not raise an exception! just return the value
  except (ValueError, TypeError):
    return ival


def csv_to_rows(file: str, column_formats: List[str], delimeter: str = ",") -> List[List[str]]:
  header = ""
  rows = []
  with open(file, "r") as fp:
    header = fp.readline().replace("\n","").split(delimeter)
    for line in fp.readlines():
      spl = line.replace('\n', "").split(", ")
      for c in range(len(spl)):
        if c < len(column_formats):
          spl[c] = convert_to_formatted_type(spl[c], column_formats[c])
      rows.append(spl)
  return header, rows

def table_to_tex(table, columnar = True):
  ret = []
  if columnar:
    ret = [""] * len(table[0])
    for i in range(len(table[0])):
      for j in range(len(table)):
        # prevent commenting out part of table
        phrase = table[j][i].replace("%", "\%")
        if j < len(table) - 1:
          ret[i] += f"{phrase}&"
        else:
          ret[i] += f"{phrase}\\\\"
  else:
    maxlen = 0
    for i in table:
      maxlen = maxlen if len(i) < maxlen else len(i)
    for i in table:
      tline = ""
      for j in range(maxlen):
        # prevent commenting out part of table
        phrase = i[j].replace("%", "\%")
        if j < len(i) and j < maxlen - 1:
          tline += f"{phrase}&"
        elif j < len(i):
          tline += f"{phrase}\\\\"
        elif j < maxlen - 1:
          tline += "&"
        else:
          tline += "\\\\"
      ret.append(tline)
  return ret

if __name__ == "__main__":
  from sys import argv
  import argparse
  from os import path
  parser = argparse.ArgumentParser(
    prog="csv_to_tex",
    description="Converts a csv file to a latex table",
  )
  OFILE_DEFAULT = "NARFDNSARG"
  
  parser.add_argument("-i", "--input-file",  required=True, dest="ifile", help="The input file to be processed")
  parser.add_argument("-o", "--output-file", required=False, default=OFILE_DEFAULT, dest="ofile",help="The file that the output tex will be put in, pass STDOUT to print to the terminal")
  parser.add_argument("-x", "--override",    required=False, default=False, dest="override", help="If true, this will overwrite any preexisting output by the same name")
  parser.add_argument("-d", "--delimiter",   required=False, dest="delim", help="The delimiter used to split the rows of the file", default=", ")
  parser.add_argument("-f", "--format",      required=True, dest="fstr", help="Space delimited format string used to format the columns of the file")

  args = argv[1:]
  if len(args) < 2:
    parser.print_usage()
    exit()
  p = parser.parse_args(args)
  ifile           = p.ifile
  ofile           = p.ofile
  ofile_overwrite = p.override
  fstrs           = p.fstr
  delim           = p.delim
  if len(delim) == 0:
    print("Delimiter cannot have zero length!")
    exit()

  if not path.exists(ifile):
    print(f"Input file {ifile} does not exist!")
    exit()
  
  if ofile == OFILE_DEFAULT:
    ofile = path.splitext(ifile)[0]+".tex"



  fstrs = fstrs.split(" ")
  
  header, rows = csv_to_rows(ifile, fstrs, delim)
  table = [header]
  table.extend(rows)
  outval = table_to_tex(table, False)
  
  if ofile == "STDOUT":
    for i in outval:
      print(i)
  elif path.exists(ofile) and not ofile_overwrite:
    print(f"Output file '{ofile}' already exists, if you meant to do this, please pass '-x' or '--override'")
    exit()
  else:
    with open(ofile, "w+") as fp:
      for i in outval:
        fp.write(i)
        fp.write("\n")