Fix review: blocked 95da81dcf729e71bcb6d105fe82caa24a8352a1d caused-by-unwritable: injected and refix can never read for rounds 10 and 11, because set-field refuses caused_by on any group without its own rca record and no roster op adds one

bus-nonce: aae61a2d80c6a924d17e019c7b081600

Round 1 (first review of this PR), a full review at head 95da81dcf729e71bcb6d105fe82caa24a8352a1d, merge base d4968fe08ba0b18f9d96f6ca308edf45f35ca469.

## Block

`loop_ledger.owed` says every escape owes `caused_by`, and so does every other hotfix group (card P7: "every hotfix group and every outside group records what caused the defect"). `roster_lib.convergence_why` admits `caused_by` only when its `rca` id is already in the group's own `rca` list (`roster_lib.py`, the `if rca not in (group.get("rca") or [])` arm). `roster_edit.py` has no op that adds an `rca` entry to an existing group. Only `append-group` writes `rca`, and `set-field` refuses `rca`, because it is not in `SET_FIELDS`. Hand-splicing the roster is ruled out. So for a group that has no `rca`, the only sanctioned writer refuses `caused_by` permanently. The PR's own self-test pins exactly that refusal (`set-field caused_by is refused without the group's own rca record`, on R9-S3).

Measured on the real record at the reader ref, `origin/handoff/audit-r10-roster` (`ev/norca.py`, `ev/norca.txt`):
- round 10: 112 of the 123 groups that owe `caused_by` have no `rca`, and so do all 48 of its 48 escapes;
- round 11: 14 of 17 owing groups have none, and so do all 12 of its 12 escapes.

So `injected`, which every escape's `caused_by` decides, and `refix`, which needs the whole ledger, can never print a value for round 10 or round 11. The same holds for every ISO week that contains one of those groups. These two reads are half of what the ledger is built to print. That contradicts two statements in the body: "Carry 8: built (found_by and caused_by on every hotfix and outside group)", and C5's "the figures exist once the orchestrator sets the fields". The orchestrator cannot set these fields. The ledger stays honest: it prints `unread` and never a wrong value. But the mechanism cannot be completed on the record it exists to read.

The fixer chooses the repair. Options include: a sanctioned way to attach a group's RCA record (an `rca` set-field arm, validated against `dev/audit/rca/`); admitting a `caused_by` whose `rca` names any root-cause record that lists the group; or narrowing `owed` so a group the root-cause rule does not reach (`defect-root-cause.md`'s two triggers) does not owe `caused_by`. Whichever is chosen, the repair needs a check showing `caused_by` written on a group that started with no `rca`.

## Findings

- Surviving mutant: `loop_ledger.load_ref`'s precedence `{**entered(b.stdout), **when}` swapped to `{**when, **entered(b.stdout)}`. With the swap, the week of a group carried from one roster into a later one is taken from the later roster, which contradicts the docstring's rule that a group's week is its roster entry. No self-test fails, because the history case uses one roster file. On today's record the output is byte-identical (`ev/ledger-blame-mutant.diff` is empty), so it is a test gap rather than a live misread. Carry: R11-PRE-ROUND-METRICS
- Surviving mutant: `roster_lib.convergence_why`'s `or not (root / "dev/audit/rca" / f"{rca}.md").is_file()` deleted. No case gives a group an `rca` id whose file is missing, so the file-existence arm of the refusal is not pinned. Carry: R11-PRE-ROUND-METRICS
- Surviving mutant: `loop_ledger.reads`'s `refix` count changed from `roster_lib.recorded(g, ("follows",), names)` to `g.get("follows")`. A `follows` naming no roster group would then be counted as a refix, and no case catches it. Carry: R11-PRE-ROUND-METRICS
- Surviving mutant: `loop_ledger.reads`'s `kids = sum(1 for g in every ...)` changed to `groups`. In a weekly split this would drop a child that falls in a different week from its countermeasure. The fixture puts every group in one period, so the two choices cannot be told apart. Carry: R11-PRE-ROUND-METRICS
- Surviving mutants that are near-equivalent or cosmetic: `entered`'s `setdefault` changed to plain assignment (a group's `"group":` line appears once per file), and the `"unentered"` week label. Both are unpinned; a case is optional. Carry: R11-PRE-ROUND-METRICS
- Note: figure: the body says the head ledger "prints every round's escapes, injected, refix and loop as unread". At this head, round 9 prints `escapes 0` and `injected 0` as values, and week 2026-W43 prints all four reads as values (`ev/ledger-head.txt`). Carry: R11-PRE-ROUND-METRICS
- Note: stale-body: the `## Head` section repeats the same recarry paragraph four times. Carry: R11-PRE-ROUND-METRICS

## Evidence

- Head: `refs/pull/3657/head` and `fix/r11-pre-round-metrics-p2` both read back 95da81dcf729e71bcb6d105fe82caa24a8352a1d at the end of the review (`ev/HEAD.txt`).
- CI: `merge_train.py classify 95da81dc... --pr 3657` prints `GREEN 95da81dcf729e71bcb6d105fe82caa24a8352a1d pending: none red: none`, both at the start and before the verdict (`ev/classify.txt`). The only red in the packet digest is `tests / nightly-status`. It is not in `merge_train.py owed-reds`, so no `## Red checks` answer is owed.
- Merge: `git merge-tree --write-tree origin/main 95da81dc...` exits 0, printing `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` touches only `architect-planner.md` and `orchestrator.md`, so `fix-review.md` is current.
- Self-tests at the head (`ev/selftests.txt`):
  - `loop_ledger self-test: 0 failed`
  - `roster_lib self-test: 95 checks, 0 failed`
  - `roster_edit self-test: 314 checks, 0 failed`
  - `scorecard self-test: ok (without mutants)`
  - `throwaway_git: 0 raw git init or clone site(s) refused`

  These match the body.
- Mutation (`ev/mutants.txt`, reviewer-built driver `mut.sh` at the head; 17 mutants, 11 killed, 6 survived):
  - Killed, re-running the body's named mutants: `replan-path`, `rca-arm`, `owed-hotfix`, `sc-split`. Also killed: `latest-dedupe`, `injected-merged`, `ratio`, `gen-cycle` (timeout), `dim-file`, `self-cause`, `owed-rca`.
  - Survived: `rca-file`, `blame-precedence`, `blame-setdefault`, `kids-every`, `refix-recorded`, `week-unentered`. Each is listed under `## Findings`.

  The CI mutation table was not re-run; its lane is green.
- The `_replan_production` fix is confirmed. The old path `parents[2] / "tools"` resolves to `tools/tools/plan/replan.py`, which does not exist. The lane-less `group_class({"group": "X"})` reads `instrument` with the base's roster_lib and `production` at the head. On the real rosters, 3 of 10 class-less round-10 groups flip (R10-CARD-VOICE, R10-ROSTER-PUSH-RACE, R10-STORE-RACES), and round 11 has no class-less group (`ev/gclass.py`, `ev/gclass.txt`).
- Null control: `--dir` on an empty directory prints `loop_ledger unread` (self-test case, passing).
- Finder's harness: none is named. This is an instrument build, not a finding fix. The instruments here (`mut.sh`, `norca.py`, `gclass.py`) are the reviewer's.
- Version: `VERSION`, the manifest version and the release notes are untouched by the diff (13 files, none of them).
- Figures not re-derived: `Architecture score: dS +0.0000 NULL` and `STRUCTURE RATCHET PASSED` are cited from CI's green `arch-score` and `gate`, not re-run. The equivalent-survivor claim for `loop_ledger.py:59 CONST_SWAP` was judged by reading the code, not by re-running it.
