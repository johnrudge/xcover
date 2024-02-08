"""Simple file i/o"""


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
                split_pri_sec = line.rstrip("\n").split("|")
                primary = split_pri_sec[0].split(" ")
                if "" in primary:
                    primary.remove("")
                if len(split_pri_sec) > 1:
                    secondary = split_pri_sec[1].split(" ")
                    secondary.remove("")
                    colored = True
                else:
                    secondary = None
                    colored = False
            else:
                splits = line.rstrip("\n").split(" ")
                options.append(splits)

    return options, primary, secondary, colored
