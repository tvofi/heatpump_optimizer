Fix review: merge 1d54b05d50f947cd40dbf3559c73ffcb18e5c299

bus-nonce: c557031c0abcdbe98413fd5f1a78c10c

Round: second review of #2557 (R10-RCA-ORCH-CONTINUITY). Round 1 (comment 6326878220, at 7e312ed2e) was blocked carry-missing. Reviewed at head `1d54b05d50f947cd40dbf3559c73ffcb18e5c299`, from a detached worktree at that SHA. `fix-review.md` is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

- The body's roster paragraph says `7213e761e` "appends the same line again" to R10-ORCH-MACHINERY. That does not re-derive. At `origin/handoff/audit-r10-roster` `545184b96` and at `e2bb0e7ac`, R10-ORCH-MACHINERY has exactly 1 carry citing #2557, out of 23. `7213e761e` re-serialises that line (a trailing-comma diff) while it appends #2558's carry. This is a mis-description in prose and changes no routing. Carry: dismissed: prose only, routing unaffected (item f1)

## Evidence

- Head: `ev/HEAD.txt`. The PR's REST head and the body's `## Head` both name `1d54b05d50f947cd40dbf3559c73ffcb18e5c299`. Its parents are 7e312ed2e (the round-1 head) and 2f171454d (the round-2 commit). `git diff 2f171454d 1d54b05d50f947cd40dbf3559c73ffcb18e5c299` is empty (`ev/resolution-delta.txt`), so the merge commit has no resolution delta of its own. The round-2 delta against 7e312ed2e is exactly two files: `carry-201.json` (+2 carries, `stage` text) and `pulse.py` (+2 lines, one self-test fixture, no production line). This matches the body.
- Merge: `git merge-tree --write-tree origin/main 1d54b05d50f947cd40dbf3559c73ffcb18e5c299` against origin/main `5a755f53e` exits 0. The driver line is `LEDGER-MERGE: resolved tests/closures.json`, a set merge of `inert_reads`, and no path conflicts (`ev/merge-tree.txt`).
- (1) Carries:
  - `carry_audit.py check --body <body>`: `5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, exit 0. The same holds with `--roster-ref origin/handoff/audit-r10-roster` (`e2bb0e7ac`). See `ev/carry-audit-body.txt`.
  - On the roster at that ref, R10-ORCH-MACHINERY and R10-RCA-HANDOFF-SLIP each carry one line "From #2557 ...", and each states its control as a fixture or replay precondition.
  - Both `#201` carries are now the last two entries of `dev/programme/carries/carry-201.json`, each with from, effect, control (with null control), remeasure and brief. That settles round-1 f1.
  - `brief_lint.mjs` reads that section as 0 error(s), 0 warning(s). It holds 19 carries at the head and 17 at merge base `1ebc737e7`, which matches the body.
- Round-1 findings are settled:
  - f2: the 0012 sentence is reworded to cite the revocation (#201 comment 6322712314).
  - f3: the body's carry-audit figure now reads 5 routed, which re-derives.
  - f4 (surviving mutant R11): it now has fixture M8.
  - The round-1 unverifiable `p90 19.2 min` is gone from the body. The 198/215 and 49.2 min figures stand, as re-derived in round 1.
- Mutation proof at this head (`ev/mutants.txt`):
  - M0 (null): 22 checks, 0 failed.
  - M8 (drop `or o.get("rc") not in (0, 1)`): 21 checks, 1 failed, "bus.sh rc 2 or more is UNREADABLE even beside a summary line".
  - M1 (`if True:`): 4 failed, the four the body names.
  - No production line of `pulse.py` changed since round 1, so its M2–M7 and R8–R14 results carry.
- Figures re-derived at this head (`ev/lints.txt`, `ev/pulse-selftest.txt`):
  - `pulse.py --self-test`: 22 checks, 0 failed.
  - `selftest_wiring.py --check`: 39 self-testing, 39 wired, 0 unwired.
  - `fold_ledger.py check`: 0 violation(s).
  - `tmp_paths.py --check`: 0 refused.
  - `policy_lint.mjs --pr-body <body> --red nightly-status`: 0 error(s).
  - `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff.
- Not re-derived from this seat in this round:
  - The scoped-gate counts. These are CI's heavy runs: `closure-scope`, `fast (3.14)` and `instrument-self-tests` concluded success at this head.
  - The `failure_logs.sh` exit-2 measurement.
  - The #201-based idle hours. Round 1 judged that the cost test holds under any of them.
- (2) Root-cause record: unchanged since round 1, which checked it against `root-cause.md`. It has a named cause, process state (a), a six-consumer class search, a cost test with numbers (3.0 h/day against 3.3 min/day), and the detector `pulse.py`. That detector's demonstration fires on the original instance: the self-test's "the 10-21 shape" fixture (blocked #2527 verdict, 7.7 h) reads STOPPED, and the replay's 25+37 windows. It has a null control: the healthy fixture reads ok, and the null-bound replay reads 0 windows. The barrier is correctly an owner's call, now carried to #201.
- (3) CI at this head (`ev/check-runs.txt`, check-runs API, 42 runs):
  - The one red is `nightly-status`, from scheduled run 39563978649 (`slow`, `mutation-nightly`) on main `c77f89d`. That is the same run, failing the same lanes, that `## Red checks` answers, with a cause, the fix for `slow` (#2548) and the owner for `mutation-nightly`. Its log on `main-protect` says this check is not a required context and does not block.
  - Both `pr-contract` runs at this head concluded success, the later one at 22:10:34Z.
  - `coverage` and `Analyze (python)` were still in progress when read. No other run is red.
