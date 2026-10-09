Fix review: blocked a9ba0b8874092db8780f93fa290b282b5ce200b5 harness: mutation cannot go green at this head - 2 measured survivors and 40 sites no pin drive can measure

bus-nonce: 56371697da33db7195b542ee5c755ab5
seat: review-2070, round 4. This overturns round 3's `merge a9ba0b887`, and it turns
on one sentence of that verdict: "The other 42 of the 46 added sites are still
unpinned: they are the autofix's to pin, and the train's CI gate waits for mutation
to go green." The autofix has already had its pass, is now both event-gated and
loop-guarded shut at this head, measured two of those sites as SURVIVORS that no
driver kills, and cannot measure the other 40 at all. `mutation` is one of the 17
required status checks (ruleset 23698884, evidence/r4-required-state.txt), so a train
that waits on it waits forever. Round 4: `fixer.md` owes a re-cut, not a fourth repair.
The fix's own substance I did not overturn -- see "carried from round 3".

## Step 11 -- the shape of the red, from the lane's own log

`mutation` check-run **113706784751**, run **37895798439** (Tests, `event =
workflow_dispatch` at this head), job 06:53:30Z -> 06:54:07Z -- 37 seconds, and it is
shape (a), the unpinned-sites ratchet refusal, and nothing else:

    MUTATION TABLE REFUSED -- 4669 unpinned site(s) against 4624 at the ratchet base
    bd59a4af1b2616a7f00761a3769d22a335e4df7c, 45 of them added by this diff.

45 `ADDED UNPINNED` entries, deduping to 42 distinct sites, every one in
`custom_components/heatpump_optimizer/early_cutoff.py` (mutation-job-113706784751.log,
added-unpinned-head.txt). Not (b): no survivor-cap line in this lane. Not (c): no
`MUTATION TABLE INCONCLUSIVE`, and none is possible -- `main()` returns 1 at the
deterministic inventory stage (tests/mutation_table.py:3130-3145), before any clone,
baseline or mutant. **At this head no mutant was evaluated at all.** Re-derived here
at the head with the body's own cheaper detector, seconds, no mutant: 4669 / 4624 / 45,
identical (r4-cheap-detector.txt).
Pending at the head: **0**. Red: `mutation` only. `nightly-status` is **skipped** here
(113706748590), not red as round 3 wrote for `3ecb86ada`.

## The autofix pass already happened, and owes nothing more at this head

- At the parent `3ecb86adaf`, run **37890872462** (`pull_request`): `mutation` failed
  (113691279964, 05:56:06Z) -> `mutation-pin-plan` (113691507877) dealt 49 sites into
  9 shards -> all 9 `mutation-pins` jobs concluded success -> `mutation-autofix`
  (**113706657606**, 06:51:49Z -> 06:53:17Z) printed `allowed=True`, `shards merged:
  measured`, `AUTOFIX: changed`, committed 4 `killed_by` files as
  `a9ba0b887 "ci: pin killed mutants"` (06:52:09Z push), dispatched Tests/Hassfest/
  Validate/CodeQL, and reported `mutation-autofix: changed -- nothing owed to a human.`
  It touched no production, test or harness line (bot-pin-delta.txt).
- **Its own report: 6 sites driven, 4 pinned, 2 SURVIVED.** Job **113691831133** at
  06:51:42Z (r4-shard1-pin-report.txt):

      UNPINNED ...early_cutoff.py:224 BOOLOP -- lives
      UNPINNED ...early_cutoff.py:267 RETURN_DEL -- lives
      PIN KILLED: 4 pinned, 2 left unpinned (2 survived, 0 not started for the budget,
      0 timed out, 0 skipped) -- a survivor needs a killing check or a
      survivor_triage verdict, which no tool writes

  Both are still `ADDED UNPINNED` at this head. That is this contract's case (b): a
  live survivor at the head. The body carries neither a killing check nor a triage row
  for either -- `tests/mutation_budgets.json` is untouched by the entire PR
  (r4-pr-files.txt), so there is no `survivor_triage` entry anywhere.
