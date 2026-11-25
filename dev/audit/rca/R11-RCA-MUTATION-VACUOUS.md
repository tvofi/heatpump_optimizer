# R11-RCA-MUTATION-VACUOUS: the fixer's generated operators do not reach the edit the reviewer undoes (#3314)

This record continues `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md`, which split the key into population C
(`custom_components/`) and population T (`tools/`). It re-derives that split on the round-11 verdict bus.

Evidence, outside the tree: the prototype `vacuous_probe.py` with its enumerators (`enumerate_blocks.sh`,
`dump_blocks.sh`, `reach.sh`, `null_controls.sh`, `repeat_demo.sh`) and their outputs, under
the prototype directory of the orchestrator state directory. Proposal: `P-R11-MUTATION-VACUOUS`.

## 1. The count

**Enumerator:** `enumerate_blocks.sh <repo> 2026-11-15T05:22:47Z`. It lists every
distinct (PR, head, verdict) on the verdict bus. It reads two sources:

- `review/*`, `verdict/*` and `archive/review/*`: the commit subject.
- `probe/rev-*` and `archive/probe/rev-*`: the first line of `verdict.md`.

Output: `ev/enum_since_v10.txt`, measured 2026-11-22T22:44Z with the refs fetched at that time.

- **Since v10.0.0** (2026-11-15T05:22Z, 7.72 days): 311 verdicts, 88 blocks, **30 `mutation-vacuous`**, which is
  3.88 a day. The next class, `class-open`, has 18.
- **Last 72 h** (from 2026-11-19T22:44Z): 95 verdicts, 26 blocks, **15 `mutation-vacuous` on 11 PRs**. That is
  58% of blocks.

Control. Reading only `review/*` and `verdict/*` gives 9 blocks and 3 `mutation-vacuous` in the same 72 h,
because most cloud verdicts exist only as a `probe/rev-*` return. The brief's "4/13" and `bottleneck_check.py`'s
"5/14 (24 h)" are both readings over a narrower set of refs. The 15 below include the probe returns.

## 2. Each instance and its cause

The surviving mutant is quoted from each verdict's `## Block`: `dump_blocks.sh` for the probe returns, and
`VERDICT.md` for the review refs. The reach columns are measured by `reach.sh` (`ev/reach_out.txt`) and by
`vacuous_probe.py` (section 6).

