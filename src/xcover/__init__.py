"""
xcover 
======

An exact cover with colors package.

The main function provided by this packages is "covers" which returns
a generator yielding solutions to exact cover problems.

"""

__version__ = "0.1.5"
__author__ = "John F. Rudge"

from .solvers import covers, covers_bool
