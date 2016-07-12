# Quicli: Zero-effort CLI generation.


To use, run quicli in place of the Python intepreter, or run this at the end of your script:

    quicli.main()

(The `quicli.main()` function checks for `__name__ == '__main__'`, so
there's no need to check explicitly).

A subcommand is generated for each function defined in the script. Module and
function docstrings are used to generate help text. Decorators are provided to
allow more fine-grained (but entirely optional) control:

- `@quicli.command`: Expose this function as a subcommand. If any functions are
thus marked, only these functions are exposed.
- `@quicli.arg.<argname>(<overrides>)`: Pass the provided keyword arguments to
add_argument() for `<argname>`. For example:

    ```
    @quicli.arg.x(type=int)
    def cmd(x):
        ...
    ```

##TODO

- [x] Optionally limit to specific functions (decorator)
- [x] Allow overrides of argparse parameters (decorator)
- [x] Parse option help (and type?) from docstring
- [x] Generate single-letter short names
- [x] Elide subcommand if only one function is being exposed
- [ ] Handle **kwargs by using parse_known_args() and processing leftovers
- [ ] Add `setup.py` and so on
- [ ] Support generation of command suites from classes
- [ ] Support running modules with "quicli -m <modulename>"
