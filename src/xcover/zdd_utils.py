"""Some additional routines for manipulating zdds"""


def to_zdd_algorithms(zdd):
    """
    Conversion to the ZDD format used by
    https://github.com/Thilo-J/zdd_algorithms
    """

    from zdd_algorithms import empty, base, get_node

    nodes = [empty()]
    done_something = False
    for z in zdd:
        if not done_something:
            nodes.append(base())
            done_something = True
        i, n, lo, hi = z[0], z[1], z[2], z[3]
        nodes.append(get_node(n, nodes[lo], nodes[hi]))
    return nodes[-1]


def to_setset(zdd, n_options):
    """
    Conversion to the ZDD format used by
    https://github.com/takemaru/graphillion
    """

    from graphillion import setset

    setset.set_universe([i for i in range(n_options)])

    zdd_string = ""
    for z in zdd:
        i, n, lo, hi = z[0], 1 + z[1], z[2], z[3]
        lo_str = "B" if lo == 0 else lo
        hi_str = "T" if hi == 1 else hi
        zdd_string += f"{i} {n} {lo_str} {hi_str}\n"
    zdd_string += ".\n"
    return setset(setset.loads(zdd_string))


def count_setset_nodes(ss):
    """
    Count the number of ZDD nodes in a graphillion setset object.
    Somewhat cumbersome, must be a better way...
    """

    ss_string = ss.dumps()
    if ss_string[0] == "B":  # an empty set just contains the single node B
        return 1
    for i, line in enumerate(ss_string.split("\n")):
        if line == ".":  # "." marks end of file, have this no. plus T and B
            return i + 2


def to_oxidd(
    zdd, n_options, inner_node_capacity=2000000, apply_cache_size=2000000, threads=1
):
    """
    Conversion to the ZDD format used by
    https://github.com/OxiDD/oxidd
    """

    from oxidd.zbdd import ZBDDManager

    zbdd = ZBDDManager(inner_node_capacity, apply_cache_size, threads)
    vbls = [zbdd.new_singleton() for i in range(n_options)]

    nodes = [zbdd.empty()]
    done_something = False
    for z in zdd:
        if not done_something:
            nodes.append(zbdd.base())
            done_something = True

        i, n, lo, hi = z[0], z[1], z[2], z[3]
        nodes.append(vbls[n].make_node(nodes[hi], nodes[lo]))

    return nodes[-1]
