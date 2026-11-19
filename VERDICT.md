Fix review: blocked b950a3904dea576c702020b905a68bb574a00f36 class-open: a sibling module's logger as an attribute (coordinator._LOGGER.error), _LOGGER reached by the string '_LOGGER' (globals(), sys.modules[__name__]._LOGGER), warnings.warn under Home Assistant's captureWarnings

bus-nonce: cfbed55afd7f33d60b3299d08d7eb467

Round 3. Scope: the delta from the last verdicted head, 5fe137027a72cdd44483f1b2ad8c4345bb554857 (verdict/3729 8ebf85a6), to b950a390: d983acca (the class-open repair), ebb5b253 (the row rename) and the main merges ff9cfca0/b950a390. The brief named 86d34e88 as the reviewed head, but no verdict names 86d34e88 (the packet's `## Review scope` reads `full` for that reason), and d983acca, which sits before 86d34e88, had never been reviewed, so the delta starts at 5fe13702.

## Prior findings: all resolved

The round-2 probe (`ev/probe_shapes.py`, unchanged from review/3729), run at this head (`ev/probe_shapes_head.txt`): `log_kw_level barrier=1`; `private_log` refused as `_LOGGER -> _LOGGER._log`; `handle_record` refused as `_LOGGER -> _LOGGER.handle` and `logging.makeLogRecord`; `module_assign_alias` refused as `logging -> Assign`; `walrus_alias` refused as `logging -> NamedExpr`; `getattr_root` refused as `logging -> getattr`; `importlib` and `dunder_import` refused as `'logging'`. Controls are unchanged: `ctl_info barrier=0 alias=[]`, `ctl_warning barrier=1`, `log_pos_level barrier=1`, `import_as_alias` refused as `lg`, `root_direct` refused as `logging.warning`.

## Block (class-open)

d983acca's docstring and the body claim that `_r11_logger_aliases` reads "both surfaces by allow-list, so a spelling nobody listed is refused rather than missed", and that the escape rule is "the only way a logger reaches a parameter, because every other source of one is refused above". The `_LOGGER` arm reads only an `ast.Name` with id `_LOGGER`. The attribute arm reads only the attrs `logging` and `logger`, and the string arm reads only the text `'logging'`. Each shape below logs at WARNING or ERROR from a package line, and neither check sees it at this head (`ev/probe_delta.py`, which execs both functions verbatim from `tests/entities.py` over `import logging; _LOGGER = logging.getLogger(__name__)` plus the shape; output `ev/probe_delta_head.txt`). The same rows read the same at 5fe13702 (`ev/probe_delta_5fe1.txt`), so these sit in the domain of the predicate this delta rewrote. They were not introduced by it. None is a live site today (`ev/live_grep_delta.txt`: the only hit is `__init__.py:121 globals()[name] = value`, which stores a value and logs nothing).

- `from . import coordinator` then `coordinator._LOGGER.error('x')` (also `from . import coordinator as c; c._LOGGER.warning('x')`): barrier=0, alias=[]. Another module's logger, reached as an attribute, is the plainest sibling of the `from .coordinator import _LOGGER` import that the check already refuses. The barrier keys on `unparse(func.value)` being `_LOGGER`, and `coordinator._LOGGER` matches neither check.
- `sys.modules[__name__]._LOGGER.error('x')` and `globals()['_LOGGER'].error('x')`: barrier=0, alias=[]. These reach the module's own logger by an attribute or by the string `'_LOGGER'`. That is the `_LOGGER` counterpart of the `'logging'` string arm this delta added.
- `import warnings` then `warnings.warn('x')`: barrier=0, alias=[]. Home Assistant turns on `logging.captureWarnings(True)` at startup, so this lands as a WARNING record on the `py.warnings` logger, a package line logging through something other than `_LOGGER`. If the barrier deliberately leaves this out (the warnings filter's per-location dedupe acts as a partial latch), say so in the docstring and the body.
- `exec("_LOGGER.error('x')")`: barrier=0, alias=[]. This is the same class as the computed module name the docstring already names as unread. Naming it there next to `import_module('log' + 'ging')` is enough.

The repair is the fixer's choice. The narrowest one would refuse an `ast.Attribute` whose attr is `_LOGGER` and a string constant `'_LOGGER'`, and would either refuse `warnings` (the module name, or the text `'warnings'`) or state it as out of the barrier's scope. Each repair needs a planted shape and a control in the existing reach check, as d983acca's shapes have.

## Delta otherwise sound

- ebb5b253 renames `unused_package_imports` to `unloaded_package_imports` in `tests/structure.py` (definition comment, function and RESULT key), in the budget row and in the `field_coverage.mjs` census. The value (14) and the rule do not change. The three-dot budget diff adds two keys at their measured values and changes no existing key (`ev/budget_diff.txt`). The rename is the only route under the base-pinned census registry, as the body's Red checks set out. What it gives up (the registry no longer demands the census) is carried by the body to round-end instrument triage. It is not metric-gamed: no number moves, and the census stays registered and is run (`censusRun` iterates every `CENSUSES` entry).
- The merge resolutions: `tests/structure_budgets.json` takes main's `duplication_copies` 7 beside this PR's two rows. `git merge-tree --write-tree origin/main b950a390` exits 0 (`ev/merge_tree.txt`).
- `python3 tests/structure.py` at this head did not finish within 250 s on a loaded host, so I have no figure of my own for it. The body's ff9cfca0 figures (`in_function_copies 11 <= 11`, `unloaded_package_imports 14 <= 14`, `duplication_copies 7 <= 7`) are cited, not re-derived, and CI's scoped gate at this head is the record.
- No `custom_components/`, `VERSION`, `RELEASE_NOTES.md` or golden or claim file is in the three-dot diff.

## Red checks

At b950a390 no check run has concluded red (`ev/checks.txt`: everything is either success, skipped, CodeQL neutral, or still queued or in progress, including `policy-docs`, `env-matrix`, `mutation` and `closure-scope`). The body's `## Red checks` answers every earlier owed red: `policy-docs` and the `gate` derived from it, with the cheaper detector named (the base's pinned `field_coverage.mjs` run at the head), and the `env-matrix` cancel. Nothing at this head is left unanswered. This verdict does not turn on CI.

## Notes

- Note: body: `## Head` carries a stale line, "`bc4b90f5ed6e...` merges the authored code head ff9cfca0", beside the correct b950a390 line. Carry: R11-SEAM-ratchets
- Note: scope: the dispatch brief named 86d34e88 as the delta base, but that is no verdicted head, so the delta was taken from 5fe13702 as fix-review.md step 12 defines it. Carry: dismissed: a scoping correction within this review, nothing owed later

## Finding carries

- class-open (sibling `_LOGGER` attribute, the `'_LOGGER'` string reach, `warnings.warn`, and `exec` named as unread): Carry: R11-SEAM-ratchets

Evidence is under `ev/`. The probe scripts are this reviewer's instruments, not the finder's. CI's heavy runs (mutation, scoped gate) are cited, not re-run.