- The other 8 shards measured nothing and stayed green. Shard 2 (job **113691831045**):
  `PIN SHARD 2/9 -- 5 of 49 site(s), split by anchor`, then `MUTATION TABLE REFUSED --
  no full-line comment in any file in the pool, so the run has no null control ...`,
  then `measure: skip-measure-failed, 0 anchor(s)` -- job conclusion success, artifact
  402 bytes (r4-shard2-refusal.txt; the autofix log lists shards 2-9 at 402 bytes each
  against shard 1's 896). `merge_pin_shards` (tests/mutation_table.py:1017-1061) takes
  the merged status as the MIN over `_SHARD_PRECEDENCE`, whose first element is
  `measured`, so one measuring shard folds eight refusals into `measured` -- which is
  how a job that evaluated 6 of 49 sites could say "nothing owed to a human". **That is
  an instrument finding for the root-cause seat, not this PR's defect; I name it here
  rather than build a check for it.**
- No second pass comes at this head, for two independent reasons. (i) Event: every run
  at `a9ba0b887` is `workflow_dispatch` -- Tests 37895798439, Hassfest 37895800934,
  Validate 37895803207, CodeQL 37895805427 -- and no `pull_request` run exists at it
  and none is held (`status=action_required` and `status=queued` both empty; the push
  step itself printed `##[notice]no action_required run at a9ba0b887... appeared within
  60s of the push; printing the after-state (fail-soft)`). `mutation-pin-plan`,
  `mutation-pins` and `mutation-autofix` each require `github.event_name ==
  'pull_request'`, and at the head all three are `completed/skipped`
  (113707329520, 113707330060, 113707330488). (ii) Loop guard: `tests/closure.py:2011-2020`
  `autofix_allowed()` returns True only when `commit_subject != loop_subject`, and the
  job passes `loop_subject="ci: pin killed mutants"` -- this head's own subject. So a
  `pull_request` run at this head prints `allowed=False / AUTOFIX: skip-not-allowed`
  and pushes nothing. ci-autofix.md: "**That wait is conditional: it holds only while
  the job reports that it is repairing.**" It is not repairing. The repair is the
  fixer's by hand.

## The hand route refuses too, for a reason in the tree

The refusal line tells you to run `python3 tests/mutation_table.py --pin-killed
--base origin/main`. I ran exactly that, unsharded, in a pristine detached worktree at
the head: `PIN KILLED -- 45 new unpinned site(s) against bd59a4af1... to drive`, then
rc=1 with `MUTATION TABLE REFUSED -- no full-line comment in any file in the pool`
(r4-pinkilled-hand-path.txt). Not a sharding flake. `null_for(pool)` reads the control
from the pool's own site files, and `null_control()` (line 2041) needs a whole-line
comment under 60 characters counting its indent. `early_cutoff.py` has 11 full-line
comments, 60 to 77 characters each -- so the file has no null control; `coordinator.py:487`,
`pump_arbiter.py:181` and `diagnostics.py:57` each have one (r4-nullcontrol.txt). That
is why only shard 1, whose dealt slice happened to hold the coordinator's site, could
drive at all. `coordinator.py:2416` is now pinned, so every remaining added site is in
`early_cutoff.py` and every pool of them -- sharded or not, and `--anchor` too -- has
no control and refuses before any baseline. `skip-measure-failed` is not in
`AUTOFIX_QUIET`, so a future pass that measured nothing would redden the job and say so.

## Step 14 -- the four `killed_by` rows the bot commit added are all earned

I re-ran every one with my own targeted mutant at the head (r4-mutant-run-notes.txt).
- `early_cutoff.py:238 RETURN_DEL` (-> `pass`), killed_by tests/structure.py:
  structure.py rc=0 PASSED clean (`max_class_loc 8810 <= 8810`), rc=1 with the mutant,
  `FAIL dead_top_level_symbols 2 > 1 (+1)` -- the failed=1 the row records. Real.
- `early_cutoff.py:301 GUARD_OFF` (-> `if False:`), killed_by tests/structure.py: the
  same single FAIL. Real.
- `early_cutoff.py:193 CMP_BOUND` (`>=` -> `>`), killed_by tests/features.py:
  features.py 3899 checks, baseline 1 failure, mutant 2 -- the new one
  "past MIN_OFF the plan's on goes through, and an off is never turned on". Real.
- `coordinator.py:2416 GUARD_OFF` (-> `if False:`), killed_by tests/features.py:
  baseline 1, mutant 3 -- "the cut reason outranks the unmetered tail freeze, which
  this install trips" and "a cut interval freezes the learners under the one
  early_cutoff reason". Real, and it matches the row's recorded rc=1 failed=3.
So no `metric-gamed` here. Worth naming what two of them are: the structure.py rows are
the dead-symbol ratchet noticing `_planned_room` / `_second_zone_cold` became
unreachable -- a true kill of a true redundancy, but not behavioural proof, and the
`301 BOOLOP` twin of the pinned `301 GUARD_OFF` is still unmeasured.

## The two survivors reproduce here, so the block is measured, not quoted

features.py, /usr/local/bin/python3 3.11.5 (python3.13 here has no `yaml` and dies at
features.py:20866 after 1778 checks). Baseline A: **1 of 3899** failed -- R9-F2.1 P3,
the BLAS solver float round 3 measured at `3ecb86ada` and attributed to the
environment, not to this diff. Every delta below is against that set, never against zero.
- **`224 BOOLOP`** (`and` -> `or`): 1 of 3899, exactly A's set -- nothing notices. And it
  is NOT an equivalent mutant: with `or`, an entity that exists and reads "off"
  short-circuits to True and `_plant_exempt` returns "defrost", exempting a step the
  clean code cuts. The only defrost fixture in the whole cut-off section sets
  `FakeState("on")` (features.py:60390; r4-defrost-coverage-gap.txt), so no check can
  see the difference. This site owes a **killing check** -- "a defrost entity reading
  off does not exempt the step" -- and the body's claim that "the behaviour each one
  guards is already killed by a named check" is false for it, twice over (CI's drive
  and mine).
