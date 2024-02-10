from xcover import covers, covers_bool
from xcover.utils import verify_exact_cover
from xcover.io import read_xcover_from_file
import numpy as np


def test_knuth_simple():
    options = [
        {"c", "e"},
        {"a", "d", "g"},
        {"b", "c", "f"},
        {"a", "d", "f"},
        {"b", "g"},
        {"d", "e", "g"},
    ]

    sols = list(covers(options))
    [verify_exact_cover(s, options) for s in sols]

    assert set(sols[0]) == {0, 3, 4}


def test_wikipedia():
    options = [{1, 4, 7}, {1, 4}, {4, 5, 7}, {3, 5, 6}, {2, 3, 6, 7}, {2, 7}]

    sols = list(covers(options))
    [verify_exact_cover(s, options) for s in sols]

    assert set(sols[0]) == {1, 3, 5}


def test_bool_solve():
    to_cover = np.array(
        [
            [1, 0, 0, 1, 1, 0, 1, 0],
            [1, 0, 0, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 1, 1, 0],
            [1, 0, 1, 0, 1, 1, 0, 0],
            [1, 0, 0, 0, 1, 0, 1, 1],
            [1, 0, 1, 1, 1, 0, 0, 0],  # <- 5
            [1, 0, 0, 0, 0, 1, 1, 1],  # <- 6
            [0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 0, 1],
            [0, 1, 0, 0, 1, 1, 1, 0],
            [0, 1, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 1, 0, 1, 1],
            [0, 1, 1, 1, 1, 0, 0, 0],  # <- 12
            [0, 1, 0, 0, 0, 1, 1, 1],  # <- 13
        ]
    )
    sols = list(covers_bool(to_cover))

    true_sols = [{5, 13}, {6, 12}]
    s1 = set([frozenset(s) for s in sols])
    s2 = set([frozenset(s) for s in true_sols])
    assert s1 == s2


def test_simple_secondary():
    primary = ["a", "b", "c", "d", "e", "f", "g"]
    secondary = ["h", "i", "j", "k"]

    options = [
        [
            "c",
            "e",
            "k",
        ],
        ["a", "d", "g", "h"],
        ["b", "c", "f"],
        ["a", "d", "f", "h", "i"],
        ["b", "g", "j"],
        ["d", "e", "g", "i"],
        ["a", "j"],
    ]

    sols = list(covers(options, primary=primary, secondary=secondary))
    [verify_exact_cover(s, options, primary=primary, secondary=secondary) for s in sols]

    true_sols = [{0, 3, 4}, {2, 5, 6}]
    s1 = set([frozenset(s) for s in sols])
    s2 = set([frozenset(s) for s in true_sols])
    assert s1 == s2


def test_simple_colored():
    primary = ["p", "q", "r"]
    secondary = ["x", "y"]
    options = [
        ["p", "q", "x", "y:A"],
        ["p", "r", "x:A", "y"],
        ["p", "x:B"],
        ["q", "x:A"],
        ["r", "y:B"],
    ]

    sols = list(covers(options, primary=primary, secondary=secondary, colored=True))

    [
        verify_exact_cover(
            s, options, primary=primary, secondary=secondary, colored=True
        )
        for s in sols
    ]

    assert len(sols) == 1
    assert set(sols[0]) == {1, 3}


def test_simple_colored2():
    primary = ["a", "b", "c"]
    secondary = ["d", "e", "f"]
    options = [
        ["a", "b", "d"],
        ["c", "d"],
        ["c", "e"],
        ["a", "b", "d:BLUE"],
        ["c", "d:BLUE"],
        ["a", "b", "d:RED"],
        ["c", "d:RED"],
    ]

    sols = list(covers(options, primary=primary, secondary=secondary, colored=True))
    [
        verify_exact_cover(
            s, options, primary=primary, secondary=secondary, colored=True
        )
        for s in sols
    ]

    assert len(sols) == 5


def test_n_queens():
    n = 8
    options = [
        [
            "r%d" % row,
            "c%d" % col,
            "d%d" % (row + col),
            "a%d" % (row + n - 1 - col),
        ]
        for row in range(n)
        for col in range(n)
    ]
    secondary = set(("d%d" % i for i in range(2 * n - 1)))
    secondary.update(set(("a%d" % i for i in range(2 * n - 1))))

    cv = covers(options, secondary=secondary)
    n_sols = len(list(cv))

    assert n_sols == 92


def test_unsolvable():
    options = [
        [0, 1],
        [0, 2],
        [1, 4],
        [1, 5],
        [1, 6],
        [2, 4],
        [2, 5],
        [2, 6],
        [3, 4],
        [3, 5],
        [3, 6],
        [4, 5],
        [4, 6],
    ]
    sols = list(covers(options))

    assert len(sols) == 0


def test_file_solve():
    import os

    file1 = os.path.join(os.path.dirname(__file__), "dodecahedron.txt")
    options, primary, secondary, colored = read_xcover_from_file(file1)

    sols = list(covers(options, primary=primary, secondary=secondary, colored=colored))
    assert len(sols) == 300

    file2 = os.path.join(os.path.dirname(__file__), "langford8.txt")
    options, primary, secondary, colored = read_xcover_from_file(file2)

    sols = list(covers(options, primary=primary, secondary=secondary, colored=colored))
    assert len(sols) == 150
