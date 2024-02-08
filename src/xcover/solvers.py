"""Solvers for exact cover problems"""

import numpy as np
from .dancing_cells import algorithm_c


def covers(options, primary=None, secondary=None, colored=False):
    """
    Exact cover with colors solver

    Parameters
    ----------
    options: a list of lists of items
    primary: a list of items that are primary (must be covered)
             if None, infer from the given options and secondary
    secondary: a list of items that are secondary (may be covered)
               if None, infer from the given options and primary
    colored: whether to do a colored solve (by default do not)
             for a colored solve, secondary items must be strings
             with colors in options separated by colons
             e.g. 'q:RED'

    Returns
    -------
    A generator object that yields solutions to the exact cover problem.
    Each yielded result is a list of integers specifying the indices of
    the chosen options.
    """
    options, options_ptr, colors, n_items, n_secondary = input_as_arrays(
        options,
        primary=primary,
        secondary=secondary,
        colored=colored,
    )
    yield from algorithm_c(options, options_ptr, colors, n_items, n_secondary)


def items(all_opts, primary=None, secondary=None, colored=False):
    """
    Infer the specific primary and secondary items and colors given user input.
    """
    if primary is None and secondary is None:
        # if items not specified assume all items in options are primary
        primary = set().union(all_opts)
        secondary = []
    elif primary is None:
        # if only secondary items specified, assume all others in options primary
        options_universe = set().union(all_opts)
        primary = options_universe.difference(secondary)
    elif secondary is None:
        # if only primary items specified, assume all others in options are secondary
        options_universe = set().union(all_opts)
        secondary = options_universe.difference(primary)
        if colored:
            secondary = {s.split(":")[0] for s in secondary}

    return primary, secondary


def color_indices(all_opts):
    """
    Label the colors of options by integer values.
    """
    col_names = {x.split(":")[-1] for x in all_opts if ":" in x}
    col_to_idx = {col: i + 1 for i, col in enumerate(col_names)}
    return np.array([col_to_idx[x.split(":")[-1]] if ":" in x else 0 for x in all_opts])


def input_as_arrays(options, primary=None, secondary=None, colored=False):
    """
    Convert the user-supplied input into array form for use in main algorithm
    """

    # A single list of all the options
    all_opts = [o for opt in options for o in opt]

    # Work out explicit primary and secondary item lists
    primary, secondary = items(all_opts, primary, secondary, colored)
    n_primary = len(primary)
    n_secondary = len(secondary)
    n_items = n_primary + n_secondary

    # Work out the color indices of each node
    if colored:
        colors = color_indices(all_opts)
    else:
        colors = np.zeros(len(all_opts), dtype=np.int64)

    # Form pointer array which gives start and end index of each option
    lens = np.array([len(opt) for opt in options])
    options_ptr = np.zeros(len(lens) + 1, dtype=np.int64)
    options_ptr[1:] = np.cumsum(lens)

    # dictionaries which enumerate each of the items
    primary_item_to_idx = {item: i for i, item in enumerate(primary)}
    secondary_item_to_idx = {item: i + n_primary for i, item in enumerate(secondary)}
    item_to_idx = {**primary_item_to_idx, **secondary_item_to_idx}

    # form final options as an array using the enumerated options
    if colored:
        enum_opts = [item_to_idx[x.split(":")[0]] for x in all_opts]
    else:
        enum_opts = [item_to_idx[x] for x in all_opts]
    options_as_array = np.hstack(enum_opts)

    return options_as_array, options_ptr, colors, n_items, n_secondary