- **`267 RETURN_DEL`** (`return None` -> `pass`): 1 of 3899, exactly A's set. This one IS
  semantically null: 267 is the last statement of `_cycle_guard` (def 253, end 267), so
  falling off the end returns None unchanged; no behavioural driver can ever kill it.
  Its honest disposition is a written `survivor_triage` row, which the tool says no tool
  writes. `231 RETURN_DEL: return None`, the terminal return of `_plant_exempt`, is the
  same shape and is in the same list -- expect it to live too.

## Body, head, records

- Steps 7/12: the live head is `a9ba0b8874092db8780f93fa290b282b5ce200b5` and has not
  moved since round 3 posted at 06:55:53Z (re-read 10:39:53Z, r4-head-recheck.txt). The
  body's Head section names `3ecb86adaf247f182679a175bd619fd363a5e35c`, its parent --
  unavoidable, since the delta is the bot's own commit, and that delta is 4 ledger files
  with no production, test or harness line, so round 3's substance survives the move.
- Step 11's shape obligation is met and I am not blocking on it: `prepr.sh` step 7d's
  `unpinned_line` asks only for a `## Unpinned sites` line per site 6d listed, and the
  body has one for all 46. The set arithmetic is exactly right: body 46 = the head's 42
  unpinned + the 4 the bot pinned, and nothing unpinned at the head is missing from the
  body (r4-site-set-arithmetic.txt). What fails is the disposition's truth: all 46 read
  "pinned by mutation-autofix" -- measured false for 2, structurally impossible for 40.
  `## Red checks` answers round 2's mutation red properly (the stale pin, the cheaper
  detector, the admission); the red this head still carries is answered only by that
  prediction. So this is not `root-cause-unanswered`.
- Step 13: GitHub says `mergeable_state: dirty`. Confirmed otherwise: `git merge-tree
  --write-tree origin/main a9ba0b887...` exits 0 with tree `77b48910b` and the drivers
  print `LEDGER-MERGE: resolved tests/closures.json` (231 / 536 entries merged as sets),
  no `MERGE-CLAIM: refused`. Not a conflict to block on. Measured against
  `origin/main = c518447eb` as fetched at 09:0x; main has since moved to `b2b6acd64`
  ("ci: record nightly kills"), so the train must re-derive it.
- Steps 4/5: no golden fixture moves; `VERSION`, the manifest version, `RELEASE_NOTES.md`
  and both claim files are untouched (r4-pr-files.txt). `tests/structure_budgets.json`
  moves 8817 -> 8810, a lowering -- the ratchet's allowed direction, and structure.py
  passes at the head.
