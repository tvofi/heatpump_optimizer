Root-cause analysis `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md`, round 2. It answers verdict/3411 (round 1, carry-missing). The enumerators behind each figure now land beside the document: `dev/audit/rca/open_prepr_receipts.py` (`--self-test`), its frozen output `open_prepr_receipts-tips.tsv` and `open_prepr_receipts-opens.tsv`, and `dev/audit/rca/open_prepr_6d.sh`. `dev/audit/config/bugclasses.json` gains the `_rca` entry the document is cited by. No production code changes.

- Round 1's host readings were cut, because no in-tree enumerator for them exists (the seat's scratch is on another host). That covers load, swap, the CPU-loop multiplier, slot `taken_at`, the `p1.log` medians and record-issue-continuation's self-test result. Its "not queued, not hung" reading is now marked not established. C3 is what makes that reading re-derivable.
- Disclosed self-correction: round 1's tree test used `git merge-base <code> origin/main`. Once the code lands on main, that merge base is the code itself, so the test read equal for any ancestor receipt. With main's first-parent commit inside the code as the base, C1's reach drops to about a quarter of round 1's figure. The cost test is re-taken on the new reach.

## Head

9bf2501d52b4dff5d67f23b5eba39cc28f69f37a on origin/main 0362916ac7 (merge base). origin/main was 5d09dedf69eb at 08:37Z on 2026-11-10, when the snapshots were taken.

## Mutation proof

n/a: this pull request lands no countermeasure and no production line. C1 to C4 are routed below, and each carries its failing case and null control. `open_prepr_receipts.py --self-test` is a harness's self-check, not a countermeasure: its non-merge row reads `no` while its merge-only row reads `yes`.

## Null control

- Tips: in `open_prepr_receipts.py --self-test`, a non-merge commit past the receipt reads `tree_equal=no` and a clean merge reads `yes`. A window that holds no tip reads no rows. Under round 1's rule, three real rows read equal although two of them carry fixer commits past the receipt (Figures). That is the control the old rule failed.
- Opens: the `receipt` grade is the control for the `full` grade. Both carry the same relay wait.
- 6d: `c19017d6` is a scoped diff, timed by the same command on the same container minutes before `6671786843`.

## Figures

Taken at 2026-11-10 08:37Z to 09:08Z against origin/main 5d09dedf69eb, over the window 2026-11-06T00:00Z to 2026-11-10T03:30Z (4.146 days).

- `python3 -I dev/audit/rca/open_prepr_receipts.py --self-test`: `PASS self-test, 0 failed`, 12 checks.
- `python3 -I dev/audit/rca/open_prepr_receipts.py tips --since 2026-11-06T00:00:00Z --until 2026-11-10T03:30:00Z --main origin/main` printed:
  - `RESULT tips=149 result=12 code=137 trailer=57 no_trailer=80`
  - `RESULT split same=5 merge-only=3 non-merge=24 not-ancestor=0 never=48 missing=0`
  - `RESULT tree_equal=2 of=27`
  - C1's reach is same + tree_equal, 5 + 2 = 7.
  - The reviewer's 12/57/81/138 and 5/25/2/49 differ by the moved refs and by this harness's ancestry-path rule for merge-only.
- Round 1's rule, `git merge-tree --write-tree <receipt> $(git merge-base <code> origin/main)` against `<code>^{tree}`, on `r10-carry-residue-2`, `r10-sav-meter-floor` and `r10-hotfix-stress-mem-peak`:
  - It printed `on_main=yes mb_is_code=yes old_rule_equal=yes` for all three.
  - The first two carry fixer commits past the receipt (`git log --ancestry-path --no-merges <receipt>..<code>`), and the harness reads them `no`.
- `python3 -I dev/audit/rca/open_prepr_receipts.py opens --since 2026-11-06T00:00:00Z --until 2026-11-10T03:30:00Z` printed:
  - `RESULT full n=70 median_min=62.8 p75_min=508.8`
  - `RESULT receipt n=68 median_min=18.9 p75_min=52.1`
  - `RESULT unmatched=3`
  - The latency rule is the delivery-row commit time less the newest body commit before it for the opened code.
- Cost test:
  - C1 saves 7 x (62.8 - 18.9) = 307 open-minutes in 4.146 days, 74 a day, at the medians.
  - Its standing cost is two git spawns per body push: ``git merge-base --is-ancestor` and `git log -1` each took 2.3 ms per call (n=50, timed with python `time.time()` on this container), about 5 ms per body push`.
