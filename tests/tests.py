#!/usr/bin/env python

import io
import os
import subprocess
import unittest

# Allow child processes to import quicli
os.environ['PYTHONPATH'] = "..:" + os.getenv('PYTHONPATH', '')

# Find the tests directory (if the current directory, make this explicit)
testdir = os.path.dirname(__file__) or '.'
scriptdir = os.path.join(testdir, "scripts")

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
        Test that quicli correctly exposes a single top-level function.
        """
        script = runnable_script('single_function')
        self.assertRegexpMatches(script(expect_error=True), r'^usage:')
        self.assertRegexpMatches(script('-h'), r'^usage:')
        self.assertEqual(script('1', '-y', '2').strip(), '3')

    def test_suite(self):
        """
        Test that quicli correctly exposes multiple top-level functions as commands.
        """
        script = runnable_script('suite')
        self.assertRegexpMatches(script(expect_error=True), r'^usage:')
        self.assertRegexpMatches(script('-h'), r'^usage:')
        self.assertEqual(script('sum', '1', '-y', '2').strip(), '3')

    def test_command_decorator(self):
        """
        Test that quicli correctly exposes a single decorated top-level function.
        """
        script = runnable_script('command_decorator')
        self.assertRegexpMatches(script(expect_error=True), r'^usage:')
        self.assertRegexpMatches(script('-h'), r'^usage:')
        self.assertEqual(script('sum', '1', '-y', '2').strip(), '3')
        self.assertRegexpMatches(script('div', '1', '-y', '2', expect_error=True), r'{prod,sum}')

if __name__ == '__main__':
    unittest.main()
