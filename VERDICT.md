Fix review: blocked 5fe137027a72cdd44483f1b2ad8c4345bb554857 class-open: _LOGGER.log(level=...) keyword level, logging module rebound by assignment or walrus, _LOGGER._log and _LOGGER.handle, reflective logging lookups

bus-nonce: b26c827b094eb5d819307bd30c382291

Round 2 (over reviewed head fc2daf48862599bb19f70ff563db63e347bdf2e7). The packet's `## Review scope` reads `full` (no verdict on verdict/3729 names fc2daf48), so the whole three-dot diff against ae0ed64af898d8923ac35afe6e9c031ac1e6b111 was reviewed, and the round-1 shapes the body lists were re-checked as closed.

## Block

The body claims `_r10_unlatched_logs` counts "every `_LOGGER` call at WARNING or above" and that `_r11_logger_aliases` refuses "every way a package line can log through anything else". Each shape below logs at ERROR or WARNING through the package and is seen by neither check at this head (both functions exec'd verbatim from `tests/entities.py` at head, over `import logging; _LOGGER = logging.getLogger(__name__)` plus the shape; `ev/probe_shapes.py`, output `ev/probe_shapes_head.txt`). None is a live site today (`ev/live_grep.txt` empty), so each is the predicates' unguarded domain (fix-review.md step 6), not a site.

- `_LOGGER.log(level=logging.ERROR, msg='x')`: barrier=0, alias=[]. `flood_level` returns False when `call.args` is empty, so a keyword `level=` is read as quiet. Control: the positional `_LOGGER.log(logging.ERROR, 'x')` reads barrier=1. This is in the PR's own new `.log` predicate.
- `lg = logging` then `lg.warning('x')` (and the walrus `(lg := logging).warning('x')`): barrier=0, alias=[]. The binding rule refuses `import logging as lg` (control: alias=['lg']) and `logging.warning` (control: alias=['logging.warning']), but not a name bound to the `logging` module by assignment, which the docstring's "a name bound ... to a ``logging`` alias" claims.
- `_LOGGER._log(logging.ERROR, 'x', ())` and `_LOGGER.handle(logging.makeLogRecord({'levelno': 40}))`: barrier=0, alias=[]. The alias check admits every `_LOGGER.<method>(...)` call and the barrier counts only the level-named methods, so the record-path methods log at any level unseen.
- `getattr(logging, 'warning')('x')`, `__import__('logging').warning('x')`, `importlib.import_module('logging').warning('x')`: barrier=0, alias=[]. A root-logger call reached reflectively. (`getattr(_LOGGER, 'warning')` is refused, as `_LOGGER -> getattr`.)

The repair the class needs is the fixer's choice; the narrowest reading would count a `level=` keyword in `flood_level`, refuse any binding whose value is the Name `logging`, refuse `_LOGGER.<attr>` for an attr outside the public level/`isEnabledFor`-style allowlist, and refuse `logging` or the string `'logging'` reaching `getattr`/`__import__`/`import_module`; or state, in the body and the docstring, which of these the barrier deliberately does not cover and why. Each needs a planted control in the existing checks, as round 1's shapes got.

## Evidence

- Finder's harness `logflood_shape.py` (sha1 ef9a2072891916165b2096e6613d0d4637ad6dfd, from `git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75`), `PYTHONPATH=tests/hastub`: base ae0ed64a barrier_sites_baseline=71, counted_exception=0, counted_critical=0, counted_log_level=0; head barrier_sites_baseline=72, counted_exception=1, counted_critical=1, counted_log_level=1; counted_warning=1, counted_alias=0 and live_blind_sites=1 at both ends. Matches the body (`ev/logflood_both.txt`).
- Finder's harness `m1_ratchet_census.py` (sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b): unperturbed base and head unused_package_imports=14, in_function_copies=6, duplication_copies=8, recount_mismatches=0, ratchet_rows_off_budget=0; `--perturb unused-import` base off-budget 0, head 1 (`unused_package_imports 14->15`); `--perturb clone-same-fn` base off-budget only `dead_top_level_symbols 1->2`, head adds `in_function_copies 11->12`. Matches the body (`ev/census2_base.txt`, `ev/census2_head.txt`).
- `python3 tests/structure.py` at head: `in_function_copies=11`, `unused_package_imports=14`, `STRUCTURE RATCHET PASSED` (`ev/structure_head.txt`). The budget diff adds two keys at their measured values and moves only `recorded_at`; no existing key changes.
- Targeted mutants (mine, `ev/mutant_probe.py`, `ev/mutants_targeted.txt`): reverting `flood_level`'s method tuple to `("warning", "error")` makes the planted `levels.py` exc/crit/warn_alias sites unseen ({}), so the R10 check's `all(...)` fails; disabling the `_LOGGER` escape rule (`elif False:`) makes the planted `param.py` handover unrefused ([]), so the R11 planted-set equality fails. The body's M1-M5, E1-E4 and R1-R6 were not re-run in full; CI's heavy runs are cited, not re-run.
- `git merge-tree --write-tree origin/main 5fe13702...` exits 0: merges cleanly (`ev/merge_tree.txt`).
- `VERSION`, `RELEASE_NOTES.md`, `custom_components/` and `tests/golden/` are untouched in the three-dot diff (`ev/untouched.txt` empty), so env_drift and the claim files have nothing to compare.
- CI at this head: `merge_train.py classify` printed `WAIT 5fe137027a72cdd44483f1b2ad8c4345bb554857 pending: gate red: none` on every read (`ev/classify.log`); the block does not turn on CI. The owed red at fc2daf48 (`governance / policy-docs`) is answered in the body's `## Red checks` with its cheaper detector named.
- The body's `## Head` names 5fe137027a72cdd44483f1b2ad8c4345bb554857, the head reviewed.
- Probe and mutant scripts under `ev/` are this reviewer's instruments, not the finder's.