- C-B: `git show <rev>:tools/pr/prepr.sh | wc -l` and `| grep -c '^ *st '` print `2734 123` at c09cf12010 and `4682 325` at b0762725099f. `HEAVY_SLOTS = 4` is set in `tests/gate_lock.py` since c09cf12010.
- C4, `bash dev/audit/rca/open_prepr_6d.sh <head>` on this cloud container (4 CPUs):
  - `c19017d6`: `rc=0 wall_s=40 predict_sha1=e880deb19085147bd6a6386916845596284cb9a1 predict_lines=16`
  - `6671786843`: ``rc=0 wall_s=1561 predict_sha1=da39a3ee5e6b4b0d3255bfef95601890afd80709 predict_lines=0` (the sha1 of empty input: no PREDICT line), run directly after `c19017d6` on the same container`
- `grep -rnE 'timeout (3000|7200)' tools/ dev/governance/ .claude/` printed nothing (rc 1).
- `python3 -I tools/audit/fold_ledger.py check`: `0 violation(s)`, 146 rca entries.

## Red checks

none

## Forward-carry

- C1, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6:
  - Change: `tools/audit/seat/body_push.sh` `prepr_trailer` takes the receipt from the local `hpo-prepr-receipt`, else from the parent body tip's one `Prepr:` trailer. It writes the receipt when the receipt's sha is an ancestor of the code head and its tree is that sha's tree.
  - Failing cases: a re-push from a second clone keeps the trailer. A clean merge of main past the receipt keeps it, and `reuse_verdict` returns rc 0.
  - Null controls, both preconditions: a non-merge commit past the receipt keeps the trailer and `reuse_verdict` returns rc 1, so a carried receipt never skips prepr on unproved code. A receipt on a non-ancestor writes no trailer.
  - Re-measure the reach with `dev/audit/rca/open_prepr_receipts.py tips` over your own window. It was 7 tips in 4.146 days at origin/main 5d09dedf69eb.
  - Carry: R10-PREPR-RESIDUE
- C2, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6:
  - Change: `tools/audit/seat/body_push.sh` names, both in its no-trailer line and in a `Prepr-absent: <reason>` trailer on the body commit, which condition failed: no receipt file in this checkout; a receipt not an ancestor of the code head; a receipt whose tree is not its sha's; or no trailer on the parent tip.
  - Failing case: each of the four, planted, prints and writes its own reason. Before the fix, all four print one line.
  - Null control: a valid receipt writes `Prepr:` and no `Prepr-absent:`.
  - Carry: R10-PREPR-RESIDUE
- C3, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6:
  - Change: `tools/pr/prepr.sh`'s step lines carry the step's elapsed seconds from bash's `$SECONDS`, with no spawn, and the final `PRE-PR:` line carries the run's.
  - Failing case: a step stubbed to sleep 2 s prints an elapsed of at least 2. Before the fix there is no field.
  - Null control: a no-op step prints 0 or 1, so the field times the step and not the run.
  - Carry: R10-PREPR-RESIDUE
- C4, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6:
  - Problem: the comment over `predict_line` in `tools/pr/prepr.sh` says step 6d "costs seconds". `bash dev/audit/rca/open_prepr_6d.sh 6671786843` measured 1561 s on a 4-CPU cloud container, against 40 s at the scoped `c19017d6`.
  - Change: correct the premise, and bound or leave to CI the GRADER replays that `instrument-self-tests` already runs, keeping SELF-TEST READS.
  - Proof: `open_prepr_6d.sh 6671786843` before and after on one host, with wall time down and `predict_sha1` unchanged (zero PREDICT lines, sha1 da39a3ee5e6b4b0d3255bfef95601890afd80709). At `c19017d6`, `predict_sha1` stays e880deb19085147bd6a6386916845596284cb9a1.
  - Carry: R10-PREPR-RESIDUE
- Reviewer follow-up, the "never" tips (48 in this snapshot, 49 in round 1's): their process state is not established, and the triggering instances are explained by C-B alone until C2 lands. After C2, extend `dev/audit/rca/open_prepr_receipts.py` to split `never` by the `Prepr-absent:` trailer, and re-take the state per reason. Null control: a tip carrying `Prepr:` is never counted in `never`. Carry: R10-PREPR-RESIDUE
- Reviewer follow-up, the out-of-tree host figures: resolved in this pull request. Each figure is landed under `dev/audit/rca/` with its enumerator, or cut. Carry: dismissed: built in this pull request

## Friction

finding-propagation.md: unenforced: `tools/audit/carry_audit.py` `landed` printed `CARRY-LANDED: 0 missing` for this body because R10-PREPR-RESIDUE's carries 8 to 11 already name this topic as their source, although they still hold round 1's text without controls. It matches on the source, not the text. The orchestrator owes these roster ops on `handoff/audit-r10-roster`: replace carries 8 to 11 with the C1 to C4 items above, append the "never" follow-up, and set the group's `rca` to `R10-RCA-OPEN-PREPR-SLOW`. Carry: R10-PREPR-RESIDUE
