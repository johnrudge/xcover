"""Some additional routines for manipulating zdds"""


def to_zdd_algorithms(zdd):
    from zdd_algorithms import empty, base, get_node

    nodes = [empty(), base()]
    for z in zdd:
        i, n, lo, hi = z[0], z[1], z[2], z[3]
        nodes.append(get_node(n, nodes[lo], nodes[hi]))
    return nodes[-1]


def to_setset(zdd, n_options):
    from graphillion import setset

    setset.set_universe([i for i in range(n_options)])

    zdd_string = ""
    for z in zdd:
        i, n, lo, hi = z[0], 1 + z[1], z[2], z[3]
        zdd_string += f"{i} {n} {"B" if lo ==0 else lo} {"T" if hi == 1 else hi}\n"
    zdd_string += ".\n"
    return setset(setset.loads(zdd_string))
