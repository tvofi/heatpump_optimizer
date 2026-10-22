Fix review: merge caac2c8dfb338b316803b94ba1df13aff02647e0

bus-nonce: 8e37cf7e0725edace0214e6642ad697b

## Round

This is round 7 overall. It re-reviews the moved head caac2c8dfb338b316803b94ba1df13aff02647e0 after round 6 blocked 056776d8 with contract-red. That head is a main absorb: a merge of 056776d8754930075a030426dd807208e0fd2bc3 and origin/main 16a8240f1. The absorb resolved one conflict by hand, so this round judges the resolution delta and re-takes every measurement. No round has blocked on code. The two blocks so far were on the forward-carry and on the body's carry routing.

## Findings

- R10-ORCH-MACHINERY still has to receive this PR's `ROSTER-APPEND R10-ORCH-MACHINERY` text as one new `carry` entry, landed by the orchestrator with roster_edit.py. The text says the beat's handoff job reads `<state>/cloud-handoff-hold` only through `cloud_relay.sh held <pr>`: rc 0 skip, rc 1 proceed, rc 2 refuse the whole pass. It gives a control, a null control, a malformed control and a mutant. The group is live (`not-started`) on origin/main, at this head and on origin/handoff/audit-r10-roster e5d5c508. Its brief plus carry still holds 0 matches for `cloud_relay\.sh held|cloud-handoff-hold|malformed`, which is the body's own null control (ev/carry-audit.txt). Carry: R10-ORCH-MACHINERY
- R10-FLOW-ROSTER-FREEZE still has to receive this PR's `ROSTER-APPEND R10-FLOW-ROSTER-FREEZE` text as one new `carry` entry. It sets the precondition for the hold-file grammar: plain PR-number lines only, remove only your own line, read back only through `cloud_relay.sh held`. One malformed line refuses the whole handoff arm (rc 2, `OWED <utc> handoff-hold-malformed <file> -` in <log>.level). The control is the self-test's nine malformed variants, which I confirmed at cloud_relay.sh:498 at this head. The null control is `a well-formed hold file owes no refusal`. The group is live (`not-started`) on origin/main, so CI's in-tree carry_audit now accepts it. Its brief plus carry still holds 0 matches. Carry: R10-FLOW-ROSTER-FREEZE

## Evidence

- RESULT head: I measured caac2c8dfb338b316803b94ba1df13aff02647e0 from a detached worktree. Before writing, the PR API head.sha and `git ls-remote origin refs/pull/2580/head` both printed this SHA. The body's `## Head` names it. Parents are 056776d87 and 16a8240f1. ev/HEAD.txt.
- RESULT roles: `git diff $(git merge-base origin/main H)...origin/main -- dev/governance/roles/` prints 0 lines, so the contract is current. The merge base is 16a8240f1. origin/main is at b787c7d45 (`ci: record nightly kills`), one commit past it.
- RESULT prior block cleared: #2588 (0d50ed2de) is an ancestor of both origin/main and this head. CI-mode carry_audit (in-tree roster, no --roster-ref) prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0. With `--roster-ref origin/handoff/audit-r10-roster` (e5d5c508) it prints the same, rc 0. Null control: renaming the ORCH carry to R10-NO-SUCH-GROUP gives `BAD-DEST ...`, `1 routed, 0 unrouted, 1 bad destination(s)`, rc 1. CI's pr-contract at this head ran twice and succeeded both times (jobs 119684743532 and 119684928263). Its log shows that same CARRY-AUDIT line, `PR-BODY: 0 error(s)` and `FIGURES: 11 resolved, 3 not verified, 0 refused`. ev/carry-audit.txt.
- RESULT conflict resolution in dev/audit/harnesses/r10_seat_selftests_mutants.py: I parsed the MUTANTS list with ast at each commit. It has 46 ids at 056776d8, 41 at 16a8240f and 52 at this head. Union minus head: none. Head minus union: none. Duplicates: none. Every tuple at the head is byte-equal (ast.unparse) to its source side's tuple. So cloud_relay-1..11 and tick_loop-1..2 plus heartbeat-1..4 are all present, and nothing was dropped or altered. ev/mutants-union.txt.
- RESULT auto-merged files: for cloud_relay.sh, INSTRUMENTS.md and dev/programme/delivery/2580.md, main's changed lines (merge-base→16a8240f) equal 056776d8→head. The PR's changed lines (merge-base→056776d8) equal 16a8240f→head. Both sides carry intact. ev/automerge-sides.txt.
- RESULT diff beyond the PR's own change: `git diff 16a8240f caac2c8d` touches only the PR's 4 files, +134/-4. Its changed lines differ from the PR's own diff at 056776d8 by exactly one docstring line. That line adds `cloud_relay-N` to `the per-file ids (tick_loop-N, heartbeat-N)`, which the body's `## Main absorb` discloses. Nothing else came in. ev/own-diff-changed-lines-delta.txt, ev/diff-main-head-stat.txt.
- RESULT finder's harness (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, no names, every mutant), at both ends:
  - At the head: 59 `: KILLED`, `M0: 0 seat step(s) red`, `RESULT survivors=0`, rc 0, 0 NOT RUN.
    - The per-row self-test failures for cloud_relay-2..11 are 36/49/2/3/18/2/1/1/27/1. cloud_relay-1 died on the self-test's `updated` file. tick_loop-1..2 and heartbeat-1..4 are KILLED.
    - This matches the body's `## Main absorb` (59) and `## Mutation proof` rows. ev/harness-head.txt.
  - At the baseline 16a8240f: 48 KILLED, `M0: 0 seat step(s) red`, `RESULT survivors=0`, rc 0. cloud_relay self-test there prints `81 checks, 0 failed`, so it has no hold.
    - The body's null-control figures (42 KILLED, survivors=1 from a ref_privacy host red) were taken at the older main 93e6a63d2. At 16a8240f, ref_privacy judges only lines since 383bca2be and prints `0 refused`. The six extra rows are main's tick_loop/heartbeat mutants.
    - The body's figure was re-derived at its stated SHA in round 6 and is not re-derivable at today's base. ev/harness-main-16a8240f.txt.
