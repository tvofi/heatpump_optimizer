Fix review: blocked f2d21754ab19327fb6089c32dfab9913c4b31929 class-open: asyncio's loop.call_exception_handler and default_exception_handler write an ERROR record to a logger from package text that names no logger, neither refused nor read by the barrier, the same kind as the refused warnings module and the residue's system_log service

bus-nonce: f3e1f805ff784b2c2e885639fbc506af
pending-ci: gate

Round 6, a later round over the reviewed head 148254e8. The PR's own delta is `git diff cb14ef7b f2d21754` (cb14ef7b: `git merge-tree --write-tree 053c33bc 148254e8`, the reviewed head on this head's base). It touches only `tests/entities.py` (the payload re-cut, the shipped-file reader and its plants) and two docstrings of `tests/structure.py`. No production delta, so the scope does not widen.

## Block

The docstring's claim reads: "every logger the package can reach from text written in its shipped tree is either a `_LOGGER.<level>(...)` call that the barrier reads or is refused". The diff puts APIs that write a log record without naming a logger inside the class: it refuses the module `warnings` because Home Assistant turns on `logging.captureWarnings`. The residue names one more, Home Assistant's `system_log` service. Two stdlib APIs of the same kind are neither refused nor in the residue:

- `asyncio.get_running_loop().call_exception_handler({'message': 'x'})`
- `asyncio.get_running_loop().default_exception_handler({'message': 'x'})`

Inside a package module, each reads `barrier=0 alias=[]` at this head (`ev/probe_r6_f2d2.txt`, shapes `exc_handler`, `exc_handler_default`, `exc_handler_per_cycle`). The per-cycle shape is an unlatched call in `_async_update`. `ev/run_live_r6.py` runs both under Python 3.14.7, and each writes a record at ERROR: `logged: 'x\ny'`, logger `asyncio ERROR x`. Its null control, the same loop with neither call (`ev/run_live_r6_null.py`), logs `''`. Home Assistant installs its own loop exception handler for the first call. This seat has no Home Assistant to run it under, so its record there is not verified.

These are not derived text. Every name and the payload are constants, so they fall inside the claim and outside the residue. The body says a new evaluator is no block. That is the fixer's framing, not the contract. Neither call evaluates text: each is a log write that the payload arm cannot see, because its text names no logger. `grep -rn call_exception_handler\|default_exception_handler custom_components/` prints nothing at this head, so this is a predicate's unguarded domain, not a live site. These two are every seam this review found. There are three ways out: refuse them by spelling, as `warnings` is; or name them in the residue with a reason; or narrow the claim to loggers named in text and disposition APIs that log by themselves as one kind.

## Prior finding: resolved

Round 5's four shapes are now refused at this head. `ev/probe_r5.py`, the round-5 reviewer's probe, unchanged (sha1 61ac3f92), gives `typing_get_type_hints`, `inspect_eval_str` and `typing_forwardref` `alias=['"_LOGGER.error(\'x\')"']`, and `pickle_str_payload` `alias=['text sha256:85a2b7af4de92195']` (`ev/probe_r5_f2d2.txt`). Every round-4 route reads its payload constant. The controls are unchanged: `ctl_warning barrier=1 alias=[]`, `ctl_re_compile barrier=0 alias=[]`. `types_functype`, `runpy_module` and `sys_modules_marshal` now read `alias=[]`, where round 5 refused them by import. The body dispositions them: their payload is a parameter, refused where its constant sits. A fullwidth `_ＬＯＧＧＥＲ.error` and a fullwidth `.ｅｒｒｏｒ` method both read `barrier=1`, because the barrier reads the AST and its NFKC names (`ev/probe_r6_f2d2.txt`).

## Evidence

- Mutation: `ev/mutants.sh` edits one predicate of this head's `tests/entities.py` per mutant. `ev/reach_drv.py` then execs the N-log-flood section verbatim, from `from collections import Counter  # noqa: E402` to the next section, under a recording `R`. Unmutated: `ok` for `R10 N-no-expiry barrier`, `R10 N-log-flood barrier` and `R11 N-log-flood barrier reach`. Each mutant prints `FAIL` for the reach check (`ev/mutants.txt`): M1 the constant arm off, M2 the shipped-file arm off, M3 no recursion into front-end output, M4 the name pattern narrowed to `_LOGGER`, M5 `pickletools.genops` off, M6 untracked files read. None was vacuous.
- `git merge-tree --write-tree origin/main f2d21754` at origin/main a8efe1d1 exits 0 (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and `tests/closures.json` are untouched three-dot against the merge base.
- The figures I could not re-derive: `ALL 2737 ENTITY CHECKS PASSED`, `ALL 441 checks PASSED`, `571 passed, 0 failed` and the census `modules 96 str/bytes constants 12522`. These are the fixer's, and the census probe is not in the tree. They are left to CI's runs at this head. The heavy gate was not re-run (tvofi 2026-09-30).
- CI at this head: `merge_train.py classify` printed `WAIT f2d21754... pending: gate red: none` on every run from 16:23 to 16:52 UTC, about 30 minutes, and on the last run (`ev/classify.txt`). No red, so no `## Red checks` answer is owed. The packet's `introduced-red` refusal is the queued `governance / instrument-self-tests`, which is still unconcluded.
- The finder's harness: the packet reads `none named`. This review's harness is a live run with a null control (`ev/run_live_r6*.py`), and it is the reviewer's, disclosed as such.
