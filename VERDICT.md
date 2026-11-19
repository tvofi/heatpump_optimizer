Fix review: blocked 8b68ba21b97bea4bf8d0f3acd442640a6e81fd94 class-open: exec, eval and compile are read only as a bare name, so builtins.exec, getattr(builtins, 'exec'), from builtins import exec as run and __builtins__['exec'] each run logger text that neither check reads

bus-nonce: 9f30525c59aac6cfa575d936f0ad719c

Round 4. This delta starts at the last verdicted head, b950a3904dea576c702020b905a68bb574a00f36 (review/3729 fbaf77c4). It covers 4eb8a9bd (the planted round-3 shapes, red), 935610a4 (the repair; both commits edit only `tests/entities.py`), the merge a8483f0e and the main merge 8b68ba21. `review_carry.py b950a390 8b68ba21` prints FRESH-REVIEW. Under fix-review.md, a fourth round means `fixer.md` owes a re-cut.

## Prior findings: all resolved

The round-3 probe (`ev/probe_delta.py`, unchanged from review/3729) was run at this head (`ev/probe_delta_8b68.txt`). Each round-3 shape is now refused:
- `coordinator._LOGGER` and `c._LOGGER`: refused by name.
- `sys.modules[__name__]._LOGGER`: refused by name.
- `globals()['_LOGGER']`: refused as `'_LOGGER'`.
- `exec(...)`: refused as `exec`.
- `warnings.warn`: refused as `warnings`.

The control `ctl_warning` still reads `barrier=1 alias=[]`. The round-2 probe (`ev/probe_shapes.py`) reads the same rows as at b950a390 (`ev/probe_shapes_8b68.txt`). Over the live package, the alias check returns only the allow-listed handover, `coordinator.py:3518 _LOGGER -> super().__init__` (`ev/live_8b68.txt`).

## Block (class-open)

935610a4's docstring names the routes to a logger by another spelling as "a named set". The names `logging`, `logger`, `_LOGGER` and `warnings` are each read "as an attribute or as text". `exec`, `eval` and `compile` are a separate case, because their code "is text this check cannot parse". The `exec`/`eval`/`compile` arm, however, reads only an `ast.Name`: `isinstance(node, ast.Name) and node.id in ("warnings", "exec", "eval", "compile")`. These names are not in `reached`, so neither their attribute spelling nor their text spelling is read.

Each shape below runs `"_LOGGER.error('x')"` as code from a package line. Neither `_r10_unlatched_logs` nor `_r11_logger_aliases` sees any of them at this head: `barrier=0 alias=[]` (`ev/probe_r4.py`, run as `ev/probe_r4_8b68.txt`):
- `import builtins; builtins.exec(...)`
- `getattr(builtins, 'exec')(...)`
- `from builtins import exec as run; run(...)`
- `__builtins__['exec'](...)`

The perturbation moves the harness. The bare spelling `exec(...)` at the same head reads `alias=['exec']` (`ev/probe_delta_8b68.txt`, `exec_string`). None of the shapes is a live site today.

The docstring's "Not read" covers only names computed at run time. These four are static spellings, the same attribute-and-text domain that round 3 opened for `_LOGGER`.

The repair is the fixer's choice. The narrowest one would read `exec`, `eval` and `compile` the way `reached` is read, as an attribute and as text. It would also refuse the module `builtins` and the name `__builtins__`, or state them out of the barrier's scope in the docstring and the body. Each needs a planted shape and a control in the existing reach check. One control to keep is `re.compile`, which an attribute arm on `compile` would refuse; the planted `ok.py` already carries `re.compile`.

## Delta otherwise sound

- The planted shapes in 4eb8a9bd cover every round-3 row. `ok.py` adds a sibling import, `re.compile` and text that only mentions `_LOGGER` and `warnings` as unrefused controls.
- `git merge-tree --write-tree origin/main 8b68ba21` exits 0 (`ev/merge_tree.txt`).
- The three-dot diff has no `VERSION`, manifest, `RELEASE_NOTES.md`, golden or claim file, and no `custom_components/` path.
- The main merges carry no resolution of the PR's own files beyond the base move. The three-dot file set is the same five files as at b950a390.

## Red checks

Read live at 8b68ba21:
- `codeql / Analyze (python)`: cancelled in run 44533636215 (job 135598039222), superseded by a success at this head (job 135701397708). Not this PR's own.
- `pr-contract / pr-contract`: failed (job 135676105145) on the stale `scope-line` figure block and `## Head` line, which the orchestrator fixed by a body edit; the rerun at this head has one success (job 135702661048) and one still running (job 135701333687). The failed job predates the body edit.
- `gate` (jobs 135682420980, 135706662049): `FAIL run(s) [44533511852] at this head are still being judged`, a pending-run refusal, not a verdict on code. It follows the `pr-contract` rerun.
This verdict is blocked on a code finding, not on any red above.

## Notes

- Note: body: `## Head` names a8483f0e as "this PR's head". The live head is 8b68ba21, a `ci: merge main` on it. Carry: R11-SEAM-ratchets

## Finding carries

- class-open (exec/eval/compile by attribute or text, `builtins` and `__builtins__`): Carry: R11-SEAM-ratchets

Evidence is under `ev/`. The probe scripts are this reviewer's instruments, not the finder's: the finding's harness is the planted-shape reach check in `tests/entities.py`, which these probes exec verbatim. CI's heavy runs (mutation, scoped gate) are cited, not re-run.
