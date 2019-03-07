#!/usr/bin/env python3
# An example of implementing a Unix filter using Quarg

import argparse
from typing import TextIO
import sys

import quarg

# A function specifying input and output directly
@quarg.arg.src(default=sys.stdin, type=argparse.FileType('r'))
@quarg.arg.dest(default=sys.stdout, type=argparse.FileType('w'))
def shouty(src, dest):
    """
    Takes a string and makes it SHOUTY.
    """
    dest.write(src.read().upper())

# Specify an input argument with a type declaration (and use a return
# value for output)
@quarg.arg.src(default=sys.stdin)
def title(src: TextIO):
    """
    Takes a string and makes it Title Case.
    """
    return src.read().title()

quarg.main()
