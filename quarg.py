"""Quarg: Zero-effort CLI generation.

To add basic automatic parsing to a script, import this module and add
the following at the end:

    quarg.main()

This function will process command line arguments only when the file
is run as a script, not when imported as a module. See the README file
for more details.

"""
import argparse
import inspect
import re
import sys

_arg_overrides = {}

class _arg:

    """Override argparse parameters.

    Provide keyword arguments that will be passed to add_argument when
    generating the parser. For example:

        @quarg.arg.x(type=int)
        def cmd(x):
            ...

    quarg.arg is an instance of this class. It auto-generates attributes
    that return functions, which in turn creates decorators to record the
    overrides for later use. Simplifications to this code would be
    appreciated.
    """

    def __getattr__(self, name):
        def wrap(**kwargs):
            def decorator(f):
                _arg_overrides[(f, name)] = dict(_arg_overrides.get((f,name), {}), **kwargs)
                return f
            return decorator
        return wrap
arg = _arg()

commands = []

arghelp_re = re.compile(r'^(\s*--(\w+):\s+)(.*)$')

def parse_docstring(doc):
    "Parse a docstring for argument descriptions."
    if doc:
        lines = inspect.cleandoc(doc).splitlines()
        help = lines[0]
        arghelp = {}
        description_lines = []
        arg = indent = None
        for l in lines:
            m = arghelp_re.match(l.strip())
            if m:
                indent, arg = len(m.group(1)), m.group(2)
                arghelp[arg] = [m.group(3).strip()]
            elif indent and l[:indent].isspace():
                arghelp[arg].append(l.strip())
            else:
                description_lines.append(l)
                arg = indent = None
        return (help, '\n'.join(description_lines),
                {a:' '.join(l) for a,l in arghelp.items()})
    else:
        return ('', '', '')

# getargspec is deprecated in Python 3
_getargspec = inspect.getfullargspec if hasattr(inspect, "getfullargspec") else inspect.getargspec

def make_parser(f, parser):
    help, description, arghelp = parse_docstring(inspect.getdoc(f))
    if callable(parser):
        # Create a subparser using the supplied function
        parser = parser(f.__name__, help=help)

    parser.description = description
    argspec = _getargspec(f)
    defaults = dict(zip(argspec.args[-len(argspec.defaults):],
                        argspec.defaults)) if argspec.defaults else {}

    abbrevs = set()

    for a in argspec.args:
        names, params = [a], {}
        if len(a) == 1:
            abbrevs.add(a)

        if a in defaults:
            d = defaults[a]

            if len(a) > 1:
                names = ['--' + a]
                # Find a single letter abbreviation if possible
                letters = []
                for letter in a:
                    letters.append(letter.lower())
                    letters.append(letter.upper())
                for letter in letters:
                    if letter not in abbrevs:
                        abbrevs.add(letter)
                        names.insert(0, '-' + letter)
                        break
            else:
                names = ['-' + a]

            params['default'] = d
            if d is not None:
                params["type"] = type(d)

        if (f, a) in _arg_overrides:
            params.update(**_arg_overrides[(f, a)])

        if a in arghelp:
            params['help'] = arghelp[a]

        parser.add_argument(*names, **params)
    return parser

def command(f):
    """Expose the decorated function as a subcommand."""
    commands.append(f)
    return f

# Flag to record the fact that we've already run main
_have_run_main = False

def main(argv=sys.argv):
    """Parse command line arguments when the calling module is run as a
    script. If the module is imported, do nothing."""
    global _have_run_main
    f = inspect.stack()[1][0]
    if f.f_locals['__name__'] == '__main__' and not _have_run_main:
        # Only run main() once
        _have_run_main = True

        # Record the objects created in the target file
        target_objects = list(f.f_locals.values())

        # If no commands are decorated, expose all top-level functions from the
        # script.
        target_commands = commands or [fn for fn in target_objects
                                       if inspect.isfunction(fn)
                                       and fn.__module__ in ('__main__', '__quarg_main__')]

        parser = argparse.ArgumentParser(prog=argv[0],
                                         description=f.f_locals['__doc__'])

        if len(target_commands) == 1:
            # Only one command is exposed, so don't use a subcommand
            make_parser(target_commands[0], parser)
            parser.set_defaults(_quarg_func=target_commands[0])
        else:
            subparsers = parser.add_subparsers(dest='_quarg_subcommand')
            for cmd in target_commands:
                subparser = make_parser(cmd, subparsers.add_parser)
                subparser.set_defaults(_quarg_func=cmd)

        args = parser.parse_args(argv[1:])
        real_args = {k: getattr(args, k)
                     for k in vars(args) if not k.startswith('_quarg')}

        if '_quarg_func' in args:
            result = args._quarg_func(**real_args)
            if result:
                sys.stdout.write("{}\n".format(result))
        else:
            parser.print_usage()
            sys.exit(1)
