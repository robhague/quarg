#!/usr/bin/env python3
# example3.py
import quarg

def convert_to_sentence(s):
    return s.capitalize()+"."

@quarg.command # Only this function is used to generate a CLI
def join(base, num : int, sentence: bool, separator=","):
    """
    Join multiple copies of a string together with a comma or similar separator.

    --base: The string to repeat.
    --num: The number of times to repeat the string.
    --sentence: If given, return the result in sentence case.
    --separator: An alternative separator
    """
    result = (separator+" ").join([base] * num)
    if sentence:
        result = convert_to_sentence(result)
    return result

quarg.main()
