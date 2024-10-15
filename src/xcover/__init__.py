"""
xcover 
======

An exact cover with colors package.

The main function provided by this packages is "covers" which returns
a generator yielding solutions to exact cover problems.

There are currently four solvers:
    covers -- exact cover with colors
    cover_zdd -- exact cover with colors, but yields nodes of a ZDD not solutions
    covers_bool -- exact cover for problem specified as an array of bool
    covers_bool_zdd -- as above, but yields nodes of a ZDD not solutions
    
The underlying numba-accelerated algorithms behind these solvers can be called directly using either
    algorithm_c -- exact cover with colors
    algorithm_z -- exact cover with colors, but yields nodes of a ZDD
but these require the problems to be first cast in sparse matrix form.
"""

__version__ = "0.2.3"
__author__ = "John F. Rudge"

from .solvers import covers, covers_bool, covers_zdd, covers_bool_zdd
from .dancing_cells import algorithm_c
from .dancing_cells_zdd import algorithm_z
