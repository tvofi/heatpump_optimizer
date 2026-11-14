Fix review: merge 667fb55efe9791553115d2391b5378341a677fc2

bus-nonce: b077686eb6536e6bbd349ef6323b7b62
pending-ci: gate

## Summary

Round 1 (first round; no reviewed head before this one). This PR is a hotfix for a red main. It re-records `tools/ci/selftest_closures.json` from main run 43632211631's `selftest-closures` artifact and adds its own delivery row. No production line changes: `git diff e901e9ef29...667fb55efe` touches only `dev/programme/delivery/3595.md` and the table. I measured at head 667fb55efe9791553115d2391b5378341a677fc2. `git merge-tree --write-tree origin/main` (d7004eaa77) exits 0, so the head merges cleanly.

## Evidence

- Artifact provenance: I downloaded artifact 14130285894 (`selftest-closures`, run 43632211631 at 4058469d79) myself. Its zip sha256 is 550d20b1…f3b7, which matches GitHub's digest. The unpacked `selftest_closures.json` is byte-identical to the head's table and to the code head 1542231b10's table. The table is the instrument's own `check --write` union output and was not edited by hand. File: ev/artifact.txt.
- Replay proof: I replayed `selftest_scope.drift(table, artifact["steps"], workflow_steps(root))` with my own script, ev/replay.py.
  - RESULT with origin/main's table (merge base e901e9ef29): 13 refusals, all UNDER-SCOPED. This holds whether the workflow is read from the run's tree 4058469d79, the merge base or the head. It matches CI's `116 gated step(s), 13 refusal(s)`.
  - RESULT with the head's table: 0 refusals and 0 notes on every one of those trees, and also on current origin/main d7004eaa77.
  - Files: ev/replay-*.txt.
- Table only adds: I compared the two tables recursively.
  - RESULT: 36 distinct paths added, 0 removed, 0 scalar changes. Top-level keys and step ids are identical. File: ev/table-compare.txt.
  - The 36 match exactly the 36 items that the 13 UNDER-SCOPED lines name.
  - Two body figures are slightly off:
    - "across 13 steps": the 13 refusals fall on 12 steps, because pr-merger has both a files line and a probes line.
    - "added 36" counts distinct paths: the lists actually grow by 49 entries, because of the duplicate entries below (finding 1).
- `python3 -I tools/ci/selftest_scope.py static` at the head prints `116 gated step(s), 0 problem(s)`, which matches the body.
- `python3 tools/ci/selftest_scope.py --self-test` prints `120 checks, 0 failed` at both the head and the code head 1542231b10. The body's figure of `110 checks` does not re-derive at either commit, so I count it as not verified. It is a body-only error, and the result itself (0 failed) holds. File: ev/static-selftest-head.txt.
- Mutation proof (step 1): n/a, because the diff writes no production line. Removing the mechanism (reverting to the base table) brings back the 13 refusals, and the head table gives 0. That is the table's role shown both ways, and it is the step-14 earned-movement check.
- Finder's harness: none is named. The red main run's drift step is the finder, and the offline replay is the only proof a PR run can give, because `SELFTEST_TRACE` is push-only. The first push to main after the merge is what proves it live.
- Claim files: untouched. `VERSION`, the manifest version and the RELEASE_NOTES heading: untouched.
- Forward-carry (step 10): both carries name groups in `dev/programme/rosters/wave-r10-groups.json` on origin/main.
  - R10-SELFTEST-SCOPE-UNION-GUARD is in-progress (#3551). Its brief already states the union `record` and the shrink guard as its own work.
  - R11-SELFTEST-SCOPE-MAIN-UNION-RERECORD is deferred. Its brief already states countermeasure A. The body's dismissal of it as a `Carry:` target is consistent with `prepr`.
- Red checks (step 11): the body answers `governance / instrument-self-tests`, naming the cheaper detector (tracing on PRs) and its standing cost. That check is not in `merge_train.py owed-reds`, so nothing is owed for it.
- CI state at this head: I polled `merge_train.py classify 667fb55efe --pr 3595` from 21:14 to 21:50Z and every run printed `WAIT 667fb55efe9791553115d2391b5378341a677fc2 pending: gate red: none` (the last is in ev/classify-final.txt).
- Live check-runs at 21:25Z:
  - `gate` had a failure of the interim kind: its log says `FAIL run(s) [43640972193] at this head are still being judged; their gate decides`, so it is not a verdict.
  - `tests / nightly-status` failed. It is not in `owed-reds` (ev/owed-reds.txt), so it is neither answered nor a block.
  - Every completed owed context was success: arch-score, budget-raise-gate, codeql (3), env-matrix, policy-docs, wave-script, hassfest, briefs, closure-scope, mutation, validate-hacs.
  - Still running: closures, typing, browser, fast, coverage, arch-instrument and `governance / instrument-self-tests`.
  - No red in owed-reds, so no `## Red checks` answer is owed by this PR. The relay posts this verdict only once CI is green at this head.

## Findings

- Instrument defect: `compact_probes` in `tools/ci/selftest_scope.py` concatenates `collapse(keep)` with the existing `/**` probes without de-duplicating. A committed `D/**` probe plus measured probes under D that re-collapse to `D/**` are written twice. ev/compact-probes-dup.txt shows `compact_probes({a/**,a/x,a/y}, {}, {a/x,a/y}) = ['a/**','a/**']`. This head's table carries 13 such duplicates, across `open-pr`, `pr-args`, `push-names-the-host`, `temp-or-machine-path`, `update-pr` and `policy-lint-mutants`. They are harmless to `covers`/`drift`/`select`, which use set semantics, and a later write de-duplicates them. They are noise in the table's diff, though, and a shrink guard that compares list lengths or multisets would misread them. The fix belongs with the union/guard work in the same file. Carry: R10-SELFTEST-SCOPE-UNION-GUARD
