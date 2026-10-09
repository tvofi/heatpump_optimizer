Fix review: merge 7843b799255741fcfee41c6d719d3de1bef84c50
bus-nonce: 6647e64f13ffa06a971a444cb8253351
seat: review-2071
Evidence: /Users/timmalmstrom/hpo-seats/review-2071/evidence

Round 3. Reviewer seat review-2071, fresh detached worktree at the live head `7843b7992` (re-checked immediately before this post; unchanged all session). Merge base `bd59a4af1`, unchanged. The fix-review contract is current (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty at `origin/main c518447eb`).

## The round-2 block is cleared: the survivor is killed by a real check

Round-3 delta `b83f92421..7843b7992`, enumerated: `6aaba97fe` (fixer, tests/features.py +6 lines — one new check) and `7843b7992` (bot `ci: pin killed mutants`, one ledger row). **No production line moved**, so round 2's production measurements stand; which numbers survive is stated per-item below.

**What killed it.** The fixer added one behavioural check to the floor-return block: `_frs_run([(0, _frs_dead), (90, _frs_dead)])[0] == [0, 1]` — ninety minutes of silence raises the repair, read on a literal clock, not through `_frs_lim`, so it does not scale with the constant the way the other 13 checks do. The `killed_by` row (`@module.CONST.fd447209.json`, added solely by the bot commit) names `tests/features.py` and records the pin path: `mutation-pins (1)` job 113704028276 at `6aaba97fe` drove the lane's own CONST mutant against a green baseline (`baseline tests/features.py: rc=0 failed=0`) and printed `pinned notifier.py:182 CONST -- killed by tests/features.py`, `PIN KILLED: 1 pinned, 0 left unpinned`; `mutation-autofix` (113712608918) committed the row. That is ci-autofix.md's sanctioned path — the bot pinned a **kill it drove**; no survivor triage was automated, and none is owed (the disposition is a kill, not a triage; `survivor_triage/notifier.py` does not exist).

**My own mutant re-run (step 1), at the live head, in my worktree, restored after each:**

```
RESULT head 7843b7992 unmutated: ALL 14 FEATURES BLOCK PASSED / ALL 20 ENTITY SLICE PASSED
RESULT CONST notifier.py:182 60.0 -> 120.0 (the lane's operator): 1 of 14 FAILED -- "ninety minutes of silence raises the repair ..." [[0, 0]]; restored -> ALL 14 PASSED, git status clean
RESULT CONST 60.0 -> 600.0 (body's M7): 2 of 14 FAILED -- period-bound [600.0 min] + ninety-minute [[0, 0]] (body's M7 claim re-derived exactly)
RESULT CONST 60.0 -> 89.0: ALL 14 PASSED;  60.0 -> 91.0: 1 of 14 FAILED (ninety-minute) -- the check bites exactly at its stated clock bound
RESULT full tests/features.py unmutated at head: 1 of 3874 FAILED = R9-F2.1 P3 storage-plan [110.4366 vs 110.1297], a pre-existing local solver-float flake on this host (unmutated baseline; CI fast (3.14) green at both heads), not this PR's
RESULT full tests/features.py under CONST 120.0: 2 of 3874 FAILED = the same P3 flake + the ninety-minute check; every features.py reference to FLOOR_RETURN_SILENT_MINUTES lives inside the block (lines 60240-60393)
```

**Attack on the killing check — it survives.** It is not vacuous (fails under the mutant, passes unmutated, and at 89/91 straddles exactly its stated bound); it does not assert the mutated value (120 fails it); it does not re-implement the production formula (it drives the real `FloorReturnWatch.handle` and asserts the repair count — tests/README.md's rule is satisfied); and it is not an instrument move: the ledger row appeared only after and because the check kills (remove the check and the pin's own drive flips to LIVES — round 2 measured exactly that at `b83f92421`, `ALL 13 PASSED` under 120.0). Step 14 answered: the movement is earned by the change.

One observation, not a block: the check hard-codes a 90-minute upper bound where the pre-existing rationale check admits `<= 180` ("shorter than three hours") and the production docstring says only "short of a day". 90 traces to no brief text I could find; it is the example this review's round-2 verdict itself offered ("such as at most 90 minutes"), the check states the property in product terms, and it passes at the real 60 — a deliberate tightening of the accepted range, which is what a value pin is for. If the product later moves the constant above 90, the pin forces that decision to be deliberate; that is the ratchet working, not a defect.

