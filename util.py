from sys import platform
from typing import List


def platpath(p: str) -> str:
  """Corrects a path to the correct form for the
  current platform OS, does not include any disk 
  information, etc, this needs to be provided by 
  the user, or in the code itself, preferably in a
  platform agnostic way
  Args:
      p (str): path you want to correct

  Returns:
      str: correct path in the system
  """
  if platform == "win32":
    return p.replace("/","\\")
  else:
    return p.replace("\\", "/")
  
def plat_path_spl(p: str) -> List[str]:
  """Splits a platform path into it's parts

  Args:
      p (str): path to be split

  Returns:
      List[str]: list with the parts of the path
  """
  if platform == "win32":
    return p.split("\\")
  else:
    return p.split("/")
  
def plat_path_join(p: List[str]) -> str:
  """Joins a path using the correct path delimeter 
  for the platform

  Args:
      p (List[str]): parts of the path to join

  Returns:
      str: joined path
  """
  if platform == "win32":
    return "\\".join(p)
  else:
    return "/".join(p)

def plat_path_sep() -> str:
  """Returns the correct path delimiter for 
  the current platform

  Returns:
      str: the correct path delimiter for the platform
  """
  if platform == "win32":
    return "\\"
  else:
    return "/"