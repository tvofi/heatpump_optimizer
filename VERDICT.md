Fix review: blocked 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9 dropped-entries: the re-record replaced 16 entries and dropped 9 live path entries and 2 objects flags that the merge base recorded

bus-nonce: 7f488e9cfb81a64ca599531388fe0267

Round 1 (first review of this PR). Measured head: 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9, merge base e4ca2d940efd1e87912d80cb3ebddf8240ba0729.

## Block

1. Dropped entries (the dispatch's check 1). I compared tools/ci/selftest_closures.json at the merge base and at the head, per step and per dimension (ev/dropped-entries.txt). These entries are present at the base, absent at the head, and name paths that still exist in the tree at the head. The head does not cover any of them under `covers()`:
   - ci-predictor files `dev/programme/rosters/wave-r10-groups.json`; probes `dev/programme/rosters`; dirs `dev/programme/rosters`
   - verdict-bus files `dev/programme/rosters/wave-r10-groups.json`; probes `dev/programme/rosters`; dirs `dev/programme/rosters`
   - prepr files `.gitattributes`, `tests/env_drift.py`, `tools/merge/ledger_merge.py`
   - dependency-graph-census `objects` true -> false; throwaway-git-helper `objects` true -> false. These are not path entries, but drift() refuses them as UNDER-SCOPED if main reads the object store again, and selection narrows for both steps.
   - Excluded from this block: `git` entry `?` was dropped from dependency-graph-census, temp-or-machine-path and throwaway-git-helper. It is not a path.
   Why the drops happened: the body's method was "only the entries whose measurement was not a subset of the committed one were replaced". That replaces each of the 16 entries with a single recording, which is the replace-not-union pattern behind the drops in #3409, #3419 and #3506. The three prepr files are exactly the reads a CI run on main measured before (the R10-HOTFIX-SELFTEST-SCOPE-UNION brief on the roster quotes them). My own record of prepr on this seat did not read `.gitattributes` either, so the read depends on the seat and main will measure it again. The body also says itself that review-packet read wave-r10-groups.json in only one of its two recordings, yet ci-predictor's and verdict-bus's reads of that file were not kept.
   Remedy: restore every listed entry, i.e. union the base entry with the new measurement for each of the 16 steps. Re-run the comparison above, which should print no DROPPED line for a live path or a flag.
2. Root-cause trigger answer (the dispatch's check 3) is incomplete. `## Red checks` names one merge, as `74fd1a9a49`. That is a merge of main into the fix/r10-mach-scorecard branch, not main's merge; main's merge is e4ba9412b2 (#3502), which added tools/audit/seat/scorecard.py. The body names no merge for the other unrecorded reads, and `git log --diff-filter=A` attributes them:
   - docs/design/2026-11-10-duty-switch-restart-learning and tests/mutation_ledger/{killed_by,survivor_triage}/duty_switch.py: #3461 (005eed2573)
   - dev/audit/rounds/round10/protection-census: #3503 (4869f1656b)
   The answer to the cheaper-detector question is present ("none that stays cheap", with a cost of about 30 minutes for a per-PR strace), so step 11 of fix-review.md is answered. The orchestrator's check asked for the merges, though, and the body names only one, under the wrong SHA.

## Evidence

- Refusals answered (the dispatch's check 2). `python3 -I tools/ci/selftest_scope.py --self-test` at the head printed `selftest_scope self-test: 117 checks, 0 failed`. This host has strace, so I ran `record --step prepr --step field-coverage --step beatd` at the head: 0 failed, 0 broken traces; prepr took 771 s (ev/record-3steps.log, ev/record-3steps.json). `check` needs a trace directory and record deletes its traces, so I applied the module's own `drift()` to that measurement instead. Against the head table it printed 0 refusals for all three steps. As a control, against the merge-base table it printed 4 refusals: field-coverage misses scorecard.py and scorecard_selftest.py, prepr misses 4 dirs, beatd misses probes `<string>` and `beatd.py`, and beatd reads the objects (ev/checks.txt). For those three steps the head answers the refusals. I did not re-measure the other 13.
- Forward-carry (the dispatch's check 4). Group R10-SELFTEST-SCOPE-UNION-GUARD is on origin/handoff/audit-r10-roster at 9e7bdd2d42e4cabe1b6ddb1bb095a28a60359625, with after: R10-HOTFIX-SELFTEST-SCOPE-RERECORD. Its brief makes record union. carry_audit at the head: 1 item, routed. The body's `## Head` records that the orchestrator re-routed it.
- `git merge-tree --write-tree origin/main 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9`: rc 0, no conflict.
- VERSION, the manifest and the RELEASE_NOTES.md heading are untouched. The three-dot diff is tools/ci/selftest_closures.json and dev/programme/delivery/3535.md only.
- Mutation proof: n/a as the body states, because the diff writes no production line. The drift control above stands in for it.
- Figures: the body's `## Figures` is none. I re-derived "16 entries changed" and "98 of 114 byte-identical": 16 steps differ, the other 98 are identical.
- tests/entities.py: not run. With `env -u BASH_ENV` under /opt/hpo/venv-ci/bin/python3 it fails at import with `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py:29. That is an environment fault on this seat, not a finding about the head.
- CI: `merge_train.py classify 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9 --pr 3535` printed `WAIT ... pending: gate red: none` on two runs. Because the verdict is a block I did not wait further.