| # | block (PR, head) | surviving mutant | named cause | prototype reach |
|---|---|---|---|---|
| 1 | #3866 f36611dd | `pump_arbiter.py:936 GUARD_OFF`, an equivalent mutant: `_map_inputs` already takes `min(boost, limit)` | The body says the cap was deleted ("the mutant site no longer exists"), but it is still at the head. The body disposes the site "pinned by mutation-autofix", but autofix pins only killed mutants. CI could not show it either: `tests / mutation-autofix` at this head was `skip-measure-failed`, because every pin shard's baseline was red on `tests/doc_claims.py` (the PR's own comment-ratchet refusal). The `PIN SHARD 1/6` log reads `MUTATION TABLE INCONCLUSIVE`. | A + B fire |
| 2 | #3866 19eafc0f | the same site, re-blocked | Repeat of #1. The delta 566727d1db did not touch the site. | A + B fire |
| 3 | #3838 6ef32c22 | `coordinator.py:6311`, `:11334` (`**rooms.floor_limits(...)` reverted to the margins-only keyword) | The edit is a keyword splat. No operator undoes it. The body credited `:6285` and `:11296` STMT_DEL kills: those are other statements, whose deletion any test kills. | C: HAND-OWED at both lines (the base text names `rooms.lifted`, which is gone) |
| 4 | #3873 73797a57 | `coordinator.py:4126` `of(self, self.mode)` -> `of(self)` | A positional argument was added. The body disposed the line as `4126 RETURN_DEL ... pinned by mutation-autofix`. A whole-return deletion is a different mutant, which any caller kills. | C: DRAWN, exactly the reviewer's M8 |
| 5 | #3835 c6c11df0 | `coordinator.py:1121` `tank.value if tank.ok else None` -> `None`; `draw_range.py:788` conjunct dropped | No operator reaches an `IfExp`. A conjunct-drop operator does not exist; BOOLOP turns `and` into `or`. | C: the line is DRAWN (the revert is not the reviewer's L); `:788` not reached |
| 6 | #3835 3d8679b7 | `:1121` -> `tank.value` (L2, the sister of L) | The re-cut killed L and missed L2. Same operator gap as #5. | C: the line is DRAWN |
| 7 | #3845 e82a2656 | `room_record.py:72-75`: the guarded `unsaved = 0` made unconditional | A guard forced true. Only GUARD_OFF exists. | not reached |
| 8 | #3869 8ca95413 | `duty_legs.py:184` numpy `& (...)` conjunct dropped; `:146` `before` -> `IDLE` | BOOLOP reads `and` only, not numpy `&`. A value replaced by a constant has no operator. | not reached |
| 9 | #3872 d6a54399 | `fault_hold.py:115` `released=` dropped and `off=` -> `False`; `heat_curve.py:287` `off=mode_off` -> `False`; `:150` `since` -> `None` | Keyword-argument values on added lines. No operator reaches them. | not reached |
| 10 | #3847 46e7faa9 | `tools/ci/prelude.py:470` reverted to read `ev` (the pre-change line) | A tools line with no generated mutation. The reviewer's mutant is the line's own revert. | C (with `--revert-path tools/`): DRAWN, exactly the reviewer's M7 |
| 11 | #3868 273e5ece | `corpus_mirror.py:160` `round` -> `int`; `:393` `max` -> last; `:425` range guard | Population T: the in-tree MUTANTS table is the author's choice (67 killed), so the reviewer's plants are new. | not reached |
| 12 | #3834 76f30b59 | `selftest_scope.py:1170` conjuncts, `orchestrator_tick.py:2092/2101`, `selftest_absorb.py:109/155/242` | Population T: hand mutants of a tools self-test | not reached |
| 13 | #3834 1ab809af | the same six, "round-1 block unanswered" | Repeat. The re-cut answered the CI reds, not the survivors. | not reached |
| 14 | #3834 6c5e3d86 | the same six, "round-1 and round-2 block unanswered" | Repeat, as #13 | not reached |
| 15 | #3821 b1ee994a | `heatpump-optimizer-card.js:7344`, `:11424`, `:5257` deleted | No generated mutation lane exists for the card JS. The test DOM stub has no `setProperty`, so the line never executes under test. | not reached (rule C reads `.py` only) |

### The common cause

The fixer and the reviewer measure two different units:

- **The fixer** (`fixer.md` step 2) draws mutants from a fixed set of syntactic operators. For `custom_components/`
  that is the seven in `tests/mutation_table.py`, plus the six operators and STMT_DEL of `mutant_run.py` diff mode.
  For a tool it is the author's own `MUTANTS` table. The fixer then disposes every survivor of that set.
- **The reviewer** (`fix-review.md` step 1, "delete the production line(s) the PR names") undoes or perturbs
  **the semantic edit the PR made**.

