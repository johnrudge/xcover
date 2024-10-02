"""
All perfect matchings of a complete graph K_n.

An example where computing with a ZDD can be faster.
"""

from xcover import covers, covers_zdd
from xcover.zdd_utils import to_oxidd
from itertools import combinations
from scipy.special import factorial2

n = 16
options = list(combinations(range(n), 2))

# Show the expected answer (n-1)!!
print("Expected solution count:", factorial2(n - 1, exact=True) if not n % 2 else 0)


def solve_covers():
    print("covers solution count:", sum(1 for x in covers(options)))


def solve_covers_zdd():
    n_options = len(options)
    zdd = covers_zdd(options, use_memo_cache=True, choose_heuristic="leftmost")
    oxi_zdd = to_oxidd(
        zdd, n_options, inner_node_capacity=100000, apply_cache_size=50000
    )
    print("covers_zdd solution count:", int(oxi_zdd.sat_count_float(n_options)))
    print("covers_zdd node count:", oxi_zdd.node_count())


import timeit

time1 = timeit.timeit(solve_covers, number=1)
time2 = timeit.timeit(solve_covers_zdd, number=1)
print(f"covers solve in {time1} s")
print(f"covers_zdd solve in {time2} s")
