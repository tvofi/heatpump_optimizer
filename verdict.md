Fix review: merge a6c6bd8eaaae1acedcb8d25d6fdad5057573a5aa

bus-nonce: 8fc0fc5229de3eb19934a2eafd43f2a8

Round 2, a delta review of the round-1 block (PR comment 6403868037, `mutation-vacuous` at d076f22c). Head measured: a6c6bd8eaaae1acedcb8d25d6fdad5057573a5aa (ev/HEAD.txt). `git ls-remote origin refs/pull/2832/head`, re-read just before writing, still returns it (ev/head_reread.txt). Merge base 0dfc063fa56ef7c5d2b202933792caf87a2ed154. Contract check: `git diff <merge-base>...origin/main -- dev/governance/roles/` changes only fixer.md. I followed fix-review.md as it stands on origin/main.

## Findings

- The body's `## Forward-carry` sends the step-0/step-1 flap (the control-mode disinfection switch toggling with each folded window) to `R10-IMMERSION-LATCH`. That group's `brief` holds no legionella text, either in origin/main's `dev/programme/rosters/wave-r10-groups.json` or at `handoff/audit-r10-roster` 78d071da. Its subject is also immersion-energy booking, not the disinfection switch. So the carry is routed in the body (carry_audit counts it), but no stage brief holds it yet. Round 1 found the same thing, and this round leaves it unchanged. The orchestrator owes a roster op that writes it into a brief, with its control: in control mode on a pump that cannot reach the target, the disinfection switch toggles once per folded window. Carry: R10-IMMERSION-LATCH

## Evidence

- Block (1) is settled. Each of the 8 sites was re-mapped to this head and re-mutated alone, as one line in a git-archive copy of the head (ev/mutants.sh, ev/mutant_*.diff). The checks were `PYTHONPATH=tests/hastub python3 tests/features.py` and `tests/guard_pins.py` (ev/mutant_*.txt):
  - The null control is a comment line. It fails only `recorded_at (#363)`, because the archive has no `.git` (as round 1 found). Every mutant shows that line too, so I subtract it.
  - d076f22c:60 CMP_BOUND, now :60, `>` → `>=`: RED, `the overdue notice comes due at the interval, not before and not an interval late`.
  - d076f22c:345 CMP_BOUND, now :349, `<` → `<=`: RED, `a window inside the retry folds into its attempt and keeps the higher peak; one at the retry's end is a fresh attempt`.
  - d076f22c:350 CLAMP_DROP, now :354, `max(peak, self.attempt_peak or peak)` → `(peak)`: RED, same check.
  - d076f22c:621 CMP_BOUND, now :625, `<= 0` → `< 0`: RED, `an attempt at or before the last completion is spent, and the next window stamps its own`.
  - d076f22c:621 GUARD_OFF, now :625, `if False:`: RED, same check.
  - d076f22c:655 BOOLOP, now :659, `and` → `or`: RED, `the overdue notice stays down with disinfection or hot water off, a tank probe notwithstanding`. This is round 1's R3.
  - d076f22c:658 GUARD_OFF, now :662, `if False:`: RED, `the overdue notice is written once per change, not on every cycle`.
  - d076f22c:701 GUARD_OFF, now :705, `if False:`: RED, `a mode block holding an overdue cycle is logged as a warning`.
  - R4 (threshold `* 48.0`): RED, 2 checks, including `…and the guard raises it one day past a 7-day interval [None]`.
  - `tests/guard_pins.py` prints `ALL 50 GUARD PIN CHECKS PASSED` under every mutant, as the body says.
  - Every named check matches the body's `## Mutation proof`.