Where the edit is one no operator draws, the generated set reports nothing, and the fixer has nothing to answer.
Such edits are an argument or keyword value (#3, #4, #9), a conditional expression (#5, #6), a numpy conjunct
(#8), a guard forced true (#7), a tools or JS line with no generated lane (#10-#15), or a line restored to its
base text (#4, #10). In each case the first measurement of that edit is the review.

At #3 and #4 the body credits a coarser mutant on the same line or statement (STMT_DEL, RETURN_DEL). Any test
kills that mutant for a reason unrelated to the edit, so the coarse kill reads as a pin of the edit.

#1 and #2 are a second, smaller cause: **the body's mutation claims are not confronted with the head**. Nothing
checks that a site the body says was deleted is absent. Nothing checks that a site disposed "pinned by
mutation-autofix" is one autofix can pin. prepr step 7d (`unpinned_line`) checks only that each site has some
disposition. The disposition grammar `fixer.md` gives ("pinned by `mutation-autofix`") is accepted for an
equivalent mutant, which autofix can never pin.

## 3. Process state: (c)

**The fixer's step was followed.** Each `custom_components/` body read in the 72 h set carries a mutation
proof with every survivor it printed disposed. Examples: #3838's "CMD the 3B block ... 8 survivors", drawn by
`mutant_run.py`; #3866's author mutants M1-M12 over the FLOWCAP block, plus an `## Unpinned sites` line for each
generated site; #3873's M1-M8. This was read from the bodies; whether prepr 7d passed at each head was not
re-run here.

**It did not produce the intended result.** The intended result is "no survivor the reviewer can find on a
changed line". The unit cannot reach the edit classes in section 2. This is the same state
`R10-RCA-MUTATION-VACUOUS.md` recorded for population C: there it was autofix's red against the reviewer's
mutants. Here the gap is named: the operator set against the edit.

**Not (b).** No fixer skipped step 2 on #3-#11 or #15. Each disposed every survivor its generator printed.
"Tell the fixer to try harder mutants" would be a firmer instruction for a step that was obeyed, which
`defect-root-cause.md` names as the most common error.

**Not (a).** Both processes exist: the generators, prepr 7d, `mutation-autofix`, and fix-review step 1.

**(d) at #1 only, as a contributing condition.** `mutation-autofix` is sound when its baseline is green. At
f36611dd its precondition failed (a red `doc_claims.py` baseline made every shard
`skip-measure-failed`, 0 anchors). Nothing told the body or the reviewer that the promised pin would not happen.
The countermeasure below (rule B) does not depend on that precondition.

**The repeats #2, #13 and #14 are (b) on their face**, since "Each SURVIVED line ... gets a killing check or an
`## Unpinned sites` disposition" was not done on the re-cut. The detector built for them failed its own
demonstration (section 6.3), so no countermeasure is proposed for them. Repeat cost is priced in section 4.

## 4. Cost test (wall-clock per occurrence, over a release cycle)

**Release cycle.** v10.0.0 (2026-11-15T05:22Z) to v10.1.2 (2026-11-21T20:36Z) spans 6 cycles in 6.64 days, a mean
of **26.6 h per cycle**. The enumerator's 3.88 blocks a day gives **4.3 `mutation-vacuous` blocks per cycle**.

**Defect cost per block.** The wall-clock time from the blocked verdict to the PR's next verdict at a new head,
over the 25 of 30 blocks since v10.0.0 that have one: **median 272 min** (min 57, max 4189). Computed from
`ev/enum_since_v10.txt` by the rule "first later verdict, same
PR, different head". The other 5 are still open. `R10-RCA-FRICTION-RESIDUE.md`'s earlier 111 min (n=8) is the
conservative alternative, and the verdicts below hold at either figure.

**Reach, measured on the 15 blocks of the 72 h window (section 2):**

- Rules A + B: 2 of 15 (#1, #2). Both bodies were in place before the review: the f36611 body was edited at
  20:06Z, and the cloud verdict landed at 20:50Z.
- Rule C draws the reviewer's own mutant: 2 of 15 (#4; #10 with `tools/`). Rule C names the line HAND-OWED:
  1 of 15 (#3).
- Rule C draws a revert on the blocked line, though not the reviewer's mutant: 2 (#5, #6). These are not counted.

**Countermeasure 1: rules A + B**, a static check over the body and the head (narrowing prepr 7d).

- Standing cost: **1.6 s** per run (measured: `time` on #3866, real 1.608 s). Run once per body push, at about 40
  heads a day (311 verdicts / 7.72 days) or 45 per cycle, that is about **72 s per cycle**.
- Induced work: false fires on healthy heads are 0 of 23 (section 6.2), so 0.
- Benefit: 2 blocks in 72 h is 0.74 per cycle. At 272 min that is **201 min per cycle** (82 min at 111).
- Verdict: **72 s < 201 min. Build.**

**Countermeasure 2: rule C**, the LINE_REVERT operator.

- Standing cost has a static half (the same 1.6 s run) and a measured half: one driver run per 1:1-modified line.
- Lines per PR: 23 healthy merged PRs drew 119 reverts before the docstring filter (`null_controls.sh`, v1), mean
  5.2 per PR. After the filter they drew 0, 4, 13 and 0 on the four 72 h merges.
- Driver run: about 11 s per mutant at block scope (measured: `mutant_run.py --spec` NULL plus one mutant, real
  21.66 s, `ev/mutrun-936.txt`).
- About 3.7 production PRs per cycle (23 merged in 7 days) at about 2 heads each gives
  **7.4 x 5.2 x 11 s ≈ 7 min of driver time per cycle**, plus writing about 5 body lines per PR (estimated
  2 min per PR, so about 7 min per cycle). Total **about 14 min per cycle**.
- A survivor that the block misses needs a closure-scope run to confirm. #3866's reviewer measured one at about
  6000 checks of `tests/features.py`. Not priced: no measured survivor rate exists for LINE_REVERT. It is the open
  number.
- Benefit: 3 blocks in 72 h is 1.1 per cycle. At 272 min that is **300 min per cycle** (122 at 111).
- Verdict: **about 14 min < 300 min. Build**, as a generator operator (self-repair rung), not as a new body
  refusal. Shadow first.

**Not built: the operator gap for #5-#9 and #15** (argument drop or constant, IfExp, numpy `&`, GUARD_ON, JS
lanes). These are 7 of 15 blocks. None is prototyped here, so no cost side exists. This is a refusal that
depends on a number nobody has, as `R10-RCA-MUTATION-VACUOUS.md` §5 recorded for T. The number that would reverse
it is the drawn-mutant count per PR, and the driver seconds, for an argument-level operator family.

**Not built: population T**, the tools hand mutants (#11-#14, 4 of 15). R10 refused this on an unpriced
`tools/` mutation table. Rule C reaches #10 with `--revert-path tools/`, so LINE_REVERT is the first tools
operator with a measured cost.

## 5. Countermeasure

The rungs, in the contract's order:

1. **Delete.** Deleting the disposition "pinned by `mutation-autofix`" is not possible: it is the right
   disposition for a killed survivor of the block driver (#3873's M1-M4 pattern).
2. **Self-repair.** For rule C: add **LINE_REVERT** to `mutant_run.py` diff mode. For each 1:1-modified line, it
   restores the base text. A base line naming a package `module.attr` that the head no longer defines is printed
   as HAND-OWED, because its revert would die of NameError, a vacuous kill. The existing rule ("each SURVIVED
   line gets a killing check or a disposition") then covers it, with no new body grammar. In the prototype rule C
   is shown as a body check only so that it can be demonstrated without a tracked edit.
3. **Narrow.** For rules A and B: narrow prepr step 7d (`unpinned_line`) and `body_push`'s predictor.
   - A refuses a body sentence saying a site in/from/inside `` `f` `` was deleted or "no longer exists" when the
     head still draws a changed-line mutant in `f`.
   - B refuses "pinned by mutation-autofix" for the one drawn changed-line site of a function that the body
     records as holding an equivalent or all-surviving mutant.
   - Each prints its repair: delete the site, or give it a killing check or a `survivor_triage`.
4. **New refusal.** None is proposed. The repeat guard (6.3) would have been one; it failed.

Rules A and B are a narrowing of an existing tracked check, which the tooling freeze bars mid-round. Overlay: run
`vacuous_probe.py --rules AB` in seat briefs before handoff (seconds). Rule C needs a `fixer.md` step 2 sentence
naming the operator, which is policy, so it waits for the owner's approval.

## 6. A detector must be shown to detect

All runs are from the prototype directory.

### 6.1 Failing on the defect, passing once fixed

**#3866 at 19eafc0f, rules A and B.** Run with
`vacuous_probe.py --repo <wt> --head WORKTREE --base 8cc3fb3e35 --body body-3866-now.md --rules AB`:

- **BEFORE**, the head unedited: `FAIL -- rule A 2, B 1`, rc 1. Both A lines name
  `pump_arbiter.py:936 GUARD_OFF` in `_boost_ceiling_c`, and B names the same site.
- **AFTER** the review's repair (`ev/fix-3866.diff`: lines 936-937 deleted and the docstring clause re-pointed to
  `_map_inputs`): `PASS -- rule A 0, B 0, C 0`, rc 0. After the repair the FLOWCAP block prints
  `ALL 12 FEATURES BLOCK PASSED`.
- **#3866 at f36611dd** (body as edited 20:06Z, from `userContentEdits`): `FAIL -- rule A 2, B 1`. That body
  predates the cloud verdict (20:50Z), so the rule would have caught both rounds.
- **The site is a real survivor, measured.** `mutant_run.py --spec ev/spec-936.json --in-place --cmd 'bash
  flcmd.sh'` at 19eafc0f prints `SURVIVED NULL` and then `SURVIVED pump_arbiter.py:936:GUARD_OFF`, rc 0
  (`ev/mutrun-936.txt`). This is the one targeted run this seat made.

**#3873 at 73797a57, rule C.** Run with `--rules C`:

- With the PR body: `FAIL -- rule C 6`. It includes `coordinator.py:4126 LINE_REVERT`, whose spec entry
  (`spec-73797a57.json`) is exactly the reviewer's M8 (`of(self, self.mode)` -> `of(self)`). The reviewer
  measured M8 surviving `debug_collect.py` 164/164 and `entities.py` 2761/2761.
- With the same body plus one `<file>:<line> LINE_REVERT: ...` line per draw: `PASS`, rc 0.
- Limit, stated: like 7d, rule C checks that a line is answered, not whether the answer is true. Its value is
  that it draws the mutant; the truth stays with the driver run and the reviewer.

**#3838 at 6ef32c22, rule C**, using the body as edited at 21:15Z: `C LINE-REVERT HAND-OWED` at
`coordinator.py:6311` and `:11334`, the two lines the block names.

### 6.2 Null control: no fire on a healthy tree, no green by skipping

- `null_controls.sh` was run over the 23 PRs merged since 2026-11-15 whose merged head changes production `.py`
  files, at that head, against the merge commit's first parent (`ev/null_controls_7d_v2.txt`). Rules A + B
  give **23 of 23 PASS**.
- The first cut fired on two PRs, and both were tightened, not waived:
  - #3670 (B, 4 sites in `_stored_floor`, a survivor not tied to one site) led to the one-site condition.
  - #3731 (A, "removed at the source: `zone_trajectories` returns early") led to the in/from/inside anchor.
- Every rerun of #3866 after both tightenings still FAILs.
- No green by skipping: every run prints the number of changed production files it read (7 at #3866, 3 at #3873).
  A run that reads 0 files prints `0 changed production file(s)`, so a pass over nothing is visible.

### 6.3 A detector that failed its demonstration: not proposed

`repeat_guard.py` was meant to refuse a re-review whose delta touches none of the files the block names (#2, #13,
#14). In `repeat_demo.sh` / `ev/repeat_demo.txt` it printed **ANSWERABLE on all three repeats**:

- #3834 r1->r2: the delta touched `selftest_absorb.py`, the file but not the survivor.
- #3834 r2->r3: the delta touched `tests/*` through main merges.
- #3866: the delta touched `tests/features.py`.

At file granularity the guard passes while the defect is present, so it is withdrawn. Line-level matching across a
re-cut that shifts lines (109 -> 141) is not prototyped.

## 7. How far the class reaches

The search covered all 30 blocks since v10.0.0 and the 15 in 72 h, read one by one. In the 72 h set:

- 9 of 15 blocks are on `custom_components/`.
- 4 of 15 are on `tools/`.
- 1 of 15 is on the card JS.
- 1 of 15 is a sister mutant of an earlier block on the same PR (#6).

The same cause, the operator set against the edit, reaches `mutation-survivor` (3 since v10.0.0) and
`mutation-survivors` (1). Those were not read line by line here.

## 8. Not established here

- The survivor rate of LINE_REVERT, and therefore the closure-scope cost of confirming its survivors.
- The cost of an argument-level operator family (#9's shape).
- Whether a line-level repeat guard detects #13 and #14.
- The 272 min round-trip is wall-clock, including queue wait. It is not seat time.

## Root cause (for #3314)

- **State (c).** The fixer's mutation proof was run and disposed. Its generated operators do not reach the edit
  that fix-review step 1 undoes: argument, keyword, revert and IfExp edits, and tools or JS lines. A coarse kill
  (STMT_DEL or RETURN_DEL) on the same line reads as a pin. A smaller part is the body's claims, which are not
  confronted with the head: "deleted" while present, and "pinned by mutation-autofix" on an equivalent mutant
  (#3866).
- **Cost test, per 26.6 h cycle:**
  - Rules A + B: standing cost 72 s against 201 min. Build.
  - LINE_REVERT: standing cost about 14 min against 300 min. Build, as a generator operator, shadowed first.
  - The other operator gaps are not built: no cost exists to test.
- **Countermeasure:** P-R11-MUTATION-VACUOUS. The prototype is at the prototype directory, shown failing on
  #3866 at 19eafc0f and passing once fixed.
- **Record:** `dev/audit/rca/R11-RCA-MUTATION-VACUOUS.md`.
