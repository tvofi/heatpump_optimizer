import inspect, textwrap
def mutated(mod, owner, name, lineno, old, new):
    fn = owner.__dict__[name]
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, (lines[i], old)
    lines[i] = new + "\n"
    src = textwrap.dedent("".join(lines))
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + src, mod.__file__, "exec"), ns)
    return ns[name]