- Site enumeration. CI's `tests / mutation` on this head (job 121402877739, ev/job_mutation_121402877739.log) prints `MUTATION TABLE PASSED`:
  - It is not INCONCLUSIVE.
  - The null `legionella.py:89 NULL_COMMENT` survived every driver.
  - It re-evaluates the 3 ledger-invalidated mutants and kills each with `tests/features.py`: 60 CMP_BOUND, 615 CLAMP_DROP and 625 GUARD_OFF.
  - It prints no UNPINNED and no stale pin.
  - That matches the body's `## Unpinned sites`, which says none at this head. The 10 killed_by rows the body names are in the three-dot diff, and the two stale `c87bfc45` rows are deleted.
  - I cite that heavy run; I did not re-run it. I did not re-run `ci_predict.py` either.
- Harness at both ends. I ran a copy of the head's `dev/audit/harnesses/r10_legionella_completion.py`, whose sha1 cba192d1ca79c5e3c661ad5c2b52a751ec4803d5 matches the body, with `--days 14`, in detached worktrees at 7d2056970e08 and at the head (ev/harness_*.txt).
  - `reach`, `short` and `marginal` reproduce the body exactly:
    - base: 5 commanded steps, gaps `[145.0, 145.0]`, due-in 122.8;
    - head: 139 steps, thirteen 24.0 gaps, due-in 0.8, `dhw_legionella_overdue {'days': '79', 'interval_days': '7'}`;
    - `reach` at both ends: 3, 9, 146.2.
  - I could not re-derive the `blind` arm. Both runs hit my 1200 s timeout under CPU contention from the parallel mutants, before that arm printed.
- Red checks (2), read from the commit's check-runs API (ev/check_runs*.tsv):
  - Reds on this head:
    - `prelude` 121402443939 and `gate` 121404451630 at 04:52Z, both `RATE-LIMITED ... exit code 3` (installation rate limit). They died before any test body ran, so they are infra.
    - `pr-contract` 121411902170 at 05:21Z, which refused because `prelude` was red and unnamed.
    - `gate` 121412097008 at 05:21Z, its aggregate.
  - After the rerun:
    - `prelude` 121414402451 is green.
    - `pr-contract` 121414682620 and 121415021993 are green. 121415021993 started at 05:32Z, after the last red concluded, and prints `red checks the body must answer:` (empty) and `clean no refusal`. Under fix-review.md step 11 that run is the evidence. The rerun green answers the rate-limit reds.
    - `gate` 121414899745 and 121415225380 are green (`PASS`).
  - Green now: arch-score, budget-raise-gate, codeql (3 analyzers), CodeQL, governance env-matrix, policy-docs, instrument-self-tests, wave-script and delivery-status, hassfest, validate-hacs, and tests closure-scope, mutation, briefs, nightly-status, typing, browser, closures, arch-instrument, coverage, coverage-ratchet, lane-proofs, graders-head-copy and fast (3.14).
  - The rest are skipped, including mutation-pins and mutation-autofix (nothing to pin). None is red.
  - The body's `## Red checks` answers the reds of the previous head 538af1321, with the cheaper detector `typing_ruler.py --mypy` and its cost. It does not name the head's infra reds. The green `pr-contract` above computed nothing owed.
- (3) Three-dot diff:
  - `VERSION`, `RELEASE_NOTES.md`, `manifest.json`, `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are untouched (empty diff), and the body claims no drift.
  - `dev/programme/delivery/2832.md` is in the diff.
  - `tests/structure_budgets.json` lowers `class_excess_loc` (18086 → 18080 against this base), which is round 1's payment.
- `python3 -I tools/audit/carry_audit.py pr 2832` prints `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit.txt).
- `git merge-tree --write-tree origin/main a6c6bd8e` exits 0 against origin/main 11b7a9d739db46a5a62e9f9cf01a8f527a974137 (ev/merge_tree.txt).
- I built my own instruments and disclose them as mine: ev/mutants.sh, a one-line sed per site on an archive copy. The finder's evidence is the owner-export figures, which the harness's starting state encodes (round 1). It is the same harness the fixer used, and no separate finder's harness exists.
