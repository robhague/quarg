#!/usr/bin/env python3
# An example of implementing a Unix filter using Quarg

import argparse
import sys

import quarg

# A function specifying input and output directly
@quarg.arg.src(default=sys.stdin, nargs='?', type=argparse.FileType('r'))
@quarg.arg.dest(default=sys.stdout, nargs='?', type=argparse.FileType('w'))
def shouty(src, dest):
    """
    Takes a string and makes it SHOUTY.
    """
    dest.write(src.read().upper())

quarg.main()