- Beyond the red lane, this head cannot present a complete gate at all: **five** required
  contexts never ran here -- `budget-raise-gate`, `env-matrix`, `policy-docs`,
  `pr-contract`, `wave-script` -- because a `ci:` bot head writes no `pull_request` run,
  and `pr-contract.yml` and `budget-raise-gate.yml` have no `workflow_dispatch` to make
  up for it (`pr-contract-rerun.yml` re-runs an existing run, and its own runs "attach to
  the default branch's commit, so nothing here can be re-reported as a required context").
  `orchestrator.md` section 11: "Every gate lane ran. Absent is not green." Same root
  cause as the skipped autofix, and the same remedy: the branch needs a commit of its own.
- What the re-cut owes, cheapest first. (1) One full-line comment under 60 characters in
  `early_cutoff.py` gives the pin drive its null control -- without it no drive, sharded
  or by hand, can reach the other 40 sites at all; it is also the reason the bot stopped
  at 4. (2) A killing check for the `224 BOOLOP` defrost-off arm, which is a real
  behaviour the suite does not pin. (3) `survivor_triage` rows naming `267` and `231` as
  equivalent terminal `return None`s -- no tool writes them. (4) A body re-take: each of
  the 46 lines must say which of the three dispositions it actually gets, not what the
  bot will do.

## Carried from round 3, not re-measured here

The router move and its re-keyed pin, the D12-s2 retarget, the `switch_supply` fence,
the archscore `coord_footprint` 2587 -> 2589 attribution, the DST wall-clock kill, the
closed-loop table's plan-aware null control and the M17 coordinator-raw-value kill are
round 3's measurements of production lines this head carries byte-identically; I did not
re-run the gate or the mutation table (heavy lanes are CI's, cited by run and job id
above), and I re-ran 5 of 17 mutants, not all of them. What I re-took at this head:
structure.py (PASSED, 8810 <= 8810), the ledger refusal's three numbers, the site-set
arithmetic, `surfaces.py` -- **0 failing cells at baseline, 2 under `--perturb`**, the
committed harness, reproducing round 3's RESULT line exactly (r4-surfaces-baseline.txt,
r4-surfaces-perturb.txt) -- the two hand-route probes, and the four targeted mutants
above.

RESULT mutation 113706784751 (run 37895798439): unpinned-ratchet refusal 4669 vs 4624, 45 entries / 42 sites, exited at the inventory stage with no mutant evaluated; re-derived locally at the head, identical
RESULT mutation-autofix at head: 113707330488 completed/skipped (with pin-plan 113707329520, pins 113707330060) -- pull_request-gated, and loop-guarded on this head's own `ci: pin killed mutants` subject; its one pass (113706657606) printed `changed -- nothing owed to a human` and pinned 4 of 49
RESULT survivors at the head: early_cutoff.py:224 BOOLOP and :267 RETURN_DEL -- shard 1's own `2 survived`; reproduced with my own mutants: features.py 1 of 3899, identical to the clean-head baseline (whose single failure is R9-F2.1 P3, the macOS BLAS float)
RESULT pins: all 4 killed_by rows the bot commit added are real kills under my own targeted mutants (structure.py `dead_top_level_symbols 2>1` at :238 and :301; features.py +1 at :193 CMP_BOUND, +2 at coordinator:2416) -- no metric-gamed
RESULT hand route at the head: `python3 tests/mutation_table.py --pin-killed --base origin/main` -> REFUSED, no full-line comment in any file in the pool; `null_control(early_cutoff.py)` is None (11 comments, all >= 60 chars) while coordinator/pump_arbiter/diagnostics each have one
RESULT body vs head: `## Unpinned sites` has 46 lines, the head unpins 42, the bot pinned 4, set-equal both ways; every disposition reads "pinned by mutation-autofix", false for 2 and unreachable for 40
RESULT structure at head PASSED max_class_loc 8810 <= 8810; surfaces baseline 0 failing cells, --perturb 2 (round 3's figure re-taken)
RESULT gate at head: pending 0, red = mutation only, nightly-status skipped (not red), 5 required contexts absent; merge-tree origin/main vs head exit 0, LEDGER-MERGE resolved tests/closures.json, no MERGE-CLAIM refusal
Evidence: /Users/timmalmstrom/hpo-seats/review-2070/evidence
