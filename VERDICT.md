Fix review: blocked 6308498975f49b3ed0f152700ee7c23b242387f8 root-cause-unanswered: `mutation` is red at this head on a cause the body does not answer -- CI's own pin pass measured 7 sites on this fix's own lines as SURVIVORS (driven, no check killed) and left them with neither a killing check nor a `survivor_triage` verdict, while the body's `## Unpinned sites` disposes exactly those rows as "left to `mutation-autofix`", which the pass that produced this head refutes; 35 further sites were never driven (`skip-budget`) and no further bot commit can come to a dispatched head

bus-nonce: 3ebf74f9de93f41c1e6f2e88892713ac
seat: review-2066 (fix-review.md, round 5; rounds 1-3 never posted, round 4 posted as review/2066 5e4e7b591; this is round 5's finish at the live head)
evidence: /Users/timmalmstrom/hpo-seats/review-2066/evidence
measured at: 6308498975f49b3ed0f152700ee7c23b242387f8 (`ci: pin killed mutants`), code head 16c06fd32 unchanged beneath it. Base: #2065's head.
head.txt: /Users/timmalmstrom/hpo-seats/review-2066/evidence/head.txt

## Round-5 verdict draft: what survives it, and why the SHA changed

The draft (`VERDICT-r5.md`) was a `merge` at 4abbc7c453e69b9a21ab5c8e7f80daa19f990eda pending the bot's
pin commit. The head moved exactly as predicted, by exactly one commit, and I re-measured before
changing the verdict.

RESULT delta 4abbc7c4..630849897: `ci: pin killed mutants`, 35 files, 210 insertions(+), 0 deletions,
every path under `tests/mutation_ledger/killed_by/` -- **zero non-ledger files** (evidence/delta.txt).

RESULT cross-check from CI's own two table outputs: added-unpinned listing 67 lines at 4abbc7c4 ->
37 at this head; 30 lines left the set; **new unpinned sites introduced by the pin commit: 0**. A
ledger-only commit cannot add a site, and it did not.

RESULT therefore: the draft's measurements survive unchanged and **none needed re-taking**. The
acceptance rows (`selfmod_matched` 0/96 -> 96/96 1.000, `min1_running` 0/15 -> 15/15), probe 7
(0.751 -> 0.751, 0.750 -> 0.750), probe 5 (1.000 x3 -> 0.978/1.000/1.000), probe 6
`selfset_hourly` (1.600 -> 1.170), `selfmod_independent_4kw` (0.636 -> 0.780, ruled accepted), the
true-COP rows (0.604/0.704/0.805/1.307, `true_0.7_reload150` 0.704), probe 4 `follow_noise20`
(1.118 -> 1.123, the one disclosed in-tolerance fold) and probe 3b (0.636 -> 0.590 during the first
48 running samples) were all taken at a tree whose production lines this commit does not touch. The
logic accepted in rounds 3-4, the null-control reading, the `brief_lint` fixture argument (my mutant
of the anchored rule still reddens it: rc 1 `FIXTURE VACUOUS ... wood_share:1152`), the version/
manifest/notes check and the forward-carry both remain as written, and carry to this head.

RESULT merge-tree: `git merge-tree --write-tree origin/main <head>` rc 0, no CONFLICT line, no
`MERGE-CLAIM: refused` marker. Not DIRTY (step 13 does not bind).

## Step 11 at the settled head -- and the one number that turns the verdict

RESULT settled: 30 check-runs, pending 0 at 2026-10-09T09:23:59Z (evidence/settle.log, 5 polls at
300 s; evidence/checkruns-settled.tsv). One run per name, no red-then-green hidden: the only Tests
run at this head is 37905550514, `run_attempt` 1, event **workflow_dispatch** (the autofix retrigger),
conclusion failure.

Green at this head, with run ids: recheck-gate 113738022229, closures 113738022637, **fast (3.14)
113738072766**, coverage 113738072749, coverage-ratchet 113748475506, briefs 113738072810, typing
113738072747, browser 113738072738, hassfest 113738032304, validate-hacs 113738041529, nightly-ha (2025.2.0) 113738022618,
CodeQL 113738283770, Analyze 113738052857 / 113738053625 / 113738053186.
Red: **mutation 113738072853**, **nightly-ha (stable) 113738022964**.
Skipped: mutation-autofix 113738323073, mutation-pin-plan 113738322164, mutation-pins 113738322953,
mutation-ledger 113738074361, mutation-ledger-push 113738075513, mutation-nightly 113738075219,
nightly-status 113738023557, slow 113738075315, closure-scope 113738023731, claims-autofix
113754885638, closures-autofix 113750910897, record-autofix 113738053342, graders-head-copy
113748477639.

`fast (3.14)` is green, so round 4's two `fast` reds (the stale `killed_by` re-key and the retired
`draw_range_evidence.py` in `tests/layout.py`) are closed at this head. That is the draft's blocker 2
resolved by measurement, not by argument.