- RESULT reviewer's own mutants, planted alone in cloud_relay.sh and restored afterwards (`git status --short` empty). Unmutated: `189 checks, 0 failed`. Each one was killed. ev/reviewer-mutants.txt.
  - R1: the grammar accepts a leading zero (`0*` dropped from the refusal case): 14 failed.
  - R2: `held` matches a substring (`grep -qF` without `-x`): 1 failed.
  - R3: a well-formed pass does not clear the level (`level_set` replaced by `:`): 1 failed.
- RESULT null control: `a well-formed hold file owes no refusal (null control)` and `the same file newline-terminated holds #41 (null control)` pass inside the 189. Every harness row ran its unmutated step first, and none printed NOT RUN.
- RESULT figures re-derived at this head (ev/quick-checks.txt):
  - `cloud_relay self-test: 189 checks, 0 failed`; `selftest_wiring: 76 self-testing, 76 wired, 0 unwired`.
  - STRUCTURE RATCHET PASSED; ALL 2382 ENTITY CHECKS PASSED; ALL 109 HARNESS HEADER CHECKS PASSED; layout self-test: ok.
  - tmp_paths 0 refused; throwaway_git 0 refused.
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (PREPR_SKIP_CLOSURES=1).
  - env_drift `--claims-only` ok. The VERSION/manifest/RELEASE_NOTES/tests/golden three-dot stat prints 0 lines. CI prepr prints `no version edit`.
- RESULT figures stated at older heads: the body states `4 files, +133/-3` at f78491bb2. At this head the own diff is 4 files, +134/-4, and the difference is the disclosed docstring line. `## Figures`' `selftest_wiring 73/73` is stated at main 93e6a63d2. `## Main absorb` re-takes it as 76/76, which I confirmed. The roster SHA 306a96d5f in the body is now e5d5c508, and the destination counts (0, 0, and 1 for the group's own entry) are unchanged there. ev/carry-audit.txt.
- RESULT merge-tree: `git merge-tree --write-tree origin/main caac2c8d` exits 0 at origin/main b787c7d45 (tree c8d7d789), and exits 0 at 16a8240f (tree ed4082b4). It is clean, with no claim-file driver involvement. ev/merge-tree.txt.
- RESULT CI (check-runs API at this head, every run, read after all concluded at 07:36Z): 49 runs, 33 success, 16 skipped, 0 failure. That includes pr-contract ×2, closures, coverage, mutation, instrument-self-tests and nightly-status success. ev/check-runs-caac2c8d.tsv.
  - pr-contract's range check prints `record red-history 17 commit(s) between origin/main and this head, every failure conclusion across them: nightly-status`. The body's `## Red checks` answers nightly-status (main's scheduled lanes; the diff touches nothing they read).
  - pr-contract's own two reds at 056776d8 (jobs 119596472527 and 119669151379) are not named in `## Red checks`. Round 6 asked for that. policy_lint.mjs:6217 excludes pr-contract's own runs from red-history by name (#956, a body deadlock otherwise), and this head's pr-contract is green. The enforced rule therefore requires no root-cause answer for them, and this review does not block on them.
- RESULT class seams: cloud_relay.sh's production lines are unchanged by the absorb. The hold-file reader grep (`cloud-handoff-hold|hold_list` over tools/ .github/ dev/) still returns only cloud_relay.sh, INSTRUMENTS.md and the harness patterns. The second reader is the R10-ORCH-MACHINERY carry above. ev/class-and-append-claims.txt.
- RESULT code-owned: `grep -n 'cloud_relay\|tools/audit/seat\|r10_seat' .github/CODEOWNERS` prints nothing at this head.
