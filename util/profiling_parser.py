import sys
import os

import pstats
from pstats import SortKey


def main():
    path = os.path.abspath(sys.argv[1])
    print(f"Parsing stats file {path}")
    stats = pstats.Stats(path)
    stats.sort_stats(SortKey.CUMULATIVE).print_stats(30)

    print("======================================================================\n\n")

    stats.sort_stats(SortKey.TIME).print_stats(30)


if __name__ == "__main__":
    main()