### `mutation` -- the refusal is real, and its cause is a survivor, not a missing pin

RESULT the lane's own output (artifact `mutation-table` of job 113738072853, step 5 "Drive the table
over what this diff tested", failed 08:33:04Z; evidence/artifacts-mutation-table/mutation-table.txt):
`MUTATION TABLE REFUSED -- 4647 unpinned site(s) against 4624 at the ratchet base 47b083b03…, 37 of
them added by this diff … record it under killed_by or survivor_triage and the count falls back.`
Not the INCONCLUSIVE baseline trap: that path prints `MUTATION TABLE INCONCLUSIVE` and exits 0
(step 11's note); this prints a REFUSED and exits 1, and the 41-second wall is the source-only
inventory before any driving, exactly as at 4abbc7c45 (4683 against 4624, 67 added; evidence/
artifacts-mutation-table-4abbc7c4/).

RESULT the bot's pass is finished and did not run out of measurement silently: at 4abbc7c45 the pull_request
run 37891964244 ran `mutation-pin-plan` (success) and **10 `mutation-pins` shards, all with status
`measured`** (shard 1 job 113695181917, 2 = 113695181960, 3 = 113695182059, 4 = 113695182065,
5 = 113695181935, 6 = 113695182015, 7 = 113695182040, 8 = 113695182038, 9 = 113695181923,
10 = 113695182210; artifacts in
evidence/pins/shard-*/, logs in evidence/logs/). Their own summary lines, per shard:

    s1  8 to drive -> 4 pinned, 4 left (0 survived, 4 not started)
    s2  8 -> 4 pinned, 4 left (4 survived, 0 not started)
    s3  8 -> 3 pinned, 5 left (0 survived, 5 not started)
    s4  9 -> 3 pinned, 6 left (1 survived, 5 not started)
    s5  8 -> 2 pinned, 6 left (0 survived, 6 not started)
    s6  8 -> 7 pinned, 1 left (1 survived, 0 not started)
    s7  7 -> 4 pinned, 3 left (0 survived, 3 not started)
    s8  8 -> 2 pinned, 6 left (0 survived, 6 not started)
    s9  7 -> 5 pinned, 2 left (1 survived, 1 not started)
    s10 7 -> 2 pinned, 5 left (0 survived, 5 not started)

RESULT 78 sites driven at: **36 pinned, 42 left = 7 `lives` + 35 `skip-budget`**. The tool's own words
on the survivors: "a survivor needs a killing check or a survivor_triage verdict, **which no tool
writes**"; on the budget shards: "no survivor: a later run drives the rest". The 42 leftovers are
therefore two different debts, and only the first is the fixer's to hand to a bot.

The 7 driven survivors, and the disposition this body gives each (evidence/unpinned-verdicts.txt):

    accuracy.py:678   CLAMP_DROP   body: `mutation-autofix`
    accuracy.py:680   RETURN_DEL   body: `mutation-autofix`
    coordinator.py:4501 CLAMP_DROP  body: NOT NAMED anywhere in `## Unpinned sites`
    coordinator.py:4532 CMP_BOUND   body: NOT NAMED anywhere in `## Unpinned sites`
    draw_range.py:111 CMP_BOUND    body: "#2065's, inherited; disposed in #2065's own body"
    draw_range.py:216 CMP_BOUND    body: `mutation-autofix`
    draw_range.py:51  CONST        body: "#2065's, inherited; disposed in #2065's own body"

RESULT all 7 verified unpinned **at this tree** with main's own read-only instrument
(`mutation_table.listed_sites`, no driving, no writes; evidence/list_unpinned.py): each returns
`UNPINNED at this head (no killed_by, no survivor_triage)`. Five of the seven are in the head's own
37-site listing; the two `coordinator.py` sites are not, and I did not establish why (the lane counts
`added by this diff` by a scope rule I did not re-implement) -- I report them as measured survivors
with no disposition, not as listing entries.

That is why the draft's `merge` does not survive the head. These are not "unpinned sites the bot
should have cleared": the bot cleared what it could clear, and what is left is a coverage claim about
this fix's own lines. `accuracy.py:678` is the duty-floor comparison the PR exists for; its `GUARD_OFF`
twin got pinned (`MeasuredCop.judge_floor GUARD_OFF 566a681f`) while its `CLAMP_DROP` **lives**;
`draw_range.py:216` likewise (GUARD_OFF pinned, CMP_BOUND lives); `draw_range.py:51` is
`MIN_SAMPLES = 48`, the constant the body's own probe table turns on twice
("47 samples give None, 48 give True") and which probe 3b's disclosed 0.636 -> 0.590 depends on.
A mutant no check kills on the line the fix moved is exactly the number the ledger exists to price.

The body's `## Unpinned sites` carries no `survivor_triage` verdict for any of them and no killing
check for them; it defers them to `mutation-autofix`. CI has now measured that the deferral fails:
the job's summary at 4abbc7c45 reads `mutation-autofix: changed -- nothing owed to a human.` (job
113737880799) -- green tick **and** green summary line, so the repair did happen and this commit is
its output -- and `apply_pins` pins only measured kills. At this head mutation-autofix,
mutation-pin-plan and mutation-pins are all `skipped`, because their `if:` requires
`github.event_name == 'pull_request'` and this run is the bot's `workflow_dispatch`. **No further
bot commit can come to this head**: the 35 `skip-budget` sites need a push from the fixer to get
another pins pass, and the 7 survivors need a human disposition either way
(`ci-autofix.md`: "Do not automate survivor triage"; "When `mutation-autofix` goes red, run
`--pin-killed` yourself").

So the root-cause trigger for this head's red is unanswered in the sense the rule means: the body's
`mutation` entry answers round 4's stale-re-key cause (and that cause is now closed -- `fast` and the
re-key are green) and names no cheaper detector and records that none exists for the survivor class.
I did not run the driving lane; per tvofi's standing rule the heavy numbers above are CI's, cited by
run id.

