# Quarg: Zero-effort CLI generation.

Quarg is a standalone Python library that generates command-line interfaces based on the top-level functions of a Python script. It doesn't _require_ any explicit specification of the interface, but additional information may be provided to refine the generated interface incrementally.

# Quick Start Examples

`quarg` generates command line interfaces from the functions that already exist in your Python script:


```python
# example1.py
def repeat(x):
    return x+x
```

```
$ quarg example1.py Foo
FooFoo
```

The `quarg` command can be avoided by importing `quarg` as a module and calling its `main` function in place of the usual `if __name__ == '__main__'` block:

```python
#!/usr/bin/env python3
# example2.py

import quarg

def times(s, n : int):
    return s * n

quarg.main()
```

```
$ ./example2.py Bar 3
BarBarBar
```

Note that Python 3 type annotations can be used to convert command line arguments as desired. Here's a more complete example, including help generated from docstrings, and exposing keyword arguments as named, optional command line arguments:

```python
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
```

```
$ example3.py --help
usage: examples/example3.py [-h] [-s] [-S SEPARATOR] base num

Join multiple copies of a string together with a comma or similar separator.

positional arguments:
  base                  The string to repeat.
  num                   The number of times to repeat the string.

optional arguments:
  -h, --help            show this help message and exit
  -s, --sentence        If given, return the result in sentence case.
  -S SEPARATOR, --separator SEPARATOR
                        An alternative separator

$ example3.py baz 3
baz, baz, baz

$ example3.py wombat 3 --sentence -S \;
Wombat; wombat; wombat.
```

Further customisation is possible if desired; see the detailed guide below. However, none is required — you can use as much or as little of `quarg` as you want, and it can grow organically as your script matures.

# Detailed Guide

## Invoking Quarg CLIs

There are two ways to use Quarg to generate a command line interface. The first is to run the `quarg` script in place of the Python intepreter, either explicitly (`quarg _myscript.py_`) or by changing the '#!' line at the top of the script itself. Neither of these methods introduces a dependency on Quarg when importing the module, so it can be useful for providing a basic CLI to a module that isn't usually called on the command line.

The second is to import `quarg` and run the `main` function at the end of your script:

    quarg.main()

This function checks for `__name__ == '__main__'`, so there's no need to check explicitly.

## The Quarg API

Quarg analyses the script, picks out the top-level functions, and generates an [`argparse.ArgumentParser`](https://docs.python.org/library/argparse.html) from them. This is then used to parse the command line arguments and call the relvant function. All of the usual behaviour of `argparse` is present; in particular, you can call the script with the argument `-h` to see help for the interface.

By default, a subcommand is generated for each function found. This behaviour can be overriden using the `command` decorator:

    def internal_function(x,y):
        ...

    @quicli.command
    def external_one(a,b,c):
        ...

    @quicli.command
    def external_two(p,q):
        ...

If _any_ function is decorated with `command`, only functions thus decorated are included in the interface. In the above example, `external_one` and `external_two` are exported, but `internal_function` is not.

If a single function is identified, that function is called with the arguments passed on the command line (after parsing). If more than one function is identified, then each function becomes a [sub-command](https://docs.python.org/library/argparse.html#sub-commands) named after that function, in the style of `git` and similar utilities.

Positional arguments of a function are mapped to positional command line arguments, and keyword arguments to named command line arguments. For example, given a the function:

    def func(a, b, c=1, d=None):
       ...

the corresponding command line usage is:

    <scriptname> [-h] [-c C] [-d D] a b

Arguments specified with `*args` or `**kwargs` syntax are currently ignored; this may be improved in a future version.

Quarg reserves long argument names beginning with `--quarg` for its own use; the corresponding parameter names should be avoided.

Arguments with defaults are exposed as optional, named arguments, and
the type of the command line argument is set to match that of the
default value. In Python 3, type annotations are also used to set the
type of arguments (overriding the type of the default value, if
present). Boolean arguments are exposed as flags.

If the command function runs to completion, the return value is
printed to standard output (see `@quarg.output`, below), and the
program exits with a status of 0 (success). If an exception is thrown,
the string value of the exception (i.e., _without_ a traceback) is
printed to standard error, and the program exits with a status
of 1. If there is an error parsing the command line arguments, the
program immediately prints a usage message to standard error and exits
with a status of 2.

During development, it is often useful to output a traceback, as is the default behaviour for uncaught exceptions. This behaviour can be reinstated by passing the argument `--quarg-debug` on the command line, or setting the environment variable `QUARG_DEBUG` to a non-empty value.

Decorators are provided to allow more fine-grained (but entirely
optional) control:

- `@quarg.command`: Expose this function as a subcommand. If any functions are
thus marked, only these functions are exposed.

- `@quarg.output(<filter>)`: Any return value other than None is sent
  to standard output. By default, this is passed through `str`; this
  decorator allows another function to be specified. The return value
  should be a string, or `None` to suppress output. `None` may be
  passed as a special case to always suppress output. Additional positional parameters and keyword arguments may be passes along with the filter function. These are passes to the filter call using functools.partial

- `@quarg.arg.<argname>(<overrides>)`: This decorator allows further customisations of the behaviour of individual arguments. The provided keyword arguments are passed to the [add_argument()](https://docs.python.org/library/argparse.html#the-add-argument-method) call for `<argname>`. These values take precedence over values (such as types) inferred automatically. For example:

    ```
    @quarg.arg.x(type=int)
    def cmd(x):
        ...
    ```

    Quarg will add set `nargs` to `?` for any positional parameters that override `default` and does not specify `nargs` explicitly, as `default` alone does not produce useful behaviour in that case.

Module and function docstrings are used to generate help text. Any lines starting with '--<argname>:' (preceded by optional whitespace) are used as help for the relevant argument.

# FAQ

- **Why _another_ argument parsing library?** Python does indeed have plenty of options for argument parsing, not least the standard library's `argparse` that `quarg` uses under the hood. However, most are focused on producing complex interfaces with extensive, explicit specifications. I wanted to explore a different area; generating the interface with a little effort as possible (in fact, zero, an aim that `quarg` has achieved) while still allowing progressive refinement.

- **Can functions exposed as commands by `quarg` still be used from Python?** Absolutely; exposing a function to the command line via `quarg` does not change its normal functionality. One of the goals of the library is to make it easy to provide a command line interface to a module that's usually used from Python.

- **Does `quarg` support Legacy Python (also known as Python 2)?** For now. Quarg started off in Python 2, and currently supports both 2 and 3. However, this situation is likely to change in the near future; in particular, it is highly unlikely that the library will still support both versions when Python 2 itself goes out of support in 2020.

- **Are you a big fan of soft cheese, or Deep Space Nine?** Neither. During internal development, the module was called `quicli`, which is a far better name. Unfortunately, there's already a package with that name on PyPI, so it needed to be renamed before being made public. `quarg` was chosen as being brief, available, and still broadly reflective of the module's purpose ("QUick ARGument parsing").

## TODO

- [x] Optionally limit to specific functions (decorator)
- [x] Allow overrides of argparse parameters (decorator)
- [x] Parse option help (and type?) from docstring
- [x] Generate single-letter short names
- [x] Elide subcommand if only one function is being exposed
- [x] Infer types from [PEP 484](https://www.python.org/dev/peps/pep-0484/) type hints
- [x] Allow customization of the way output is returned
- [ ] Handle **kwargs by using parse_known_args() and processing leftovers
- [ ] Support generation of command suites from classes
- [ ] Support running modules with "quarg -m <modulename>"
