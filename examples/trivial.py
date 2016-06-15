#!/usr/bin/env python -m quicli
"""Basic maths functions.

Simple use of the quicli module, with no additional
annotation.
"""

def prod(x,y = 1):
    """Multiply two numbers.

    This is pretty basic stuff."""
    print x, "*", y, "=", int(x) * y

def sum(x, y = 0):
    """Add two numbers.

    Addition was known to the ancient Babylonians."""
    print x, "+", y, "=", int(x) + y
