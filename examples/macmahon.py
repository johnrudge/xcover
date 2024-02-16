"""Routines for MacMahon's triangular edge-matching puzzles"""

from itertools import product
from shapely import Polygon, Point
import numpy as np
import matplotlib.pyplot as plt

default_colors = {"a": "white", "b": "tab:blue", "c": "tab:green", "d": "tab:red"}


def macmahon_mesh(boundary_word, initial_cell=[0, 0]):
    """
    Construct a mesh of equilateral triangles given a description of the
    boundary by a boundary word.

    Returns both the cells of the mesh and the edges of the boundary
    """
    cell = initial_cell
    vertices = []
    boundary_edges = []
    sgn = 1
    for symbol in boundary_word:
        if symbol in ["_", "\\", "/"]:
            # these symbols tell us the kind of edge
            direction = symbol
        elif symbol == "-":
            # for a minus sign we're going backwards on an edge
            sgn = -1
        else:
            # the number tells us how far we go
            number = int(symbol)
            if sgn == 1:
                # going forward
                if direction == "_":
                    edges = [(cell[0] + i, cell[1], direction) for i in range(number)]
                elif direction == "/":
                    edges = [(cell[0], cell[1] + i, direction) for i in range(number)]
                elif direction == "\\":
                    edges = [
                        (cell[0] - 1 - i, cell[1] + i, direction) for i in range(number)
                    ]
            else:
                # going backward
                if direction == "_":
                    edges = [
                        (cell[0] - 1 - i, cell[1], direction) for i in range(number)
                    ]
                elif direction == "/":
                    edges = [
                        (cell[0], cell[1] - 1 - i, direction) for i in range(number)
                    ]
                elif direction == "\\":
                    edges = [
                        (cell[0] + i, cell[1] - 1 - i, direction) for i in range(number)
                    ]

            # Now work out new position
            if direction == "_":
                cell[0] += number * sgn
            elif direction == "/":
                cell[1] += number * sgn
            elif direction == "\\":
                cell[0] -= number * sgn
                cell[1] += number * sgn

            sgn = 1
            vertices.append(np.array(cell))
            boundary_edges.extend(edges)

    # Given the vertices of the mesh, we can now work out which cells lie inside
    vertices = np.array(vertices)
    x = vertices[:, 0]
    y = vertices[:, 1]
    poly = Polygon(shell=vertices)

    cells = []
    for i in range(min(x), max(x) + 1):
        for j in range(min(y), max(y) + 1):
            if poly.contains(Point([i + 1 / 3, j + 1 / 3])):
                # "normal" triangle
                cells.append((i, j, False))
            if poly.contains(Point([i + 2 / 3, j + 2 / 3])):
                # upside-down triangle
                cells.append((i, j, True))

    return cells, boundary_edges


def macmahon_pieces():
    """The 24 unique triangular tiles with a choice of four colours."""
    ts = []
    for x in product(["a", "b", "c", "d"], repeat=3):
        s1 = (x[1], x[2], x[0])
        s2 = (x[2], x[0], x[1])
        if x not in ts and s1 not in ts and s2 not in ts:
            ts.append(x)  # only include is not cyclically the same as what have
    return ts


def cell_edges(cell):
    """Given a triangular cell, determine its three edges"""
    x, y, orient = cell

    edges = []
    if orient:
        edges.append((x, y + 1, "_"))
        edges.append((x + 1, y, "/"))
        edges.append((x, y, "\\"))
    else:
        edges.append((x, y, "_"))
        edges.append((x, y, "/"))
        edges.append((x, y, "\\"))
    return edges


def cell_to_string(cell):
    """A string representation of a given cell"""
    x, y, orient = cell
    cell_string = str(x) + "," + str(y)
    if orient:
        cell_string += "'"
    return cell_string


def edge_to_string(edge, color=None):
    """A string representation of a given edge"""
    x, y, direction = edge
    edge_string = direction + str(x) + "," + str(y)
    if color:
        edge_string += ":" + color
    return edge_string


