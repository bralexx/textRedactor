import curses
import sys
from Interface import Interface


args = sys.argv
args.pop(0)
i = Interface(args)
curses.wrapper(i.draw)
