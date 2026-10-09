Fix review: merge c54beab894db7210c570cd67f7cfb61212ed301c

Round 3.
seat: review-2074c
bus-nonce: 7f7c7f4f8ce8769fc6646f18fb01c54a
Measured at `c54beab894db7210c570cd67f7cfb61212ed301c` in a detached worktree at
`/Users/timmalmstrom/hpo-seats/review-2074c/wt`; merge base `b2b6acd64`.
Python 3.14.7 (`$HOME/.local/state/hpo/venv-ci/bin/python3`).
Evidence: /Users/timmalmstrom/hpo-seats/review-2074c/evidence

**Contract currency, named rather than assumed.** `git diff $(git merge-base
origin/main HEAD)...origin/main -- dev/governance/roles/` is **not** empty this
round (`fix-review.md` step 7's `--carry` amendment; `fixer.md` step 5's
`run_always` wording and step 7's), so the copy I executed is `origin/main`'s —
`git show origin/main:dev/governance/roles/fix-review.md | diff - /private/tmp/r9-main/...`
is byte-identical. Steps 7, 11, 12, 14, 15 were taken against that text. The body
read the same diff and states the same obligations; `fixer.md` step 5's new words
are accurate: `tests/run.sh` has exactly four `run_always` **call** sites (427
`env_drift.py --claims-only`, 430 `closure.py selftest`, 507 `harness_headers.py`,
511 `layout.py`; the fifth grep hit is the function's own dispatch at 274), and I
re-ran two of them (claims hygiene `b2b6acd64... ok`; `ALL 57 closure shrink pins
PASSED`), citing CI for `harness_headers.py` and taking `layout.py` whole myself
(rc 0, guard findings 0 at this head vs the base).

**My instrument, disclosed** (`fix-review.md` step 9 — mine, not the fixer's, and
not a re-implementation): `evidence/review_block3.py` execs the tree's own
`tests/entities.py` lines **31594..31801 verbatim**, each boundary found by its own
line marker rather than a carried number, with `_workflow_job`, `_TESTS_YML` and
`_MUT_BODY` lifted verbatim the same way, `mutation_table` imported as the tree
imports it, and the four stdlib aliases bound to the modules the file binds them
from. Arms are applied to the files **on disk** and restored with `git checkout
HEAD --`, every run ending `git status --short` empty and `git diff --quiet HEAD`
clean (proved in `evidence/arms_C_D_A_B_REVERT.txt` and after the single-arm runs).

## The delta, measured

`git log --oneline 96497ffc6..HEAD` is one commit; `--stat` names four files —
`.github/workflows/tests.yml` (20), `tests/entities.py` (21),
`tests/mutation_table.py` (27), `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` (89).

- **The workflow edit moves no behaviour, and I checked it by filter.** Every
  `+`/`-` line of that diff outside the headers matches `^[+-][[:space:]]*#`; my
  non-comment filter printed nothing. The two rounds' opposite-sounding statements
  are both true of their own ranges: round 2 read
  `git diff 7e8c5c8e4 96497ffc6 -- tests/mutation_table.py .github/workflows/tests.yml`
  as **empty** (the round-2 delta moved neither), and this round's delta moves both —
  as comment only. It is still `/.github/workflows/` text, which
  `.github/CODEOWNERS:91` owns to `@tvofi`, so **the owner's approving review at this
  head is owed and this verdict is not it**.
- **`tests/mutation_table.py` and `tests/entities.py` are AST-identical to
  `96497ffc6`'s with docstrings stripped** (my own `ast.dump` comparison:
  `mutation_table: lines 3706->3715 AST identical: True`,
  `entities: 34147, identical: True`), and the only docstring that moved in either
  file is `seed_pool_seconds`' (`docstrings changed: ['seed_pool_seconds']`; entities: `[]`).
  So `driver_timeout` and `seed_pool_seconds`' code did not move and round 1's bound
  arithmetic needed no redo — I re-derived it anyway (below).
- `git diff b2b6acd64...HEAD -- tests/closure.py` = **0 lines**; `TIMEOUT_SCALE = 3`
  and `closure.SECONDS_BAND = 2.0` read at this head. The PR's file list is
  unchanged from round 2 (six paths).

## Round 2's two blocks: both closed

**(a) §7's arm record.** `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md:429-437` is a
seven-row table — clean, revert, A, B, C, D, E — each row naming what it breaks, the
check it reddens, its tally and its log; the round-1 `2239` tallies survive at 443-447
under "those four tallies are the round-1 head's". I read round 1's four logs:
`entities_FAILINGARM.txt` "3 of 2239", `entities_MUTA.txt`/`entities_MUTB.txt`
"1 of 2239", `entities_FINAL.txt` "ALL 2239 ENTITY CHECKS PASSED" — the labels are
true. Round 3's seven logs print `ALL 2241` / `4 of 2241` / `1 of 2241` x5, as the
table states.

I did not take the portability argument on reading — **I ran all seven arms at
`c54beab89`** (`evidence/block_CLEAN_AT_HEAD.txt`, `block_{REVERT,A,B,C,D,E}.txt`):
CLEAN 0 of 7; REVERT **4 of 7** (the three defect checks *plus* the driver pin, both
null controls and the workflow pin green — the body's arm exactly); **A** 1 of 7
with its detail printing `driver_timeout(1200, max(800.2, 2401.0)) = 2401, need >=
7203.0`; **B** 1 of 7 (verdict back to "Fix the suite first", "STALE" gone);
**C** 1 of 7 (`missing=` naming `--pool-seconds` in `mutation-nightly` AND
`mutation-ledger`); **D** 1 of 7
(`missing=['own_s = seed_pool_seconds(recorded_seconds(), prior_pool)']`); **E** —
the arm this dispatch asked me to run — **1 of 7** through the adjacency regex
(`missing=[]; save-if-always=False`), not the step name. Each red is the one row the
table names for that arm.

Its supporting claims each check out: `git diff 90ef590d8..HEAD --name-only` prints
`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` alone and the diff of the three code
files between them is empty; `grep -n R9-NIGHTLY-MUTATION-BOUND tests/entities.py`
returns 31576 and 31593, both `#` lines; `tests/layout.py:310` `GUARD_EXEMPT` names
`dev/audit/rca/` and is consumed as `path.startswith(skip)` (403/430, 466/467);
`fold_ledger._intree` (196-197) is `startswith(RCA_DIR + "/") and os.path.isfile(...)`
— a stat. `dev/audit/` is an INERT prefix (`tests/closure.py:297`, its comment:
"prose and evidence no gate script opens"), so `tests/entities.py`'s classification
check accepts the new file; `tests/closure.py` never globs `dev/audit/rca`.

**(b) The superseded pool factor.** `git grep -nE '1\.3[-–]3\.3'` over this head
returns **nothing** (exit 1): no surviving hit of the dead claim. The four lines now
carry `0.47x-3.27x` with the rule and a resolvable `§2` citation —
`tests/mutation_table.py:136-143`, `:2883-2898` (inside `seed_pool_seconds`'s
docstring), `.github/workflows/tests.yml:1083-1094`, `tests/entities.py:31572-31593`;
`pool_seconds`' own docstring, which round 2 did not list, carries no stale figure
either (read: it names the two driver rows, not a range). The `0.3x-3.4x` grep
returns three hits, each correctly labelled: `tests/closure.py:1537-1539` — the
source, and it reads "Recordings of one script vary **0.3x-3.4x run to run**", which
is recording variation, the band's own reason (`SECONDS_BAND = 2.0` beside it, with
"60 of 72 rewrites over 21 merges were inside 2x"); the RCA doc:223, quoting tvofi's
reason in those words; and the new `entities.py:31576-31579`, which says in terms
that figure "states how much one script's RECORDINGS vary run to run ... two
different quantities, and conflating them is how the figure this replaces travelled".
The other `3.3x` hits (`tests/stress.py:562`, `:1793`, `bugclasses.json:1432`) are
the scenario call-growth budget — a different quantity, correctly untouched.

## The two figures that had no enumerator, re-derived by me

- **Factor range.** I fetched two of the three logs myself and applied §2's rule
  (pool ÷ the committed solo at *that run's* head, excluding the `env_drift.py`
  stub and any solo under 1 s):
  `112708109605` (head `be0cb8213`) — 23 rows parsed, **16 kept**, 7 excluded
  (`env_drift.py` stub; `guard_pins.py` 0.9, `open_meteo.py` 0.3, `plan_view.py`
  0.9, `solar_alignment.py` 0.9, `typing_ruler.py` 0.3, `wood_advisor.py` 0.8);
  min **0.4653** (`harness_headers.py` 449.2 -> 209), max **3.0002**
  (`boost_drift_replay.py` 525.3 -> 1576, **rc 124** — a floor, as §2 marks it);
  `112708109541` — **16 kept**, same min, max **3.2692** (`structure.py` 5.2 -> 17,
  rc 0, uncensored), and `boost`'s one uncensored row 1573/525.3 = **2.9945**, the
  doc's "2.99, three seconds of margin". Both logs' row counts, both ends, both
  drivers and all four inputs match §2's per-log table exactly. I did **not**
  re-take the third log's 19 rows; `16+16+19 = 51` is the doc's arithmetic over a
  population round 2 enumerated whole.
  I also checked §2's 10-08 table against the committed table at its own head
  `816547efe`: all seven **solos and all seven bounds** are mine from
  `git show 816547efe:tests/closures.json` through the tree's `driver_timeout`
  (2401/1200/1200/1200/1851/1200/1200, matching the table), and the factors follow
  from its pool column (3.0005/2.7327/2.2800/2.2807/0.6973/0.7121/1.2635) — that
  column I took from the doc rather than re-reading the third log's 19 rows, as
  above. The §6 note added this round (`env_drift` stub 0.6 at `816547efe` and
  `be0cb8213`, 0.9 at the merge base) reads correctly at all three heads.
- **Cron-to-dispatch delay.** The body's own twelve-run query, `created_at` minus the
  `02:17Z` `tests.yml:119` declares (line read): **5 h 54 m 57 s**
  (`37108891698`, 2026-10-03T08:11:57Z) to **6 h 53 m 23 s**
  (`37909555545`, 2026-10-09T09:10:23Z) — the doc's ends, both re-taken, with the
  rule and per-run print in `evidence/delay_mine.txt`. §4 now states the rule and
  labels the diagnosing seat's narrower "6 h 19 m - 6 h 53 m" as the same rule over
  four runs, which is the honest form.
- **Bounds** (`evidence/bounds_and_seeds_mine.txt`, the tree's own `driver_timeout`):
  `1200 / 1200 / 1200 / 2297 / 1576 / 2401 / 4469` for `2e569748a fb11a0172
  a1da8d381 cff39dad6 be0cb8213 816547efe c518447eb`; seeded `4719 / 7200 / 7203`;
  `driver_timeout(1200, 0.0) = 1200`; seed-never-lowers holds over all three pools.
  Voided lane work from each job's own stamps: **63.4 / 64.2 / 72.4 min** ✓ (§4).

## Item 8, checked against CI rather than read for plausibility

§1's table now carries **10-06** with the bound derived from that head's own
committed recording — `cff39dad6 {seconds: 765.6, rc: 0}` -> **2297** (my number, not
the doc's) — and the row says both mutation lanes were green, which I confirmed from
run `37440269774`'s jobs: the only `failure` is `record-autofix` (job `112192034609`)
and `mutation-ledger` `112192036224` / `mutation-nightly` `112192036397` both
`success`, so "neither evidence for the mechanism nor against it" is right.
The streak-end sentence says `37909555545` (head `c518447eb`) concluded **success**,
ending the streak **without this fix**, "on the luck of that re-recorded number". I
tested that: at `c518447eb` the recording is `1489.6` -> bound **4469**, and that
night's lanes printed `baseline tests/boost_drift_replay.py: rc=0 failed=0 **2416s**`
(job `113751143057`) and `**2492s**` (job `113751143182`) — **both above the 2401 s
bound that killed the same driver on 10-08**. So the mechanism was still live and
only the higher bound carried the night: the document understates its own case, and
the fix is indeed still owed. (`evidence/streak_end_1009.txt`,
`ev/my_1006_*.txt`.)

## Step 11, the checks at this head

CI settled at this head, polled every 300 s from 18:56:40Z to **19:31:51Z** (8
polls; a failed or short fetch is retried, not counted as settled —
`evidence/ci_poll.log`, `checkruns_poll_1..8.tsv`). From `check-runs` at
`c54beab89` (`evidence/checkruns_final.tsv`, 40 runs / **38 distinct names**,
latest per name) against the 17 required contexts read from ruleset
`23698884 main-protect-checks` (`evidence/ruleset_raw.json`; they live at
`rules[].parameters.required_status_checks` — this repo answers
`404 Branch not protected` on the branch-protection endpoint, so the ruleset is the
only place the required list exists, and `conditions` carries only `ref_name`):

- **all 17 required contexts ran and concluded `success`**: `fast (3.14)`, `browser`,
  `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`, `validate-hacs`,
  `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`, `Analyze (actions)`,
  `Analyze (javascript-typescript)`, `Analyze (python)`, `mutation`,
  `budget-raise-gate`. **ABSENT: none. NOT-SUCCESS: none.**
- Nothing else in the range is red either. Of the 38 names, **14 are `skipped`** —
  the expected PR-only arms (`closures-autofix`, `claims-autofix`,
  `mutation-autofix`, `record-autofix`, `record`, `recheck-gate`, `slow`,
  `nightly-ha`, `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push`,
  `mutation-pins`, `mutation-pin-plan`, `delivery-status-publish`) — and **7 more
  succeed** beside the required seventeen: `nightly-status`, `delivery-status`,
  `coverage`, `coverage-ratchet`, `graders-head-copy`, `instrument-self-tests`,
  `CodeQL`. So **nothing is red at this head, and the previous head
  (`96497ffc6`) answers the same way** (scanned with the same filter: no
  non-success conclusion), which means the body's `## Red checks` owes nothing
  further for this range.
- **The non-exempt `nightly-status` arm is answered**: this diff touches
  `.github/workflows/tests.yml`, which that reporter reads, and the body names the
  detector (`nightly_status.py` grades `main`, fails closed, no cheaper one), the
  standing cost (none added) and the remedy (the orchestrator's on `main` — fix the
  lane, then dispatch Tests on the default branch). Here it is `success` anyway,
  because the 10-09 nightly ended the streak.
- **`mutation` is green, and I read its own log this round** (the one number round 2
  relied on round 1 for): job `113966243112` prints `--scope changed --base
  origin/main --max 10 --jobs 3`, then `MUTATION TABLE -- scope changed: no
  production code line added or modified against the base` / `MUTATION TABLE PASSED
  (empty scope)` — "none was evaluated", not "no mutant survived"
  (`evidence/mutation_lane_log.txt`).
- **The whole-file citation, and the two numbers a reader will meet.** `fast (3.14)`
  (job `113966243087`) checks out `3c8c2b1f Merge c54beab89 into d0f085ff` — the
  merge of this head into *current* main, which is what a `pull_request` run is — and
  prints `ALL **2243** ENTITY CHECKS PASSED` with all seven `RCA-1565 …` lines `ok`
  (`evidence/fast314_checkout.txt`, `fast314_rca_lines.txt`). The record's **2241**
  is this head alone: every whole-file run in the seat's logs prints 2241, including
  `entities_R3_HEAD_FINAL.txt` (mtime 19:51, after the 19:35:48 commit), which I read
  but did not re-take, because CI's lane is the citation and step 11 forbids
  repeating it. The 2-row difference is **main's side of that merge ref**: main has
  moved `tests/entities.py` since the base (`git log b2b6acd64..origin/main --
  tests/entities.py` names `d7a5634a1 test(R9-CI-2b): pr-contract accepts the
  merge-main bot's automatic merge…`, which adds fixture cases), while this branch
  adds seven (`R.check(` literals: 1693 at the base, 1700 at the head, 1694 at
  main). The printed total is not the literal count — some checks execute from a
  loop over fixture cases — so I can say the +2 comes from main's newer cases but not
  decompose it further, and I did not try. **Neither number contradicts the record,
  but a seat comparing §7's tally with the `fast` log will see 2241 against 2243 and
  nothing in the tree says why** — half a line in §7 would close that.

## Step 13, and the hygiene a ratchet-bound repo owes

`git merge-tree --write-tree origin/main c54beab89` (against the **moved** main,
`d0f085ffb`) exits **0**, tree `d03f9702e`, stderr empty — no conflicting path, no
`MERGE-CLAIM: refused`, nothing for the driver to resolve. `mergeable: true`,
`mergeStateStatus: BLOCKED` = draft + code-owner review, not a conflict.
Both claim files are 0 diff lines against the base (`git diff --name-only
b2b6acd64...HEAD -- tests/golden/` empty) and against main's tip the difference is
main's own newer content, exactly as the body says; `env_drift.py --claims-only
b2b6acd64` -> `claims hygiene: b2b6acd64... ok`. No `*_budgets.json` in the diff;
`VERSION`, `RELEASE_NOTES.md`, `hacs.json`, `custom_components/**` untouched
(three-dot counts all 0) — step 5 ✓ and step 4 has no moved fixture to reconcile.
`tests/structure.py` -> **STRUCTURE RATCHET PASSED** (`seam_cut_total 760 <= 760`,
`max_class_loc 8817 <= 8817`), and its class metrics are measured over
`custom_components/**` only (`tests/structure.py:21`, `:1720`), so the nine comment
lines added to `tests/entities.py` move nothing — step 14 finds no instrument this
delta touches, and the `2239 -> 2241` movement round 2 paid for is still earned:
I made each of the two pins bite. `fold_ledger.py check` -> `28 classes, 549
instances, 39 in-tree judge survivors (rounds [8]), 101 rca entries / 0
violation(s)`, with `RCA-1565-mutation-timeouts` `status: done`,
`parts_missing: []`, the (c)+(d) `process_state`, the (iv) refusal in
`countermeasure`, and `doc`/`in_tree_home` naming the RCA file.
`dev/programme/delivery/2074.md` still reads **open** ✓.

## Reported, not blocking (four wording defects; no number depends on any of them)

1. **§7's provenance names two SHAs that no remote ref carries.** `90ef590d8` and
   `51ed9aee7` are the first two amends of this same round-3 commit: `git show -s
   --format=%p` gives all three the single parent `96497ffc6`, and `git
   merge-base --is-ancestor` refuses both, so they are siblings, not ancestors, and
   "Every commit after `90ef590d8` in this series" describes an ancestry that does
   not exist. Worse for a later seat: a fresh `--filter=blob:none` clone of the live
   remote **cannot resolve them** (`git cat-file -e 90ef590d8` -> "not a valid
   object name"; `git fetch origin 90ef590d8` -> "couldn't find remote ref"), so the
   paragraph's own check command is unrunnable off this machine. I verified the
   substance both ways — tree comparison *and* re-running every arm at the head — so
   the demonstration does not rest on those objects; the record should cite
   `96497ffc6` plus the byte-identity I measured instead of dangling SHAs.
2. **"no check reads this file's contents" is wider than the tree.** Each of the
   three instruments named is exactly as described, and none can move these tallies.
   But `tests/layout.py`'s `check()` **reference** arm greps *all* tracked text for
   retired-path citations and its `skip` (line 223) does **not** carry
   `GUARD_EXEMPT`. I proved it: planting `site: tools/audit/app_approve.sh` in this
   document (staged, then restored, worktree clean) moved the arm from 1289 to 1290
   findings and printed `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md:474 cites retired
   path tools/audit/app_approve.sh; use tools/pr/app_approve.sh`
   (`evidence/layout_probe_staged_citation.txt`). That arm is REPORT mode ("exit 0 on
   findings until R9-RO-9"); the enforcing `guard()` arm does exempt the prefix (its
   findings at this head: 0). So the inference stands and no figure moves, but the
   universal is false, and a later seat that edits prose here and trusts it is
   trusting the one arm that will enforce later.
3. **The three lines this PR adds name the corpus as runs, not logs.**
   `tests/mutation_table.py:136-137`, `.github/workflows/tests.yml:1085-1086` and
   `tests/entities.py:31573-31575` all say "the 51 driver rows of the **three**
   2026-10-07/08 nightly runs". The three job ids are `112708109605` and
   `112708109541`, both of run `37595831734` (10-07), and `113233890923` of run
   `37753990323` (10-08) — read from each job's own `run_id`. **Two runs, three
   logs**, and 10-08's ledger lane is not in the corpus at all; §2's own rule says
   "the three parsed job logs", which is right. A seat that enumerates *runs* gets a
   different row count from the one the comment quotes. "three job logs of the two
   2026-10-07/08 nightly runs" is the fix, in all three places.
4. **Two small counts and one restore claim in the same file.** §7's evidence bullet
   says "the seven `entities_R3_*.txt` arms (§7's table names each)": there are
   seven arms and the table names seven logs ✓, but nine files match that glob in the
   scratch, and `entities_R3_HEAD_FINAL.txt` — the clean run at **this** head, whose
   mtime (19:51) postdates the commit (19:35:48 +0200) and which the body names — is
   not named in the landed doc, so the record cites only arms taken at the two
   dangling SHAs of finding 1. And the table's intro says each arm's "restore is
   confirmed `git diff --quiet HEAD`", while the seat's own driver log ends
   ` M dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` / `DIRTY` (its in-flight prose
   edit, not mutation residue; the body's "all three code files were re-checked
   IDENTICAL to HEAD" is the accurate wording). Naming FINAL, and scoping the restore
   claim to the mutated files, closes both — and finding 1's rewording would carry
   it, since a run at the head needs no byte-identity argument at all.

Also worth recording: `round-2 nit closure checked` — §2b's header now says members 1,
2, 4, 5 and 6 were re-measured and **member 3 was not**, matching member 3's own
disclosure; the opening states its cause-grouping rule ("a cause here is a
**mechanism** ... not a proximate fault"), which makes "five distinct causes" and
§2b's "three different faults ... rather than one cause" one count; the body's
`## Head` names `fix/r9-nightly-bound`, and `git ls-remote` confirms that branch and
`handoff/r9-nightly-bound` both at `c54beab89` (the round-2 wrong-branch-name nit is
gone), and calls `96497ffc6` "round-2 code head `7e8c5c8e4` plus this PR's own row",
which `git diff --name-only 7e8c5c8e4 96497ffc6` = `dev/programme/delivery/2074.md`
alone confirms (the "automatic merge" mislabel is gone). Step 10: `§2b` is in the
tree with six members, the (iv) arm routed to the owner with its price in §4, and the
`record-autofix` correction still true — round 2 read the `if:` verbatim at this head
and at `83f7ca558`, and nothing this round touched it. Step 15: the added lines are
comment and docstring text that name the measurement, its rule and its destination;
no new concern, import, state or parallel mechanism, so `fixer.md` step 17 has
nothing to breach.

## Step 12, head discipline

I measured `c54beab894db7210c570cd67f7cfb61212ed301c`, the SHA the body's `## Head`
names. Re-read before posting: `gh api pulls/2074` still answers
`head.sha = c54beab894db7210c570cd67f7cfb61212ed301c`, `state: open`, `draft: true`
(`evidence/head_recheck3.tsv`), so the head did not move under this verdict. My
worktree is `git diff --quiet HEAD` clean at the end of every arm run, so no mutation
residue is in the tree I measured. If the head moves after posting, everything in the
CI paragraph is this head's own; the arms survive only by the tree-identity argument
above — which is why I recommend the doc replace it with a run at the head (finding
4) before the merge.

**This is round 3.** `fixer.md` still owes a repair, not a re-cut, and the four
items are one-sentence edits to prose this PR already touches — none of them prices a
number. Route back to the fixer that authored `7e8c5c8e4` and this round's commit if
they are to be made before merge; the orchestrator may equally carry them, since no
figure changes and none of them is load-bearing. **The owner's code-owner review of
`.github/workflows/tests.yml` at this head is owed and outstanding** (`reviewRequests:
["tvofi"]`, `reviews: []`); this verdict is the approver's review, not that.

## RESULT lines (round 3)

- `RESULT delta-comment-only: PASS` — 4 files; every changed `tests.yml` line matches
  `^[+-]\s*#` (my filter printed no non-comment line); `mutation_table.py` and
  `entities.py` **AST-identical to `96497ffc6` with docstrings stripped** (my own
  `ast.dump`), sole docstring moved = `seed_pool_seconds`; `tests/closure.py` 0 diff
  lines, `TIMEOUT_SCALE 3`, `SECONDS_BAND 2.0`.
- `RESULT arms-at-head-mine: CLEAN 0 of 7 | REVERT 4 of 7 | A 1 | B 1 | C 1 | D 1 | E 1`
  — my harness over the tree's verbatim lines 31594..31801 at `c54beab89`; each red
  exactly the check §7's new seven-row table names; E bites through the adjacency
  regex; every restore `git diff --quiet HEAD` clean.
- `RESULT round2-block-record-7: CLOSED` — seven-row arm table landed (doc 429-437);
  round-1's four `2239` tallies labelled and matched against those logs; the three
  named instruments verified individually; `git diff 90ef590d8..HEAD --name-only` =
  this doc alone with an empty diff for the code files.
- `RESULT round2-block-factors: CLOSED` — `git grep -E '1\.3[-–]3\.3'` = 0 hits
  tree-wide at this head; four lines carry `0.47x-3.27x` + rule + resolvable `§2`;
  all three `0.3x-3.4x` hits labelled as recording variation, read against
  `tests/closure.py:1537-1547`.
- `RESULT factor-rule-mine: 16 rows 0.4653->3.0002(censored) | 16 rows 0.4653->3.2692`
  from two logs I fetched and computed under §2's rule, exclusions printed (7 rows,
  each with its solo); third log's 19 rows not re-taken; §2's 10-08 table cross-checked
  against `git show 816547efe:tests/closures.json` (7/7 solos, factors and bounds).
- `RESULT delay-mine: 5h54m57s -> 6h53m23s over 12 runs` (`tests.yml:119` cron read;
  ends `37108891698`, `37909555545`).
- `RESULT bound-arithmetic-mine: 1200/1200/1200/2297/1576/2401/4469; seeded
  4719/7200/7203; seed never lowers` — tree's own `driver_timeout` over seven heads,
  taken although the delta did not touch its code.
- `RESULT streak-end-honest: TRUE and understated` — 10-09 completed that driver at
  2416 s (nightly) / 2492 s (ledger) under the 4469 s bound from 1489.6, both above
  the 2401 s bound that killed 10-08; §1's new 10-06 row (2297) derived by me, its
  "both mutation lanes green" confirmed from run `37440269774`'s jobs.
- `RESULT voided-lane-mine: 63.4 / 64.2 / 72.4 min` from the three jobs' own stamps.
- `RESULT ci-at-head: 17 of 17 required success; ABSENT none; nothing red in the
  range` — settled 19:31:51Z after 8 polls at 300 s; `nightly-status`,
  `delivery-status`, `coverage`, `coverage-ratchet`, `graders-head-copy`,
  `instrument-self-tests`, `CodeQL` success; `mutation` green **and its log read by
  me as `empty scope`**, closing the one number round 2 relied on round 1 for.
- `RESULT whole-file-citation: CI's fast (3.14) prints ALL 2243 on the MERGE of this
  head into current main (`3c8c2b1f`), all seven RCA-1565 lines ok; the branch alone
  answers 2241 (+7 `R.check(` over the base). Both taken from CI's own log; the +2 is
  main's, not the record's, and the doc could name the difference in half a line.`
- `RESULT ratchet-and-hygiene: PASS` — STRUCTURE RATCHET PASSED (ratchet's class
  metrics are `custom_components/**` only, so the added comments move nothing),
  fold_ledger 101 rca entries / 0 violations, claims hygiene ok, closure selftest 57
  pins, layout rc 0, no budget/claim/fixture/version path in the diff, delivery row
  reads open.
- `RESULT merge-tree-vs-moved-main: exit 0, no MERGE-CLAIM` — step 13 clean against
  `d0f085ffb`; `BLOCKED` = draft + code owner.
- `RESULT findings-reported-not-blocking: 4` — §7 cites two amend SHAs that no remote
  ref carries and a fresh clone cannot fetch (measured); "no check reads this file"
  is falsified by `layout.py check()`'s report-mode reference arm (demonstrated with
  a planted citation, restored); "three nightly runs" for three logs of two runs;
  `entities_R3_HEAD_FINAL.txt` absent from the doc and the restore claim contradicted
  by the driver's own `DIRTY` line. Also: the doc's 2241 vs CI's 2243 deserves half a
  line.
- `RESULT code-owner-review: OWED from @tvofi at this head` — `/.github/workflows/`
  is owned (`CODEOWNERS:91`), the head edits it (comment-only), `reviewRequests`
  names `tvofi` and `reviews` is empty. This verdict does not supply it, and I did
  not approve, merge, mark ready, or post anything but this verdict.
