# Quarg: Zero-effort CLI generation.


To use, run quarg in place of the Python intepreter, or run this at the end of your script:

    quarg.main()

(The `quarg.main()` function checks for `__name__ == '__main__'`, so
there's no need to check explicitly).

A subcommand is generated for each function defined in the
script. Module and function docstrings are used to generate help text.

Arguments with defaults are exposed as optional, named arguments, and
the type of the command line argument is set to match that of the
default value. In Python 3, type annotations are also used to set the
type of arguments (overriding the type of the default value, if
present). Boolean arguments are exposed as flags.

Decorators are provided to allow more fine-grained (but entirely
optional) control:

- `@quarg.command`: Expose this function as a subcommand. If any functions are
thus marked, only these functions are exposed.
- `@quarg.arg.<argname>(<overrides>)`: Pass the provided keyword arguments to
add_argument() for `<argname>`. These values take precedence over values (such as types) inferred automatically. For example:

    ```
    @quarg.arg.x(type=int)
    def cmd(x):
        ...
    ```

## FAQ

- **Why _another_ argument parsing library?** Python does indeed have plenty of options for argument parsing, not least the standard library's `argparse` that `quarg` uses under the hood. However, most are focused on producing complex interfaces with extensive, explicit specifications. I wanted to explore a different area; generating the interface with a little effort as possible (in fact, zero, an aim that `quarg` has achieved) while still allowing progressive refinement.

- **Are you a big fan of soft cheese, or Deep Space Nine?** Neither. During internal development, the module was called `quicli`, which is a far better name. Unfortunately, there's already a package with that name on PyPI, so it needed to be renamed before being made public. `quarg` was chosen as being brief, available, and still broadly reflective of the module's purpose ("QUick ARGument parsing").

## TODO

- [x] Optionally limit to specific functions (decorator)
- [x] Allow overrides of argparse parameters (decorator)
- [x] Parse option help (and type?) from docstring
- [x] Generate single-letter short names
- [x] Elide subcommand if only one function is being exposed
- [x] Infer types from [PEP 484](https://www.python.org/dev/peps/pep-0484/) type hints
- [ ] Allow customization of the way output is returned
- [ ] Handle **kwargs by using parse_known_args() and processing leftovers
- [ ] Support generation of command suites from classes
- [ ] Support running modules with "quarg -m <modulename>"