### `nightly-ha (stable)` -- ran here only because this head is a dispatch; its failure is the lane's instrument

RESULT the job executed, not skipped, at this head (steps: "Pull the Home Assistant image" success,
"Run the integration inside Home Assistant" failure, floor-names verify skipped). Its `if:` runs the
lane on `schedule`, `workflow_dispatch`, or a `pull_request` whose `closure-scope` output says
`nightly_ha == 'true'`; measured at 4abbc7c45's pull_request run 37891964244 the lane is `skipped`,
and `closure-scope` is `skipped` at this head too -- so the branch's own diff does not reach what the
lane reads, and the run here is the dispatch's.
RESULT the two failures, from the job's own log (evidence/logs/nightly-ha-stable-head.txt):
`FAIL hb:positive_control [a 600 ms spin read as 600.2 ms; dump names the spin: True; py-spy rc=0
names it: False]` and `run:exit_status [the container exited 1]`, the second a consequence of the
first. 62 of 64 checks passed, including every substantive assertion this fix could move:
`entry:loaded`, `entities:registered` (51), `a3:roster` (79/79, missing=[], extra=[]), `a9:reload_*`
(5/5), `plan:*`, `a4:*`, `a16:*`, and the whole contract set (61 + 94 + 22 comparisons passed). The
failing check is the py-spy heartbeat positive control (#1758), an instrument of the lane.
RESULT not this pull request's, on the exemption's reasoning (`defect-root-cause.md`: a lane that
grades outside this diff): main's own 2026-10-08 scheduled run 37753990323 failed **both** arms, and
its 2026-10-09 scheduled run 37909555545 passed both -- a live flakiness/repair history on `main`, on
the arm that failed here. And `git diff --stat 47b083b03 origin/main -- tests/nightly_ha.py
tests/ha_floor.py .github/workflows/tests.yml custom_components/` is **empty**, so main carries no fix
this branch lacks and no change to what the lane reads.
The body does name and answer this check, so step 11's trigger is not breached for it; but one half of
its answer is now measurably false: "This PR's heads skip that lane" held for `pull_request` heads and
does not hold for this head, which is a dispatch. Correct that sentence when the body is next taken,
and name the arm (`hb:positive_control`, py-spy) rather than the ancestry.

`nightly-status` 113738023557 is `skipped` at this head and is main's lane; the body names it. No
breach.

RESULT range sweep (step 11's "the head's runs are not the range's"), branch `fix/cop-duty-floor`,
Tests runs: 9d77a97b1 37865588177 reds = nightly-status, mutation, fast (3.14), briefs; 4abbc7c45
37891964244 reds = nightly-status, mutation; 630849897 37905550514 reds = mutation, nightly-ha
(stable); 2c1ea2dad / 1d011c887 / 588692957 cancelled by the next push, no reds to answer. **Every
one of those contexts is named in the body's `## Red checks`**; the only one whose answer does not fit
its cause at the head is `mutation`, which is this block.

## Step 14 on the 35 new rows -- the pins are earned, so this is not metric-gamed

RESULT every one of the 35 rows' `old` text is present verbatim in the module its anchor names: 0
missing, 0 read failures (loop over the 35 paths, evidence/delta.txt for the file list). Killed_by
distribution: `tests/features.py` 30, `tests/structure.py` 3, `tests/entities.py` 2.

Two spot-kills, my own mutants at the named sites, run in my detached worktree at this head and
restored (evidence/spotkill*.out; `git status --porcelain` empty after each):

1. `coordinator.py:4459` `if refusal := MeasuredCop.judge_floor(commanded, self._measured_power,
   params):` -> `if False:` (the row's own GUARD_OFF form, key
   `HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c31691cd`, named killing check
   `tests/structure.py`). Baseline my run: **rc 0, STRUCTURE RATCHET PASSED** (5 s,
   evidence/base-structure.out). Mutant: **rc 1** -- `FAIL dead_methods 1 > 0 (+1)`, naming
   `_solve_failures: coordinator:_note_solve_failure`. The row's claim (rc0/failed0 -> rc1/failed1)
   reproduced: **1 failing check**.
2. `draw_range.py:216` `if high < FOLLOW_ASK_SPAN * low:` -> `if False:` (key `follows_ask GUARD_OFF
   695c3a8d`, named check `tests/structure.py`). Baseline rc 0; mutant **rc 1** --
   `FAIL dead_top_level_symbols 2 > 1 (+1)`. Claim reproduced: 1 failing check.

RESULT neither row is "pinned without a killing check": both named checks go red on my own mutant, so
`metric-gamed` does not apply to the ledger, and I found no movement that is the instrument's rather
than the change's. The commit removes nothing (0 deletions) and adds only dispositions for sites the
inventory already held, so the count fell (4683 -> 4647) by measurement, not by deleting a site.

One thing the two spot-kills do show, and the orchestrator should price rather than celebrate: both
kills came through `tests/structure.py`'s dead-symbol ratchet, not from a behavioural assertion --
turning the guard off makes a helper unreachable and the ratchet refuses the growth. That is a real
refusal of the mutant, and it is what the ledger records, but it is the weakest of the three kinds:
behavioural coverage for those very lines is what the surviving `CMP_BOUND` twins at
`accuracy.py:678` and `draw_range.py:216` say is missing. I could not drive the 30 `features.py` rows
or the 2 `entities.py` rows myself: both import the `homeassistant` package (`tests/entities.py` at
this head dies at `tests/harness.py:25` for want of it, evidence/base-entities-314.out), the container
lane was retired 2026-10-04, and the standing rule is to cite CI's heavy runs. Their evidence is the
pass's own measured `reason` strings (baseline rc=0 failed=0 -> mutant rc=1 failed=N) plus main's
`measurement()` guard, which refuses the `measured` status unless the base program's own
`PIN KILLED:` count matches the ledger diff it uploaded -- the #523 class, closed by #1599's review.

## What the fixer owes to clear this

1. A disposition for each of the 7 measured survivors: a `features.py` (or `entities.py`) check that
   kills it, or a `survivor_triage` entry with a verdict -- the tool cannot write it and no bot will.
   The two `coordinator.py` sites and `draw_range.py:51 CONST` are the ones I would look at first:
   `MIN_SAMPLES` at 47/48 is the boundary the body itself quotes as tested, yet the CONST mutant at it
   lives.
2. A push, any push, to get the 35 `skip-budget` sites driven by a real `pull_request` pins pass --
   they are not evidence of anything yet; they are unbilled work the ratchet still counts.
3. The body re-taken: the `mutation` entry's answer is for round 4's cause; the 7 survivors need the
   cheaper-detector-or-none-exists sentence, and the `nightly-ha (stable)` sentence "This PR's heads
   skip that lane" needs the dispatch correction above.
4. Everything else in the draft stands. The logic, the harness and probe rows, the null controls, the
   `brief_lint` fixture argument, the version check, the forward-carry (both `carry-2066.json` and
   `carry-2065.json` verified present as written in rounds 3-4) and the stack ordering -- #2065 must
   merge first, and #2065's head has since moved again (1e957282e -> 3c9fe53fa), which this branch
   does not carry; the merge base is still 47b083b03.

I am not approving, not marking ready, not merging; the PR stays a draft. Class chosen:
`root-cause-unanswered` is the taught word for "the fix is sound, the branch turned a check red, the
body owes the answer" -- but the debt here is also a repair (7 dispositions), so the fixer should be
resumed with items 1-3, not only the root-cause seat.
