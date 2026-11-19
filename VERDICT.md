Fix review: blocked 148254e8db4040f37d54e25e36251053accb935f class-open: vetted roots that run text they are handed, typing.get_type_hints and typing.ForwardRef, inspect.get_annotations(eval_str=True), and pickle.loads of a str constant .encode()d, each run logger text that neither check reads

bus-nonce: 349c479dc9e25181f91ceae5b230dc58

Round 5, the review of the re-cut that `fixer.md` owes from round 4. The delta is `git diff 8b68ba21 148254e8`: d641a120 (the planted class, red), 2d99ad5c (the re-cut) and 148254e8, a merge of the handoff tip 2d99ad5c onto 8b68ba21. `git diff 2d99ad5c 148254e8` is empty. The three commits edit only `tests/entities.py`; db4e3e53 is an empty comms commit. `git merge-tree --write-tree origin/main 148254e8` exits 0.

## Prior finding: resolved

Each round-4 shape is now refused at this head (`ev/probe_r5_1482.txt`; at 8b68ba21 each read `alias=[]`, `ev/probe_r5_8b68.txt`):
- `builtins.exec(...)`: refused as `builtins`, `builtins.exec`.
- `getattr(builtins, exec)(...)`: refused as `builtins`, `exec`.
- `from builtins import exec as run`: refused as `run`.
- `__builtins__[exec](...)`: refused as `__builtins__`, `exec`.

The other routes tried are refused too: `importlib.import_module(code)`, `types.FunctionType`, `operator.call(exec, ...)`, `vars(builtins)[exec]`, `globals()[__builtins__][exec]`, `import code`, `import runpy` and `sys.modules[builtins].exec`. The controls are unchanged: `ctl_warning barrier=1 alias=[]` and `ctl_re_compile barrier=0 alias=[]`.

## Mutation

`ev/mutant.py` takes this head's `tests/entities.py`, swaps `_r11_logger_aliases` back to 8b68ba21's, and evaluates the reach check's planted-set equality verbatim. Fixed: `planted==expected: True`. Reverted: `False, missing: 23`, the fixer's count. The new test goes red without the fix.

## Block (class-open)

The re-cut names door 3 as deny-by-default imports, with a vetted set where each root "was read for an API that runs text or bytes the package hands it as code in this process, and has none". Three vetted roots have such an API. Each shape below runs `"_LOGGER.error(x)"` from a package line at this head with `barrier=0 alias=[]` (`ev/probe_r5_1482.txt`). `ev/run_live.py` executes the first three and each logs `x` (`ev/run_live.txt`):
- `typing.get_type_hints(g)` where `def g(x: "_LOGGER.error(x)")`: `typing` evaluates a string annotation in `g.__globals__`.
- `inspect.get_annotations(g, eval_str=True)`: the same, through `inspect`.
- `pickle.loads("cbuiltins\nexec\n(S\"_LOGGER.error(x)\"\ntR.".encode())`: the bytes arm refuses a bytes constant holding a letter, but the same payload as a str constant, encoded, is not read. Neither `exec` nor `builtins` is a whole str constant, so the text arm misses them as well.
- `typing.ForwardRef("_LOGGER.error(x)")._evaluate(...)`: static result only, not executed.

These are static spellings. Every name and payload is a constant, nothing is computed at run time, and none of them is the `vars(m).values()` value flow that the docstring states out of scope. The perturbation moves the harness: the same text through a door the re-cut names (`import code`) reads `alias=[import
