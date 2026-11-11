Fix review: blocked 0740542f38ffb23e273bf91fd128aa2469d9a120 mutation-vacuous: note-replayed, run's replay flag into sizes_provenance is unpinned

bus-nonce: 04cbf47207f7a9f4794d123bdb159a3f

Round 4 is a delta re-review of 95c04821e5..0740542f38. I measured head 0740542f38ffb23e273bf91fd128aa2469d9a120 from a detached worktree. It was still the PR head when this verdict was written (ev/head-at-verdict.txt). The body carries a `## Re-cut` that states what was cut ("nothing") and what was added (the injection of `reads` and `roster_file` into `run`, and the two arms). The delta diff matches that account. No other behaviour changed: the defaults `reads=READS` and `roster_file=None` keep `run`'s callers' behaviour.

## Block

Round 3's three survivors are now killed: `note-run`, `run-via` and `replan-via`. One mutant on the same provenance line still survives:

- `note-replayed`: in `size_durations.run` (tools/plan/size_durations.py:851), `input_note(via, since, len(prs), replayed)` becomes `input_note(via, since, len(prs), False)`, and `size_durations.py --self-test` stays at 0 failed. A run from `--prs-cache` then states "read by size_durations.fetch_rest (--via rest)." with no ", replayed from a --prs-cache file.", which is a false provenance. The mutant is not equivalent, because `input_note` changes its text on that flag. `read-replay` is killed, so `read_prs`'s own flag is pinned, but `run` forwarding it is not: the new arm drives `run` with `cache=None` only. The body's `## Unpinned sites` does not list it, and diff mode cannot generate it, because the line is not an added line of this round's delta.

Fix: add one call of the existing arm with `cache` pointing at a fixture `--prs-cache` file. Assert that `sizes_provenance` ends with `input_note(<via>, since, n, True)`. The current `cache=None` runs are its null.

## Findings

- Residual: the survivor `note-replayed` (the block above): `size_durations.run` hands `replayed` to `input_note` with no arm reading it. Carry: dismissed: this PR's own block, to be settled in this PR's next round
- Follow-up: the test-side mutant `replan-cap` (`unset = ("live_remaining_fraction",)` to `unset = ()`) still survives at this head, as round 3 recorded. Carry: dismissed: test-side only, and the production defaults are pinned, as round 3 dismissed it

## Evidence

- RESULT round-3 named mutants, run through tools/audit/seat/mutant_run.py (ev/spec-sd3.json, ev/mutants-sd3.txt, FAIL lines in ev/sd3-fails.txt). NULL SURVIVED, with 0 failed. `note-run` is KILLED, with `FAIL run --via rest: sizes_provenance ends naming fetch_rest` and `FAIL run --via graphql (null): sizes_provenance ends naming fetch`. `run-via` (`read_prs(reads, "graphql", ...)`) is KILLED, with `FAIL run --via rest: the rest read builds the PR list`. `note-replayed` SURVIVED. These match the body's Mutation proof.
- RESULT replan mutants (ev/spec-rp.json, ev/mutants-rp.txt), `replan.py --self-test`. NULL SURVIVED. `replan-via` (drop `args.sizes_via`) is KILLED. So is my added `replan-via-const` (pass `"graphql"`). `replan-cap` SURVIVED, a test-side mutant, see Findings. The body quotes the `replan-via` FAIL text, `['graphql', 'graphql']`. That matches the stub's default reading.
- RESULT size_durations mutants (ev/spec-sd.json, ev/mutants-sd.txt). `note-run`, `run-via`, my added `note-via` (`input_note("graphql", ...)`), `note-count` (n set to 0), and round 3's `rest-short`, `rest-since`, `rest-merged`, `rest-first` and `read-replay` are all KILLED. `note-replayed` SURVIVED.
- RESULT round-2 hot-* mutants (ev/spec-pp.json, ev/mutants-pp.txt), `plan_page.py --self-test`. NULL SURVIVED. `hot-render`, `hot-gates`, `hot-notdone`, `hot-dis`, `hot-crit`, `hot-title`, `hot-allrows` and `hot-nothotfix` are all KILLED.
- RESULT self-tests at head, unmutated (ev/selftests.txt). `size_durations self-test: 0 failed`. `plan_page self-test: 93 checks, 0 failed`. replan passes as the NULL of ev/mutants-rp.txt.
- Step 13: `git merge-tree --write-tree origin/main 0740542f38` exits rc=0 with no conflict, against origin/main cbd23f1c8b (ev/merge-tree.txt).
- Step 5 and step 14: the three-dot diff touches no VERSION, manifest, release-notes heading, budget, claim, golden or closures file.
- Step 11: `pr-contract / pr-contract` is red at this head (job 130477101092). It fails with the same `AttributeError: module 'roster_lib' has no attribute 'carry_receivable'` that the body's `## Red checks` answers. `git grep "def carry_receivable"` finds it at origin/main and not at the head (ev/carry-receivable.txt). `tests / nightly-status` is red, but it is not in `owed-reds` (ev/owed-reds.txt). `gate` reads failure in the digest. `merge_train.py classify` prints `WAIT ... pending: gate red: none` from 10:58Z through 11:05Z (ev/classify-poll.txt), so `gate` is pending and owes no answer yet. This block does not depend on CI.
- I did not re-run diff mode, so the body's figure of 21 survivors is not re-derived here. `durations.json` was not re-measured in this pass, as the body says.
- Finder's harness: none. This is an instrument group fed by roster carries, as recorded in round 3. Carry: dismissed: evidence, not a finding
