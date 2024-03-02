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
    return np.array(
        [col_to_idx[x.split(":")[-1]] if ":" in x else 0 for x in all_opts],
        dtype=np.uint64,
    )


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
        colors = np.zeros(len(all_opts), dtype=np.uint64)

    # Form pointer array which gives start and end index of each option
    lens = np.array([len(opt) for opt in options])
    options_ptr = np.zeros(len(lens) + 1, dtype=np.uint64)
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
    options_as_array = np.array(np.hstack(enum_opts), dtype=np.uint64)

    return options_as_array, options_ptr, colors, n_items, n_secondary


def covers_bool(matrix):
    """
    Exact cover solver for a boolean matrix

    Parameters
    ----------
    matrix: a numpy array whose nonzero entries indicate nodes.
            Columns are the items, rows are the options.

    Returns
    -------
    A generator object that yields solutions to the exact cover problem.
    Each yielded result is a list of integers specifying the row indices of
    the chosen options.
    """
    n_options = matrix.shape[0]
    n_items = matrix.shape[1]
    options = np.array(np.nonzero(matrix)[1], dtype=np.uint64)
    options_ptr = np.empty(matrix.shape[0] + 1, dtype=np.uint64)
    options_ptr[0] = 0
    options_ptr[1:] = np.cumsum(np.count_nonzero(matrix, axis=1))
    n_data = len(options)
    n_secondary = 0
    colors = np.zeros(n_data, dtype=np.uint64)
    yield from algorithm_c(options, options_ptr, colors, n_items, n_secondary)
