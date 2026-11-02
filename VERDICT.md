Fix review: blocked b307f3599921ff345f677f34583958fa930a935a class-open: features.py still fails 3 zone checks at the head under America/New_York and Asia/Tokyo; only Europe/Stockholm was measured

bus-nonce: 63a83911d29f177af308c181cff4727f

## Head

b307f3599921ff345f677f34583958fa930a935a, the head named in the dispatch and in the PR body; `git ls-remote` re-read it unchanged at the end of the review. Round 1, full review. Merge base dfb4ce2b52fafb340e0320bc2efb870099a53884. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Block

1. **class-open (carries 0 and 3, 0-based).** The group brief's class is "the features checks that fail under a non-UTC `HASTUB_TZ`". The body measures one zone, Europe/Stockholm (UTC+1), and its new comments claim correctness "under any `HASTUB_TZ`". No enumeration rule is named. I ran the head under two more non-UTC zones, and the same failure shape (a naive or UTC-literal instant against the configured zone) is still red there:
   - `HASTUB_TZ=America/New_York`: base `6 of 4770 FEATURE CHECKS FAILED`, head `3 of 4770 FEATURE CHECKS FAILED`. Still red at the head:
     - "with no meter, a month of DHW-only mornings bills what the stated rule bills ..." (tests/features.py:17145)
     - "a naive stored tick adopts the clock's zone and detects the same gap" (tests/features.py:47485; `_T3_OUTAGE_NOW` is UTC-aware, and the naive tick is replaced to naive UTC wall clock)
     - "the humidity entry nearest NOW wins, not the first in the list" (tests/features.py:50527; `_T6_HUM_NOW` is naive)
   - `HASTUB_TZ=Asia/Tokyo`: base `8 of 4770 FEATURE CHECKS FAILED`, head `3 of 4770 FEATURE CHECKS FAILED`. Still red at the head:
     - the DHW-only mornings bill check
     - "#943: the honest sizer leaves a power-limited heavy house at the full nameplate step ..."
     - the humidity-nearest-NOW check

   These are neither fixed in the diff nor dispositioned in the body. The fix pattern the PR already uses (name the instant in `DEFAULT_TIME_ZONE`, or make it aware) applies to each. Whether any of them is a production zone defect rather than a test assumption has to be settled per check by the fixer.
2. **The gate-lease carry (carry 1, 0-based) is marked BUILT, but the flake is still live at the head.** Without any planted defect, `one_winner` read red once at the head on a quiet runner with the CI signature `queued=True overlaps=1 order=['b', 'a']` (ev/gl_head_quiet.txt). Overall it was 1 red in 190 head runs and 0 in 160 base runs.

   The mechanism is a TOCTOU in production `_free_slot` (tests/gate_lock.py:708-715). `_read_at` sees `is_file()` False and returns None. The rival's `os.link` then lands. `_free_slot`'s own `if not path.is_file()` re-check is now True, so it unlinks the rival's live, just-created slot. Every waiter runs `_free_slot` on every poll, including a waiter that is not at the head of the queue.

   A pure 30 ms delay after `_read_at` returns None for a slot path, with no logic changed, makes the case red 2 of 10 at the head and 2 of 10 at the base (ev/gl_toctou.py, ev/gl_head_toctou.txt, ev/gl_base_toctou.txt). So the race predates this PR. The PR's test-side change (a condition wait instead of the 0.15 s hold) is sound and keeps the planted control red, but it does not fix the flake the carry exists for. The body's "cause is not established" should become the cause above, and the fix belongs in `_free_slot`: do not unlink on a missing-then-present file, or re-read before unlinking. That fix also needs a planted-delay control like the one here.
3. **root-cause-unanswered: `tests / replay`** (check-run 125168587530) concluded `failure` at this head: `1 of 176 replay checks FAILED`, "synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.389 over its budget 2.173]". `## Red checks` says "none from this diff" and does not name it, and `pr-contract` refuses on exactly that (run 125180207180: "check `tests / replay` is red and `## Red checks` does not name it"). The diff writes no runtime code (see Evidence), so this is likely runner CPU noise, but the body owes the answer.

## Findings

- features.py zone checks still red at the head under America/New_York (3) and Asia/Tokyo (3): DHW-only mornings bill, naive stored tick (`_T3_OUTAGE_NOW`), humidity nearest NOW (`_T6_HUM_NOW`), and #943 sizer. Fix or disposition each, and measure Stockholm, New_York, Tokyo and UTC at both ends. Carry: R10-SUITE-HOST-DETERMINISM
- Gate-lease flake still live at the head (1 of 190 unplanted). The cause is the `_free_slot` is_file TOCTOU (tests/gate_lock.py:708-715), demonstrated with a delay-only plant at base and head (2 of 10 each). Build the fix in `_free_slot` with the delay plant as its control; the CI history's earlier `overlaps=1` reds before 2026-10-24 were fab4a07c1's torn create. Carry: R10-SUITE-HOST-DETERMINISM
- `tests / replay` red at the head (cycle_cost cpu_ratio 2.389 > 2.173 on synthetic-dhw-only.json) is not named in `## Red checks`, and `pr-contract` is red on it. Carry: R10-SUITE-HOST-DETERMINISM
- No committed finder's harness exists for carries 0-3. I built my own and disclose them as the reviewer's, not the finder's: ev/crv.py (it runs the head's `_coverage_revalidation` against either tree's coverage_tree.sh), ev/gl.py (repeats `_priority_cases`, optionally with the pre-fab4a07c1 O_EXCL-then-write create planted), and ev/gl_toctou.py (the delay-only plant). The fixer should land the gate-lease one with the `_free_slot` fix (fixer.md 18). Carry: R10-SUITE-HOST-DETERMINISM