**CI at the live head, read from the lane's own logs (step 11's green-mutation rule):** `mutation` 113712782376 at `7843b7992`: `MUTATION TABLE PASSED`, `0 survivor(s) of 3 evaluated = 0.0%`, `PIN RE-VERIFICATION: 3 reproduced, 0 not reproduced, 0 not re-verified`, `4622 unpinned ... the ledger agrees with the deterministic inventory`. Not INCONCLUSIVE — mutants were drawn and evaluated. The 3 reproduced pins are the drawn GUARD_OFF sites; the CONST pin was not re-drawn at this head, so its authority is the pins job's drive at `6aaba97fe` (identical production and features.py — the bot commit changed only the ledger row) plus my own run above, and I say so rather than reporting the green lane as a re-verification of it.

## Steps 2/3 at the round-3 delta: the finder's harness, both ends, re-run this round

The delta is tests+ledger only, so the ends are unchanged production; I re-ran the finder probes anyway (reviewer-built; the finding has no committed harness — disclosed in round 1, stands):

```
RESULT probe at head 7843b7992: diag config.min_kw=1.2 max_kw=6.0 (live 1.2/6.0, setup 3.0/14.0); config_setup.min_kw=3.0; leaks=[]; token/name REDACTED; floor stale_7h / implausible_85C / unknown raise [0,0,1,1]; fresh_5min, fresh_5h_under_limit, other-input-dead raise 0 -- identical RESULT lines to rounds 1-2
RESULT probe at merge base bd59a4af1: diag config.min_kw=3.0 max_kw=14.0 (the setup-only defect), config_setup absent, floor probe AttributeError: no FLOOR_RETURN_SILENT_MINUTES -- the defect and the absent implementation, confirmed again
```

Round 2's mutation kills, surviving unchanged (no production line moved; re-cited, not re-taken): R1 config->dict(data) 2/20, R2 overridden->sorted(options) 2/20, R3 listener deleted 1/13, R7 selector->True 1/13, R8 config_setup->merged 3/20 (`evidence/round2-b83f9242....txt`). The block's own null controls (live sensor, unconfigured slot, other-input-dead, short-gap restart, payload-without-signal) all pass unmutated at the live head in my run.

## Step 11 at the live head (check-runs API, latest run per name)

```
RESULT check-runs at 7843b7992: total=67, pending=0; 39 success, 27 skipped, 1 failure = nightly-status only
RESULT nightly-status red: grades main's nightly lane; gh pr diff --name-only reaches no workflow and nothing it reads differently; the body names and answers it -- not this PR's (contract step 11)
RESULT red-history in range: 6aaba97fe ran mutation red (the unpinned CONST survivor) and nightly-status red; the body's ## Red checks names both, answers the mutation trigger with the cheaper detector (run CI's own CONST operator per site, not a hand-picked value) and corrects the round-1/2 mis-citation -- answered, per contract I check the trigger was answered, not the answer
```

## Steps 4/5/6/7/10/12/13

```
RESULT claim files + tests/golden/: diff touches none; both byte-identical to origin/main (step 4)
RESULT VERSION / RELEASE_NOTES.md heading / manifest version: untouched (step 5)
RESULT class-open (step 6): delta is tests+ledger only; the body's 21-slot reader census and one-slot disposition stand from round 2, unchanged
RESULT step 7/12: the body's ## Head names 6aaba97fe, the head before the bot's pin commit 7843b7992 -- steward S10's autofix shape; pr-contract is green at the live head; reported, not blocked, per dispatch. Head measured = head posted = 7843b7992, re-checked at post time; it did not move under this review
RESULT forward-carry (step 10): unchanged from round 2 -- live-arch/DESIGN.md carries S6 (set_issue reuse, line 35) and section 6 "5 vs floor return" (line 139), verified present this round
RESULT merge-tree --write-tree at 7843b7992 (step 13): rc=0 vs origin/main c518447eb, and pairwise vs #2065 6f420a1f7, #2066 630849897, #2070 a9ba0b887 -- no conflict, no MERGE-CLAIM line; mergeStateStatus BLOCKED is the draft + required-checks state, not DIRTY
```

## Step 8 — what I could not re-derive

The pin row's `failed=2` is CI's full-features count at `6aaba97fe`; the job log does not name the two checks, and this host cannot re-derive the count because my unmutated baseline already fails the BLAS-sensitive R9-F2.1 P3 (the documented local-container gap; CI is the authority and its baseline was `failed=0`). The kill does not rest on that figure: my own drive of the lane's exact mutant at the live head fails the pinned driver, and among all floor-return checks only the new one.

Body figures re-derived and matched where cheap: 14 block checks, 120-mutant 1 of 14, M7 2 of 14, unmutated ALL 14 / ALL 20. The body's full-suite and structure/archscore figures remain CI's and round 2's authority; not re-run here (heavy-run rule).

PR is a DRAFT; left as-is. No approval, merge, ready-for-review or comment posted by this seat; the verdict goes on the bus only.
