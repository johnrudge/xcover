# xcover

A python package for solving exact cover with colours problems.

## Installation

This package can be installed using pip:

```
pip install xcover
```
The only dependency is [numba](https://numba.pydata.org/).

## Usage

A simple example of an [exact cover](https://en.wikipedia.org/wiki/Exact_cover) problem is the following. Given the set of 6 options
0:={1, 4, 7}; 1:={1, 4}; 2:={4, 5, 7}; 3:={3, 5, 6}; 4:={2, 3, 6, 7}; 5:={2, 7}, each of which are subsets of a set of seven items (the numbers 1 to 7), find a subset of the options which contains each item once and only once. Such a problem can be solved using the package as

```
from xcover import covers

options = [[1, 4, 7], [1, 4], [4, 5, 7], [3, 5, 6], [2, 3, 6, 7], [2, 7]]
print(list(covers(options)))
```

```
[[1, 3, 5]]
```
which outputs a list of possible exact covers. In this case there is a single solution: cover by the options 1:={1, 4}, 3:={3, 5, 6}, and 5:={2, 7}.

The `covers` function returns a [python generator](https://wiki.python.org/moin/Generators), an object that can be used in a `for` loop. This is useful in the case of multiple solutions if you want to do something immediately with each solution as it is calculated. If you just want to find the next solution you can use the `next` function on the generator.

### Exact cover with colours

The package supports two extensions to the standard exact cover problem. The first extension is the addition of secondary items. These are items that do not need to be covered, but may be covered once if required. The second extension is the ability to colour the secondary items in each option. In the coloured case the secondary item may be covered multiple times, so long as it is coloured the same way in each cover. A simple example of an exact cover with colours problem is the following

```
primary = ["p", "q", "r"]
secondary = ["x", "y"]
options = [
    ["p", "q", "x", "y:A"],
    ["p", "r", "x:A", "y"],
    ["p", "x:B"],
    ["q", "x:A"],
    ["r", "y:B"],
]

print(list(covers(options, primary=primary, secondary=secondary, colored=True)))
```

```
[[3, 1]]
```
In this problem there are three primary items `p`, `q`, and `r` that must be covered, and two secondary items `x` and `y` that may be covered. The exact cover is given by the two sets {`p`, `r`, `x:A`, `y`} and {`q`, `x:A`}. In this cover the item `x` is covered twice, but that is acceptable as both instances are colored `A`. The xcover package denotes the colouring of items by a colon followed by a label.

### Boolean arrays

An alternative way of specifying an exact cover problem is in terms of a [boolean incidence matrix](https://en.wikipedia.org/wiki/Exact_cover#Incidence_matrix). The package provides a `covers_bool` function for directly solving such problems.
```
import numpy as np
from xcover import covers_bool

matrix = np.array([
    [1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 1],
    [0, 0, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 1]
    ], dtype=bool)
print(next(covers_bool(matrix)))
```

```
[1, 3, 5]
```

## Dancing cells

The algorithm used for finding the exact covers is [Donald Knuth's](https://www-cs-faculty.stanford.edu/~knuth/) algorithm C which uses "dancing cells". A full description of the algorithm can be found in his [draft manuscript](https://www-cs-faculty.stanford.edu/~knuth/fasc7a.ps.gz). The main algorithm is in `xcover.dancing_cells.algorithm_c` and can be called directly if desired.

## Numba

To accelerate the performance of the solver this package uses [numba](https://numba.pydata.org/) to perform Just In Time (JIT) compilation of the main algorithm. This means the first call to the solver may be slow (a few seconds) while numba compiles the function. However, later calls will be fast, as numba uses a cache to avoid repeated compilation. JIT compilation can be disabled by explicitly configuring numba before importing the `xcover` package.

```
from numba import config
config.DISABLE_JIT = True
```

## Applications

Many recreational mathematical puzzles can be naturally cast as exact cover problems. Examples include pentomino tiling, sudoku, and the n-queens problem. Donald Knuth's [Art of Computing volume 4B](https://www-cs-faculty.stanford.edu/~knuth/taocp.html) has an extensive discussion of many such problems. Exact cover problems are [NP-complete](https://en.wikipedia.org/wiki/NP-completeness) which means solve times can get very long very quickly as problems get larger. Be warned!

## License

This package is licenced under the GNU Lesser General Public License v3.0.