def macmahon_option(piece, cell, rot):
    """The option for placing a given piece on a given cell and a given rotation"""
    option = []
    option.append(cell_to_string(cell))
    option.append("".join(piece))

    if rot == 0:
        rotated_piece = piece
    elif rot == 1:
        rotated_piece = (piece[1], piece[2], piece[0])
    else:
        rotated_piece = (piece[2], piece[0], piece[1])

    edges = cell_edges(cell)
    for i, edge in enumerate(edges):
        option.append(edge_to_string(edge, color=rotated_piece[i]))
    return option


def boundary_condition(boundary_edges, color):
    """Option describing the boundary condition that boundary edges are a certain color."""
    option = ["*"]
    for edge in boundary_edges:
        option.append(edge_to_string(edge, color=color))
    return option


def macmahon_options(cells, pieces, boundary_color=None, boundary_edges=None):
    """
    Given the cells of the mesh, the set of pieces, and possibly the
    boundary edges and coloring, determine the list of options for the exact
    cover problem.
    """
    options = []
    for cell in cells:
        for piece in pieces:
            opts = [macmahon_option(piece, cell, rot) for rot in range(3)]
            if opts[0] == opts[1]:  # case where rotation gives same thing
                options.append(opts[0])
            else:
                options.extend(opts)

    if boundary_color:
        options.append(boundary_condition(boundary_edges, "a"))
    return options


def macmahon_primary(cells, pieces):
    """The primary items for the exact cover problem."""
    piece_strings = ["".join(piece) for piece in pieces]
    cell_strings = [cell_to_string(cell) for cell in cells]
    return piece_strings + cell_strings + ["*"]


def plot_filled_triangle(w1, w2, w3, facecolor="lightsalmon", edgecolor="black"):
    """Given three Cartesian vectors giving vertices, plot a filled triangle."""
    plt.fill(
        [w1[0], w2[0], w3[0]],
        [w1[1], w2[1], w3[1]],
        facecolor=facecolor,
        edgecolor=edgecolor,
    )


def plot_piece(s, colors=None):
    """Given one of the options in a solution, plot the piece."""
    if colors is None:
        colors = default_colors

    place = s[0].strip("'")
    h_color = colors[s[2].split(":")[-1]]
    f_color = colors[s[3].split(":")[-1]]
    b_color = colors[s[4].split(":")[-1]]

    orientation = s[0][-1] == "'"
    x_y = place.split(",")
    x = int(x_y[0])
    y = int(x_y[1])

    shift = np.array([x + 0.5 * y, y * np.sqrt(3.0) / 2.0], dtype=float)
    if orientation == 0:
        v1 = np.array([0.0, 0.0]) + shift
        v2 = np.array([1.0, 0.0]) + shift
        v3 = np.array([0.5, np.sqrt(3.0) / 2.0]) + shift
        c = (1.0 / 3.0) * (v1 + v2 + v3)

        plot_filled_triangle(c, v1, v2, facecolor=h_color)
        plot_filled_triangle(c, v2, v3, facecolor=b_color)
        plot_filled_triangle(c, v1, v3, facecolor=f_color)

    if orientation == 1:
        v1 = np.array([1.5, np.sqrt(3.0) / 2.0]) + shift
        v2 = np.array([1.0, 0.0]) + shift
        v3 = np.array([0.5, np.sqrt(3.0) / 2.0]) + shift
        c = (1.0 / 3.0) * (v1 + v2 + v3)

        plot_filled_triangle(c, v1, v2, facecolor=f_color)
        plot_filled_triangle(c, v2, v3, facecolor=b_color)
        plot_filled_triangle(c, v1, v3, facecolor=h_color)


def plot_solution(solution, colors=None):
    """Plot a solution with colors specified by a dictionary mapping"""
    if colors is None:
        colors = default_colors
    for s in solution:
        if s[0] != "*":  # ignore the boundary condition
            plot_piece(s, colors)
    plt.gca().set_aspect("equal")
    plt.axis("off")
    plt.tight_layout()
