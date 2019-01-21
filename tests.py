#!/usr/bin/env python

import argparse
import io
import os
import re
import subprocess
import textwrap
import unittest

import quarg

# Allow child processes to import quarg
os.environ['PYTHONPATH'] = "..:" + os.getenv('PYTHONPATH', '')

# Find the tests directory (if the current directory, make this explicit)
testdir = os.path.dirname(__file__) or '.'
scriptdir = os.path.join(testdir, "test_scripts")

def runnable_script(scriptname):
    "Return a function that calls the name script as a subprocess."
    def run(*cmd, **kwargs):
        expect_error = kwargs.pop('expect_error', False)
        try:
            output = subprocess.check_output((os.path.join(scriptdir, scriptname),) + cmd,
                                             stderr=subprocess.STDOUT)
            if expect_error:
                raise Exception("Command {} unexpectedly succeeded".format(repr(cmd)))
            else:
                return output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            if not expect_error:
                raise e
            else:
                return e.output.decode('utf-8')
    return run

class TestScriptRunners(unittest.TestCase):

    def test_single_function(self):
        """
        Test that quarg correctly exposes a single top-level function.
        """
        script = runnable_script('single_function')
        self.assertTrue(re.search(r'^usage:', script(expect_error=True)))
        self.assertTrue(re.search(r'^usage:', script('-h')))
        self.assertEqual(script('1', '-y', '2').strip(), '3')

    def test_suite(self):
        """
        Test that quarg correctly exposes multiple top-level functions as commands.
        """
        script = runnable_script('suite')
        self.assertTrue(re.search(r'^usage:', script(expect_error=True)))
        self.assertTrue(re.search(r'^usage:', script('-h')))
        self.assertEqual(script('sum', '1', '-y', '2').strip(), '3')

    def test_command_decorator(self):
        """
        Test that quarg correctly exposes a single decorated top-level function.
        """
        script = runnable_script('command_decorator')
        self.assertTrue(re.search(r'^usage:', script(expect_error=True)))
        self.assertTrue(re.search(r'^usage:', script('-h')))
        self.assertEqual(script('sum', '1', '-y', '2').strip(), '3')
        self.assertTrue(re.search(r'{prod,sum}', script('div', '1', '-y', '2', expect_error=True)))

class MockParser:
    """
    A mock parser, allowing tests to examine the changes.
    """
    def __init__(self, name = None, help = None):
        self.name = name
        self.help = help
        self.description = None
        self.arguments = {}

    def add_argument(self, *names, **params):
        for name in names:
            self.arguments[name] = params

class ParseError(Exception): pass

class TestParser(argparse.ArgumentParser):
    """
    A real argument parser that allows errors to be caught.
    """
    def error(self, message):
        raise ParseError(message)


class TestFunctionProcessing(unittest.TestCase):

    def test_basic_arguments(self):
        def cmd(a, b, c=None, d=None):
            "A test function"
            pass

        p = quarg.make_parser(cmd, MockParser)
        self.assertEqual(p.name, "cmd")
        self.assertEqual(p.description, "A test function")
        self.assertEqual(set(p.arguments.keys()), set(['a', 'b', '-c', '-d']))
        self.assertNotIn('default', p.arguments['a'])
        self.assertEqual(p.arguments['-c']['default'], None)

    def test_types(self):
        def cmd(x=1, y="foo", z=None): pass
        p = quarg.make_parser(cmd, MockParser)
        self.assertEqual(p.arguments['-x']['type'], int)
        self.assertEqual(p.arguments['-y']['type'], str)
        self.assertNotIn('type', p.arguments['-z'])

    def test_flags(self):
        "Test both positive-sense and negative-sense flags"
        def cmd(pos=False, neg=True): pass
        p = quarg.make_parser(cmd, TestParser())

        # Check that various valid inputs set the flags correctly
        for (args, expected_pos, expected_neg) in [
                ([], False, True),
                (["--pos"], True, True),
                (["--neg"], False, False),
                (["--pos", "--neg"], True, False),
                (["-n", "-p"], True, False),
                (["-n", "-p", "-n"], True, False),
        ]:
            parsed = p.parse_args(args)
            self.assertEqual(parsed.pos, expected_pos)
            self.assertEqual(parsed.neg, expected_neg)

        # Check that flags do not consume arguments
        with self.assertRaises(ParseError):
            p.parse_args(["--pos", "1", "--neg", "0"])


    def test_arg_decorator(self):

        @quarg.arg.x(type=int)
        @quarg.arg.y(type="string")
        @quarg.arg.y(help="Some help")
        @quarg.arg.z(action="store_const", const="Z")
        def cmd(x,y,z): pass

        p = quarg.make_parser(cmd, MockParser)

        # Single arg decorator
        self.assertEqual(p.arguments['x']['type'], int)

        # Multiple arg decorator
        self.assertEqual(p.arguments['y']['type'], 'string')
        self.assertEqual(p.arguments['y']['help'], 'Some help')

        # Single arg decorator with multiple values
        self.assertEqual(p.arguments['z']['action'], 'store_const')
        self.assertEqual(p.arguments['z']['const'], 'Z')

def _pds(docstring):
    """A utility to dedent and parse a docstring"""
    return quarg.parse_docstring(textwrap.dedent(docstring))

class TestParseDocString(unittest.TestCase):

    def test_multiline_arg_descriptions(self):
        help, desc, arghelp = _pds("""
        help

        desc1
        desc2

        --x: x1
        --y: y1
             y2
        --z: z1
        """)
        self.assertEqual(help, "help")
        self.assertEqual(desc, "help\n\ndesc1\ndesc2\n")
        self.assertEqual(arghelp["x"], "x1")
        self.assertEqual(arghelp["y"], "y1 y2")
        self.assertEqual(arghelp["z"], "z1")

if __name__ == '__main__':
    unittest.main()
