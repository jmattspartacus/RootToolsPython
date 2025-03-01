from .literature_values import *
from .beta_2n_halflife_analyzer import *
from .handyutils import *
from .analysis_tools import *
from .root_hist_decorator import *
from .root_hist_decorator_multiD import *
from .root_tree_fields import *
from .fit_result_wrapper import *
from .i_gamma_scheme import *
from .gamma_efficiency_by_isotope import *
from .serialization import *
from .parsing import *
from .root_macro_interfaces import *
from .trace_analyzer_fields import *
from .multi_thread_hist_fill import *
from .binning import *
from .par_iter import *
from .root_to_pyplot import *
from sys import argv, platform
# uses readline, which is not available for windows
if platform == "linux" or platform == "linux2" or platform == "darwin":
    from .prepinteractive import *
if not parsing.parse_boolean(argv, "silent", silent=True, output_message="", only_output_on_success=False):
    print("Contact James if you have issues with RootTools!")