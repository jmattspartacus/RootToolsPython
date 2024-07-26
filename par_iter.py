from typing import Iterable, List, Callable
import multiprocessing

def par_iter_map(input_vals: Iterable, func: Callable, workers: int) -> List:
  """Maps a task across a specified number of cores on your machine, running

  Args:
      input_vals (Iterable): Iterable of arguments compatible with your function
      func (function): function accepting elements of input_vals as an argument
      workers (int): number of workers that will be spun up to do work

  Returns:
      List: output from the functions
  """
  if workers < 1:
    workers = 1
  # run this in parallel
  with multiprocessing.Pool(workers) as p:
    ret = p.map(func, input_vals)
  return ret


if __name__ == "__main__":
  test_args = [i for i in range(100000000)]
  def square(i):
    for i in range(i):
      t = i*i
    return t
  import time
  nworkers = multiprocessing.cpu_count()
  ptime_start = time.time()
  out = par_iter_map(test_args, square, nworkers)
  ptime_end = time.time()
  
  stime_start = time.time()
  out = [square(i) for i in test_args]
  stime_end = time.time()
  print(f"Par time {ptime_end - ptime_start}")
  print(f"Ser time {stime_end - stime_start}")