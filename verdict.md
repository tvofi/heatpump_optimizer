Fix review: merge a1fa38896bc5d82c4b30e72575a5244a865a64e1

bus-nonce: 748b1f4f94c47d421e70576e4cefcc3a

## Summary

Round 1, full scope. Reviewed head a1fa38896bc5d82c4b30e72575a5244a865a64e1, the one the body names. The diff touches only `tests/replay.py` (`replay_timeout_minutes` and two controls) and its own delivery row. `custom_components/`, VERSION, the manifest version and the notes heading are untouched. No claim files or budgets move. The new regex has one parse per line. I measured it linear, and it reads exactly what the base read.

## Evidence

- CI: `merge_train.py classify a1fa38896bc5d82c4b30e72575a5244a865a64e1 --pr 3941` printed `GREEN a1fa38896bc5d82c4b30e72575a5244a865a64e1 pending: none red: none`, rc 0, on two runs (ev/classify-1.txt, ev/classify-2.txt).
- Red checks: the head's failures, `CodeQL` and `tests / nightly-status`, are not in the `owed-reds` set (ev/owed-reds.txt). They are neither answered nor a block.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, clean (ev/merge-tree.txt). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Mutation proof, re-run by me (driver ev/drv.sh, output ev/mutants.txt, head baseline ev/mut-0-head.txt). Each mutant changed the one production line, then I restored it:
  - Base regex restored: `FAIL control:headroom:cap_read_is_linear read None in 1.310 s`.
  - Third overlapping arm ` *\n` added: `FAIL ... cap_read_is_linear ... 1.619 s`.
  - Tab arm dropped: `FAIL control:headroom:reads_the_replay_job`.
  - The ` {0,3}\n` arm dropped: `FAIL ... reads_the_replay_job read None`.
  - Survivors: ` {0,3}\n` narrowed to ` {0,2}\n` (see Findings), lazy `*?` made greedy (equivalent on any job with one four-space cap line, and the base had the same exposure), and the lookahead `(?! {4})[ \t]*\n` (a semantically equivalent spelling).
- Equivalence: I ran the body's corpus driver from a retyped copy (ev/equiv.py). It printed `corpus 115840 strings, base matched 23265; head disagrees on 0; null control disagrees on 8400`, rc 0, which matches the body. My copy's sha1 is 5a848ebb…, not the body's 25e3d70d…: the copy is retyped and byte-level whitespace differs, so I verified the figure by its output, not its hash. My own random corpus of 200000 strings, including CR, colons and tab/space mixes (ev/equiv2.py), gave `base matched 15017 disagree 0`.
- Real input: on `.github/workflows/tests.yml`, base and head both return span (78958, 79176) and group `60`. This matches the body.
- Null control, at n blank four-space lines with no cap, on this host. Base: 0.010 s (16), 0.039 s (18), 0.145 s (20), 0.606 s (22). That is roughly 2x per line, the body's shape; the absolute times are host-dependent. Head: 0.000 s at each n. Head at 5000 lines: 0.0014 s, and 0.0013 s for 5000 mixed space-tab lines, so the search is linear.
- The new control's 0.25 s bound sits about 5x under the base's time at n=23 on this host and far above the head's. I did not re-take the body's host-specific dst_checks, entities and replay full-script counts; per the contract I cite CI's gate and fast lanes, which are green.
- Disjointness: the four-space arm needs a literal 4-space prefix. ` {0,3}\n` takes a line of at most 3 spaces. ` {0,3}\t[ \t]*\n` needs a tab within the first 4 characters. So no line has two parses.

## Findings

- Residual: the narrowing mutant ` {0,3}\n` → ` {0,2}\n` survives `replay.controls()`, because no control spells a blank line of exactly three spaces. A regression of that shape reads None, which the caller already treats as red, so it fails loud rather than silently. The body's equivalence corpus does cover `"   \n"`. Carry: dismissed: test-strength gap on a test instrument whose failure mode is a visible red, not a silent misread
- Residual: the advisory `CodeQL` check at this head reports "1 new alert including 1 high severity" in code the PR changed. I could not read its annotation without the code-scanning API, so I cannot confirm that alert 69 (`py/redos`) closes. `pr-contract`'s `codescan_wait.py` listing at this head printed `code-scanning alerts the body must answer:` with nothing after it. The linearity itself is measured above. Carry: dismissed: not in the owed-reds set and pr-contract lists no alert at this head; alert 69's closure is read on main after the merge

## Friction

none
