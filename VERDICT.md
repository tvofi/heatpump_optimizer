Fix review: merge 87d3a6f45eec23cee45ead473166ba9db5ad486e

bus-nonce: 3ddc3b46ad75638e55bcd4addda1a9b0

## Scope

First round, full review, at head 87d3a6f45eec23cee45ead473166ba9db5ad486e. This head is still the branch tip, read back by ls-remote before the push. The role contract matches main: the three-dot diff over dev/governance/roles/ is empty. The diff is tests/entities.py (+70/-5) and dev/programme/delivery/3579.md. No production code, VERSION, manifest, notes heading, claim files, budgets, closures.json or INERT are touched.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 87d3a6f4` exits 0. origin/main is 8af37bdf44 and the head merges cleanly (ev/merge-tree.txt).
- RESULT CI: `merge_train.py classify 87d3a6f4 --pr 3579` printed `GREEN 87d3a6f45eec23cee45ead473166ba9db5ad486e pending: none red: none` at 02:37:40 UTC (ev/classify.log). The packet's `gate` failure and `introduced-red` refusal were read before the runs concluded, and classify supersedes them. No required check is red, so no `## Red checks` answer is owed.
- RESULT head run: `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head gives `ok` for all three checks this PR touches: the location is redacted whole; the search ignores a clock reading that contains a rounded coordinate; a coarsened coordinate still fails the clock-free search. The total is 2713, which is 2711 + 2 new checks (ev/entities_head.log).
- The local run exits 1 with 2 failures, and neither is this PR's.
  - The every-script-once budget failure (count 56 vs 54) came from my two untracked mutant copies in tests/.
  - `pages.yml is not a gate file, and is classified` depends only on tree content this PR does not touch, so it is the same at the merge base.
  - CI's `tests / fast (3.14)` is green at this head.
- RESULT mutation proof, re-run:
  - mut1 (`_clockless` returns `a` unchanged, the body's mutant): FAIL `the rounded-coordinate search ignores a clock reading that contains one` (ev/mut1.log).
  - mut2 (`_rounded_hits` returns []): FAIL `a genuinely coarsened coordinate in the payload still fails the clock-free search` (ev/mut2.log).
  - Both were restored. The other failures in those logs are closure-instrument checks reacting to the untracked mutant files, which show up in the diff against the head log.
- RESULT null control: the poisoned-clock check asserts that the whole-blob search hits at 2026-01-05T03:04:18.100000Z, so the old flake reproduces deterministically and the new search clears it. The coarsened-probe control is shown killing mut2 above.
- The clock pin follows the file's own pattern: every earlier `dt_util.freeze(x)` in entities.py is released with `freeze(None)` at module level, so `_diag_payload_at` clobbers no outer freeze.
- Harness: this hotfix names no finder's harness. The deterministic reproducer, the poisoned-clock check, is the fixer's own and is committed in the same script. It is disclosed as the fixer's, not the finder's.
- Figure not re-derived: the body's "1 of 2711 on main at 50373173" is a CI run on main that I did not re-run. The body marks the chance-match mechanism as an inference. The head total of 2713 is consistent with it.

## Findings

- Residual: `_clockless` drops every leaf, and every list whose length differs, between the two pinned clocks. A coordinate leaked inside a clock-dependent value would be masked from the rounded search, for example a string that also carries a timestamp, or a list whose length depends on time. I did not measure how much of the payload is dropped. The whole-redaction asserts on config/config_setup and the a10:no_precise_location check still stand. Carry: dismissed: the narrowing is the minimum that removes the clock-dependent false positive; precise and whole-field redaction stay asserted by other checks, and I did not show a clock-dependent leaf that carries a coordinate (unmeasured, not shown absent).

## Friction

- The frugal inline-read guard refused reading the head log during the review, so the mutant runs were delegated to a scout seat.
