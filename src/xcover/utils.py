"""Some useful additional routines"""
import numpy as np
from .solvers import items


def verify_exact_cover(solution, options, primary=None, secondary=None, colored=False):
    """
    Throws an exception if a solution does not represent an exact cover.
    """
    # A single list of all the options
    all_opts = [o for opt in options for o in opt]

    # Work out explicit primary and secondary item lists
    primary, secondary = items(all_opts, primary, secondary, colored)

    # Check the primary items for exact cover
    primary_options = [o for s in solution for o in options[s] if o in primary]
    cover = set().union(*[options[s] for s in solution])
    primary_cover = set(primary).intersection(cover)

    is_exact = len(primary_options) == len(primary_cover)
    is_cover = primary_cover == set(primary)
    assert is_exact
    assert is_cover

    # Check secondary items for covering at most once
    if colored:
        secondary_options = [
            o for s in solution for o in options[s] if o.split(":")[0] in secondary
        ]
    else:
        secondary_options = [o for s in solution for o in options[s] if o in secondary]

    # Count occurances of each secondary item
    counts = {s: 0 for s in secondary}
    colors = {s: 0 for s in secondary}
    for item in secondary_options:
        if colored:
            itm = item.split(":")[0]
            if len(item.split(":")) > 1:
                col = item.split(":")[1]
            else:
                col = 0
        else:
            itm, col = item, 0
        if col != 0:
            if colors[itm] == 0:
                colors[itm] = col
                counts[itm] += 1
            elif colors[itm] != col:
                assert False  # can't color twice
            else:
                continue  # fine to have another item of same color
        else:
            counts[itm] += 1
    for _, count in counts.items():
        assert count <= 1  # each only covered once


def bool_array_to_options(bool_array):
    """Convert a boolean array into a options list of lists"""
    return [list(np.nonzero(bool_array[i, :])[0]) for i in range(bool_array.shape[0])]
