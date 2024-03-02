"""Numba-accelerated implementation of Donald Knuth's dancing cells algorithm."""

import numpy as np
from numpy import uint64 as u
from numba import njit


@njit("(uint64[:], uint64[:], uint64[:], uint64, uint64)", cache=True)
def algorithm_c(options, options_ptr, colors, n_items, n_secondary_items):
    """
    Donald Knuth's dancing cells algorithm C.
    Exact covering with colors.

    Parameters
    ----------
    options: array of integers, giving all options
    options_ptr: array of integers, pointing where each option
                 begins and ends
    colors: the color of each item in each option
    n_items: the number of possible items
    n_secondary_items: the number of items that are secondary

    Returns
    -------
    a generator object that yields solutions to the exact cover problem
    """

    # C1: Initialisation of the matrix
    n_data = u(len(options))
    n_opts = u(len(options_ptr) - 1)
    n_primary_items = u(n_items - n_secondary_items)

    # options_j gives the option index of each node in the matrix
    options_j = np.empty(n_data, dtype=np.uint64)
    for j, i in enumerate(range(n_opts)):
        options_j[options_ptr[u(i)] : options_ptr[u(i + 1)]] = j

    # matrix_size gives the number of (active) options for each item
    matrix_size = np.zeros(n_items, dtype=np.uint64)
    for node in range(n_data):
        matrix_size[options[node]] += u(1)

    # matrix_start_ptr points to the start of the "column" in the matrix
    # for each item
    matrix_start_ptr = np.empty(n_items, dtype=np.uint64)
    matrix_start_ptr[0] = 0
    matrix_start_ptr[u(1) :] = np.cumsum(matrix_size)[:-1]

    # matrix_set and matrix_loc are sparse-set partners
    matrix_set = np.empty(n_data, dtype=np.uint64)
    matrix_loc = np.empty(n_data, dtype=np.uint64)
    counts = np.zeros(n_items, dtype=np.uint64)
    for node in range(n_data):
        i = options[node]
        val = matrix_start_ptr[i] + counts[i]
        matrix_loc[node] = val
        matrix_set[val] = node
        counts[i] += u(1)

    # the active items (items left to cover) use another sparse set
    # matrix_active_items and matrix_active_items_sparse are partners
    matrix_active_items = np.arange(n_items, dtype=np.uint64)
    matrix_active_items_sparse = np.arange(n_items, dtype=np.uint64)
    matrix_active_items_len = np.empty(u(1), dtype=np.uint64)
    matrix_active_items_len[0] = n_items
    matrix_old_active_items_len = np.empty(u(1), dtype=np.uint64)
    matrix_active_items_len[0] = n_items

    def active_insert(item, index):
        """Insert an item into position index in the active_items sparse set"""
        matrix_active_items[index] = item
        matrix_active_items_sparse[item] = index

    def deactivate_item(item):
        """C3: make an item inactive: remove from active_items list"""
        end_index = matrix_active_items_len[0] - u(1)
        end_item = matrix_active_items[end_index]
        index = matrix_active_items_sparse[item]
        active_insert(end_item, index)
        active_insert(item, end_index)
        matrix_active_items_len[0] -= u(1)

    def active_options(item):
        """the active options of a given item"""
        return matrix_set[
            matrix_start_ptr[item] : (matrix_start_ptr[item] + matrix_size[item])
        ]

    def remove_node(node):
        """remove a node from the matrix"""
        item = options[node]
        loc = matrix_loc[node]

        end_loc = matrix_start_ptr[item] + matrix_size[item] - u(1)
        end_node = matrix_set[end_loc]

        matrix_set[loc] = end_node
        matrix_set[end_loc] = node
        matrix_loc[end_node] = loc
        matrix_loc[node] = end_loc
        matrix_size[item] -= u(1)

    def hide(item, col, initial):
        """given an item and a coloring col, remove the relevant nodes"""
        # initial refers to whether we're hiding directly after a choose operation
        for node in active_options(item):
            if col == 0 or colors[node] != col:
                j = options_j[node]
                for k in range(options_ptr[j], options_ptr[j + u(1)]):
                    iprime = options[k]
                    if (
                        iprime != item
                        and matrix_active_items_sparse[iprime]
                        < matrix_old_active_items_len[0]
                    ):
                        if (
                            not initial
                            and matrix_size[iprime] == u(1)
                            and matrix_active_items_sparse[iprime]
                            < matrix_active_items_len[0]
                            and iprime < n_primary_items
                        ):
                            return False  # end if about to delete last
                        remove_node(k)
        return True

    def cover(node, item):
        """C6 and C7: main cover routine"""
        option = options_j[node]
        ptr_range = range(options_ptr[option], options_ptr[option + u(1)])
        matrix_old_active_items_len[0] = matrix_active_items_len[0]

        # C6: deactivate other items of option
        for ptr in ptr_range:
            itm = options[ptr]
            if (
                itm != item
                and matrix_active_items_sparse[itm] < matrix_active_items_len[0]
            ):
                deactivate_item(itm)

        # C7: hiding nodes
        for ptr in ptr_range:
            itm = options[ptr]
            col_hide = colors[ptr]
            if itm != item:
                if (
                    itm < n_primary_items
                    or matrix_active_items_sparse[itm] < matrix_old_active_items_len[0]
                ):
                    status = hide(itm, col_hide, False)
                    if status is False:
                        return n_opts
        return option

    def save_state():
        """C5: Save the current state (sizes) for backtracking"""
        return (matrix_size[:].copy(), matrix_active_items_len[0])

    def undo(state):
        """Restore a previous state of the matrix"""
        matrix_size[:], matrix_active_items_len[0] = state

    def choose():
        """C2: Choose the next item to cover. Return n_data if solved already"""
        # Using the minimum remaining value (MRV) heuristic here
        active_items = matrix_active_items[0 : matrix_active_items_len[0]]
        chosen_item = n_items
        chosen_length = n_data
        for item in active_items:
            if item < n_primary_items:
                length = matrix_size[item]
                if length < chosen_length:
                    chosen_item = item
                    chosen_length = length
                    if length == u(1):
                        return chosen_item
        return chosen_item

    # Main loop. A depth-first search, written here using a stack
    # rather than recursive as numba doesn't support yield from
    solution = []  # current solution
    node_stack = [[n_data]]  # current list of nodes to explore (n_data is root)
    item_stack = [n_items]  # current list of covered items
    initial_state = save_state()  # saved state for backtracking
    state_stack = [initial_state]  # stack of states

    need_to_undo = False
    while node_stack:
        if len(node_stack[-1]) == 0:
            # backtracking, C10
            node_stack.pop()
            state_stack.pop()
            item_stack.pop()
            need_to_undo = True
            if solution:
                solution.pop()
        else:
            if need_to_undo:
                undo(state_stack[-1])  # return to previous state, C11
                need_to_undo = False

            node = u(node_stack[-1].pop())  # C6
            if node < n_data:
                option = cover(node, item_stack[-1])  # C6 and C7
            else:
                option = n_opts + u(1)
            if option == n_opts:  # case where cover failed
                need_to_undo = True
            else:
                if option < n_opts:
                    solution.append(option)  # include option in partial solution
                item = choose()  # C2
                if item == n_items:
                    yield list(solution)  # found a solution!
                    solution.pop()
                    need_to_undo = True
                else:
                    item_stack.append(item)
                    deactivate_item(item)  # C3
                    matrix_old_active_items_len[0] = matrix_active_items_len[0]
                    hide(item, 0, True)  # C4
                    state_stack.append(save_state())  # C5
                    node_stack.append(list(active_options(item)))
