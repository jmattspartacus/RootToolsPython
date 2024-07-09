# CommonToolsPython

This is a collection of tools for data analysis, some of which are specific to E19044, but many of them are general use tools. Some are simple wrappers around ROOT classes to simplify their use, others are classes for useful encapsulation of data that makes analysis steps faster.

## beta_2n_halflife_analyzer.py

Serves to allow rapid determination of beta decay halflives, and beta normalizations. 

## decay_scheme/py

Allows building decay scheme visualizations for various decay modes. Current functionality is limited to beta decay schemes with branching ratios.

## fit_result_wrapper.py

Contains a number of classes useful for quickly fitting and presenting fit results

### FitResultSummary1D

Allows grouping salient information about a particular fit result, intended mostly for Gaussian type fits, but is not limited.

### FitResultWrapper

Provides an interface for summarizing and presenting a fit result. Currently only 1D fits are supported. Serves as a wrapper class for ROOT.TFitResultPointer, with an acessible member containing the original fit result.

### MultiFitResult

Provides interface and retention for a set of fit results, and allows getting salient information, presentation to user and access to underlying TFitResultPointers, peak counts, error.


## gamma_efficiency_by_isotope.py

Provides a lazy interface to a lookup table for getting simulated efficiencies for each isotope, based on their average implantation position. The calculations to collate the efficiency for average implant positions are split between ImplantationPosition and AddBackEfficiency directories.

## handyutils.py

Is collection of utility functions that do not fit cleanly into another category toolswise. These vary from timing code execution, unit conversions, converting tables/dictionaries to latex tables and more.

## i_gamma_scheme.py

Allows construction of absolute/relative gamma intensity schemes using a set of lines and number of counts, with literature value it allows comparison of them with expected strengths.

## literature_values.py

Provides a lazily initialized lookup table for pulling nuclear properties from NUDAT or other provided sources. Not guaranteed to always be up to date with current literature.

## parsing.py

Provides some simple argument parsing functionality, currently handling numeric types and string arguments, with support for delimited lists of arguments.

## prepinteractive.py

Provides the ability to keep a log of an interactive session for analysis for a particular isotope using datasets with merger/addback already complete. Records all commands in a log at session exit.

## root_hist_decorator.py

Provides a wrapper class around ROOT's histogram classes, currently supporting only 1D with included support for fitting multiple peaks, integration, fast drawing, zoom, retained axes bounds without refilling/redrawing histograms, customizable automatic axis bound determination, and background subtraction, using both constant and histogram defined backgorunds.

## root_tree_fields.py

Provides information about fields in ROOT trees and how they relate to the detector setup.

## serialization.py

Provides utility functions to simplify loading and saving python objects to the JSON format. Allows discarding objects that do not have a defined JSON serialization schemes. Also allows defining custom serialization schemes for types to allow more dynamic serialization schemes.
