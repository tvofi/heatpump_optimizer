Hotfix (P676, orchestrator go 2026-11-12). `tools/pr/prepr.sh` self-test compared `$(mg status --porcelain | wc -l)` to `0` as a string; BSD/macOS `wc` pads its count, so the arm failed on Darwin since #3455 (536 passed, 1 failed) and every full-prepr open or update from a macOS host was refused. The site now strips the padding with `| tr -d ' '` as its siblings do, and the arm runs under a stub `wc` that pads its count, first on PATH, so the defect is reproducible on Linux.

After the merge the orchestrator removes the local `wc` stopgap shim (marker `hpo-wc-shim`) from its host's instruments bin dir.

Alternatives: a `$(( ... ))` arithmetic wrap was equivalent; `tr -d ' '` matches the sibling sites. The deferred raw-`wc` string-compare lint (P676(b)) is not built here; this is the second Darwin-only prepr self-test red, a third triggers the class barrier.

## Head

1386441425905fd0d7bb0571f1bac61ff5d7777b

## Mutation proof

Deleting `| tr -d ' '` from the arm (the fix) and running `bash tools/pr/prepr.sh --self-test` gave `FAIL and the in-place run leaves the work tree clean, under a wc that pads its count (got        0, wanted 0)` and `537 passed, 1 failed`; restored, the same command gives `538 passed, 0 failed`.

## Null control

The first new arm asserts the stub pads (`printf 'x\n' | wc -l` under the stub equals `       1`), so the second arm is measured under a padding wc; without `tr` it fails as above. Unmodified tree at 6d16af36c2 on Linux: the arm passes because Linux `wc` does not pad, which is why CI never saw it.

## Figures

- Sibling sweep: `git grep -n 'wc -[lc]' -- '*.sh'`, string compares lacking `tr -d` or `$(( ))`, numeric `-ge/-lt` tests excluded: the only site is `tools/pr/prepr.sh` clean-tree arm, fixed here.
- `bash tools/pr/prepr.sh --self-test`: 538 passed, 0 failed at the head above.

## Red checks

none. Disclosure: the local full `tools/pr/prepr.sh` run reported `REFUSE closures: failed while being recorded: tests/entities.py (exit 1)` on this Linux seat; run alone, `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2707 ENTITY CHECKS PASSED` (rc=0) at the same head, so the refusal was the seat's run limit, not the diff. Every earlier step was ok, including self-test 538 passed, 0 failed. The only changed file is `tools/pr/prepr.sh`.

## Forward-carry

none

## Friction

none
