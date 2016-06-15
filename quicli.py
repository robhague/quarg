"""
Quicli: Zero-effort CLI generation.

To use, add "-m quicli" to the #! line at the start of your script:

    #!/usr/bin/env python -m quicli

See the README file for more details.
"""

if __name__ != '__main__':
    # Module definition
    import inspect
    import re

    _arg_overrides = {}

    class _arg:

        """Override argparse parameters.

        Provide keyword arguments that will be passed to add_argument when
        generating the parser. For example:

            @quicli.arg.x(type=int)
            def cmd(x):
                ...

        quicli.arg is an instance of this class. It auto-generates attributes
        that return functions, which in turn creates decorators to record the
        overrides for later use. Simplifications to this code would be
        appreciated.
        """

        def __getattr__(self, name):
            def wrap(**kwargs):
                def decorator(f):
                    _arg_overrides[(f, name)] = kwargs
                    return f
                return decorator
            return wrap
    arg = _arg()

    commands = []

    arghelp_re = re.compile(r'^\s*--(\w+):\s+(.*)$')

    def parse_docstring(doc):
        "Parse a docstring for argument descriptions."
        if doc:
            lines = inspect.cleandoc(doc).splitlines()
            help = lines[0]
            arghelp = {}
            description_lines = []
            for l in lines:
                m = arghelp_re.match(l.strip())
                if m:
                    arghelp[m.group(1)] = m.group(2)
                else:
                    description_lines.append(l)
            return help, '\n'.join(description_lines), arghelp
        else:
            return ('', '', '')

    def make_parser(f, parser):
        help, description, arghelp = parse_docstring(inspect.getdoc(f))
        if callable(parser):
            # Create a subparser using the supplied function
            parser = parser(f.__name__, help=help)

        parser.description = description
        argspec = inspect.getargspec(f)
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
else:
    # Run as a module; generate an interface for argv[1]
    import sys
    execfile(sys.argv[1])
    # Record the objects created in the target file
    target_objects = list(locals().values())

    import argparse
    import inspect
    from quicli import make_parser, commands

    # If no commands are decorated, expose all top-level functions from the
    # script.
    commands = commands or [f for f in target_objects
                            if inspect.isfunction(f)
                            and f.__module__ == '__main__']

    parser = argparse.ArgumentParser(prog=sys.argv[1], description=__doc__)

    if len(commands) == 1:
        # Only one command is exposed, so don't use a subcommand
        make_parser(commands[0], parser)
        parser.set_defaults(_quicli_func=commands[0])
    else:
        subparsers = parser.add_subparsers(dest='_quicli_subcommand')
        for cmd in commands:
            subparser = make_parser(cmd, subparsers.add_parser)
            subparser.set_defaults(_quicli_func=cmd)

    args = parser.parse_args(sys.argv[2:])
    real_args = {k: getattr(args, k)
                 for k in vars(args) if not k.startswith('_quicli')}
    result = args._quicli_func(**real_args)
    if result:
        print result