## Red checks

Every check-run at the head (55 runs, one page, read live after all workflows concluded):
- `tests / replay` (125168587530) is red; see Block 3.
- `pr-contract / pr-contract` (125179056639 and 125180207180) is red on the unnamed replay red, the only ERROR in its body check.
- `gate` (125179329799 and 125180528483) is red as the aggregate of the above.

`merge_train.py classify` printed `RED b307f359... pending: none red: gate` (rc=1). Everything else is success or skipped, including fast (3.14), coverage, coverage-ratchet, closures, graders-head-copy, instrument-self-tests, mutation, typing and arch-score.

## Evidence

- RESULT carries in the body: all nine roster carries (0-8) are named. Carries 0-3 are marked built; carries 4-8 are named as later parts that stay in the group's roster `carry` list on handoff/audit-r10-roster (c9bf8de54). This is consistent with the roster entry.
- RESULT coordinator.py: the change is docstring-only. The AST with docstrings blanked is identical at base and head (ev/coordinator_ast.txt). `_comparable_ts` already returns `dt_util.as_local(ts).replace(tzinfo=None)` for an aware stamp against a naive grid, so the old docstring ("keeps its own wall clock") was wrong and the new one matches the code. There is no runtime change, and the behaviour is preserved. The features check over it (`_t6_comparable_ts`) passes at the head under Stockholm, UTC and unset.
- RESULT features at both ends (`PYTHONPATH=tests/hastub python3 tests/features.py`):

  | zone | base | head |
  |---|---|---|
  | Europe/Stockholm | 6 of 4770 failed | ALL 4770 passed |
  | UTC | ALL 4770 passed | ALL 4770 passed |
  | unset | not run | ALL 4777 passed |
  | America/New_York | 6 of 4770 failed | 3 of 4770 failed |
  | Asia/Tokyo | 8 of 4770 failed | 3 of 4770 failed |
  | Asia/Tokyo with TZ=Asia/Tokyo and LANG=de_DE.UTF-8 | not run | 3 of 4770 failed |

  The body's Stockholm figures (6 failed before, all 4770 after, 4777 unset) re-derive exactly. The five Stockholm hunks map one-to-one onto the six base FAIL names (ev/features_base_Stockholm.summary.txt). UTC is unchanged.
- RESULT entities (`PYTHONPATH=tests/hastub python3 tests/entities.py`): base `ALL 2592 ENTITY CHECKS PASSED`; head `ALL 2593 ENTITY CHECKS PASSED`; head under HASTUB_TZ=TZ=Asia/Tokyo LANG=de_DE.UTF-8 `ALL 2593 ENTITY CHECKS PASSED`. The FAIL lines in those logs are the planted controls of passing rows. Carry 4's "2 of 2449 failing at the base" does not reproduce on this host at this base, which agrees with the body.
- RESULT coverage_tree.sh (carry 2, 0-based), with my ev/crv.py:
  - At the base, the late-writing descendant is recorded as `entities.nodata` with no refusal, which reproduces the early read.
  - At the head it is waited for: no `entities.nodata`, no refusal.
  - At the head with `W5P_DESCENDANT_WAIT=0` it refuses with "left descendants still running", naming the script, and records no nodata.

  The base run is also the mutant that drops `wait_descendants`, and the row's predicate is false there. The refusal propagates through `measure ... || exit 1` in every lane mode. CI `tests / coverage` and `coverage-ratchet` are green at the head.
- RESULT gate_lock planted control, pre-fab4a07c1 O_EXCL-then-write create (ev/gl.py): base 8 of 30 red, head 10 of 30 red, all with the CI signature. The control still reads red after the change.
- RESULT gate_lock unplanted one_winner:

  | runner | base | head |
  |---|---|---|
  | under 4-core load (features running) | 0 of 100 | 0 of 100 |
  | quiet | 0 of 60 | 1 of 30, then 0 of 60 |

- RESULT structure: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED. No `*_budgets.json`, `tests/closures.json`, VERSION, manifest or RELEASE_NOTES change in the three-dot diff.
- RESULT claim files: byte-identical to origin/main, at dfb4ce2b5 and again at 8fcaf47e1.
- RESULT `git merge-tree --write-tree origin/main b307f359` exits 0, both at dfb4ce2b5 and at 8fcaf47e1 (ev/merge_tree.txt).
- RESULT delivery row: dev/programme/delivery/3170.md is in the three-dot diff. No host path appears in the added lines.
- The fixer's statement "0 bad of 150 under CPU load" is the fixer's own measurement. I did not re-derive it, and my own counts are above.
