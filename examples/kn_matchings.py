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
print("Expected count:", factorial2(n - 1, exact=True) if not n % 2 else 0)


def solve_covers():
    print("covers count:", sum(1 for x in covers(options)))


def solve_covers_zdd():
    n_options = len(options)
    zdd = covers_zdd(options, use_memo_cache=True)
    oxi_zdd = to_oxidd(zdd, n_options)
    print("covers_zdd count:", int(oxi_zdd.sat_count_float(n_options)))


import timeit

time1 = timeit.timeit(solve_covers, number=1)
time2 = timeit.timeit(solve_covers_zdd, number=1)
print(f"covers solve in {time1} s")
print(f"covers_zdd solve in {time2} s")
