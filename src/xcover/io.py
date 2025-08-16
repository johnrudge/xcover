"""Simple file i/o"""

from .solvers import items


def read_xcover_from_file(filename):
    """
    Simple parser for files decribing exact cover problems in Knuth's format
    """
    with open(filename, "r", encoding="utf-8") as cover_file:
        first = True
        options = []
        for line in cover_file.readlines():
            if first:
                if (
                    line[0] == "|" or line[0] == "/" or line == "\n"
                ):  # a comment line, ignore
                    continue
                first = False
                split_pri_sec = line.rstrip("\n").lstrip().split("|")
                primary = split_pri_sec[0].split()
                if len(split_pri_sec) > 1:
                    secondary = split_pri_sec[1].split()
                    colored = True
                else:
                    secondary = None
                    colored = False
            else:
                splits = line.rstrip("\n").lstrip().split()
                options.append(splits)

    return options, primary, secondary, colored


def write_xcover_to_file(
    filename, options, primary=None, secondary=None, colored=False, item_to_string=None
):
    """
    Write options to knuth-formatted DLX file.

    item_to_string is a function that describes the mapping from items to
    strings in the file. If None, a simple mapping which removes spaces is used.
    """

    # A single list of all the options
    all_opts = [o for opt in options for o in opt]

    # Work out explicit primary and secondary item lists
    primary, secondary = items(all_opts, primary, secondary, colored)

    if item_to_string is None:

        def item_to_string(item):
            return str(item).replace(" ", "")

    with open(filename, "w", encoding="utf-8") as cover_file:
        for item in primary:
            cover_file.write(item_to_string(item))
            cover_file.write(" ")
        if secondary:
            cover_file.write("| ")
            for item in secondary:
                cover_file.write(item + " ")
        cover_file.write("\n")
        for option in options:
            for item in option:
                cover_file.write(item_to_string(item))
                cover_file.write(" ")
            cover_file.write("\n")
