class ansicolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

def printColoredLine(line, color, shift = 0, discard_colors = False):
    str = ""

    for i in range(shift):
        str = '%s%s'%('\t', str)

    if discard_colors:
        print("%s%s" % (str, line))
    else:
        print("%s%s%s%s" % (str, color, line, ansicolors.ENDC))
