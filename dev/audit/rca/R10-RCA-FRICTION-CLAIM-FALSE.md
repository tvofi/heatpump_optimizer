# R10-RCA-FRICTION-CLAIM-FALSE: a ruling whose rule never met its own instance (#2907)

The root-cause record for the recurring-friction key `claim-false` (#2907),
filed by the governance cron at 4 distinct pull requests / 8 entries in
`v7.0.5..origin/main`. It ran apart from any fix, under the root-cause role
contract. It lands one policy sentence and no production code.

**Merge base and window.** Every figure was taken on 2026-10-29 at merge base
`88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, which was also `origin/main` at
measurement. Tag `v7.0.5` = `e8cb7e68302b1d350bb8219fea99e911170af030`,
committed 2026-10-27T22:36:10Z.

## 1. The count, re-derived

`node tools/policy/policy_lint.mjs --stats --since v7.0.5`, rc=0, 2 min 7 s
(`claim-false/stats_v7.0.5.txt`): `4 / 8 claim-false <- at or over threshold`
and the `would open "[policy] recurring friction: claim-false"` line, out of 55
merged PRs that carried a parsable verdict (59 merged). That matches #2907's
4 / 8.

The four PRs and their eight `Fix review: blocked <head> claim-false` comments
(`gh api repos/tvofi/heatpump_optimizer/issues/<pr>/comments`, posted by
`hpo-approver[bot]`):

| PR | what | blocked heads | min to next verdict |
|---|---|---|---|
| #2883 | fix, R10-FLOW-BOARD | `8f05b74d`, `3bd284f7` | 268, 308 |
| #2890 | triage batch 41 (P212-P215) | `54ac455a`, `adf5ef47` | 23, 298 |
| #2891 | triage batch 42 (P216) | `4a276b6a`, `f975e044` | 308, 62 |
| #2900 | triage batch 45 (P227-P231) | `75cfbce6`, `ebbc01ea` | 51, 174 |

"Minutes to next verdict" runs from each blocked comment's `created_at` to the
same PR's next `Fix review:` comment. It counts fixer, CI, reviewer and idle
time together, so it is an upper bound on what a block costs. Sum 1492 min,
median 221 min.

Three of the four PRs are triage batches. The stats line `STATS COVERAGE BY
CLASS` counts **5** triage-titled PRs in the window, so 3 of the window's 5
triage PRs were blocked `claim-false`.

`claim-false` is a word no list teaches. `VERDICT_CLASSES` in
`.claude/workflows/web-fix-wave.js` holds `claims`, which is the golden-fixture
claim class, and not this one. The key reached the threshold under its own
spelling, so #2436's derived `other (untaught)` family is not needed to see it.
Controls in earlier windows: `stats_v7.0.0.txt` shows `claim-false` at 1 / 1,
and `stats_v7.0.4.txt` shows none, with its siblings `claim-refuted` 1 / 1 and
`body-claim-wrong` 1 / 1 (all three under `dev/audit/rca/harness-friction/`).

## 2. The author paths, item by item

One verdict can block on several things. `claim-false/items.tsv` lists the
**18 blocking items** of the eight verdicts, one row each, with the path that
produced each. It omits non-blocking and "Verified" items.

| path | items | PRs | what |
|---|---|---|---|
| F: a fix's promise, closed only for the demonstrated seams | 5 | #2883 | "a source the board cannot read prints UNAVAILABLE, never a zero" |
| T: a typed or carried citation | 5 | #2890, #2891 | a function that never existed, a 45-minute figure, `456/464` for `455/466` (twice), a step that does not say what the ruling says it says |
| V: a proposal id from a second id writer | 2 | #2890, #2891 | headings `(V132)`-`(V136)` beside `Source:` V125-V129 |
| R: a ruling's rule never run on its own instance | 2 | #2900 | P228's every-failed-job rule, then its FAIL-prefixed gate rule |
| O: another semantic claim | 2 | #2890 | P214's destination ownership, P215's guarded op set |
| C: a `Cost:` that read no cap | 1 | #2891 | "one CLAUDE.md paragraph, no check to keep green" at 3605/3605 |
| B: a body claim about the check state | 1 | #2883 | `## Red checks: none` while `tests / closures` was red |

**The brief's hypothesis holds inside the triage batches, not for the key.** In
the three triage PRs, ids and lines typed from memory (T + V) account for 7 of
12 blocking items. They lead 3 of the 6 triage verdicts: #2890's two and
#2891's first. Over the whole key, T + V is 7 of 18 items. Neither half is the
cost. Section 4 shows that P219 has already removed V, and that T never caused
a round on its own.

**What cost rounds is R + C.** Each of #2891's second verdict and #2900's two
verdicts blocked on **one** item, and that item was R or C. Their
block-to-next-verdict times are 62, 51 and 174 min: **3 rounds and 287 min**,
each of which a ruling would have avoided had it run its own rule on its own
instance (R) or read the cap of the file it charged (C).

The R items were re-derived at the base where the tree allows it:
`tools/ci/gate.py:224` prefixes only the first reason (`f"FAIL {why[0]}"`),
and `:295` prints the rest with no prefix (`"\n".join([outcome] + why[1:])`).
So a rule that reads only `FAIL`-prefixed lines misses every reason after the
first, as #2900's second verdict found. Job 122526090837 is `gate`, `failure`,
completed 2026-10-27T23:10:21Z, in run 40596083060 (`gh api .../actions/jobs/
122526090837`). Its log was **not** re-read here: the log's blob host is
outside this seat's network policy. The C item re-derives directly:
`policy_lint.mjs --budgets` at the base prints
`CLAUDE.md 213 221 3605 3605 yes`.

## 3. Named cause and process state

**Cause.** A triage ruling's figures are cited, but its *rule* is never run.
An ACCEPT's carry states a predicate (match these strings, read these lines,
charge this file), and the seat checks the predicate's citations against code.
It does not put its own counted instances through the predicate, so a
predicate that excludes its own instance reads as true. A `Cost:` is an
estimate, and nothing ties it to the one measured cost a policy edit has: the
cap of the file it grows.

**Process state: (a) for R and C.** The contract at the base,
`dev/governance/roles/proposal-triage.md` "The ruling" paragraph, requires
`Instances:` "with the command or log reference beside its figure: cite it,
don't carry it" and `Cost:` "(the estimate)". It requires no run of the ruling's
rule on those instances, and no cap read. The seat did what the contract asks:
#2900's first review records every code citation as re-derived ("All hold") and
then blocks on the rule. The contract's "rulings are checked against code"
(its first paragraph) is the check that was done. It is not the missing one.

**Process state: (b) for T.** The "cite it, don't carry it" step existed, and
these items broke it. The identical wrong pair `ruling_verdict at 456,
triage_refusal at 464` appears in both #2890's and #2891's bodies. At the base
`grep -n` puts the two `def`s at `tools/audit/seat/roster_edit.py:455` and
`:466`. `conflicting_claims_message` was typed with "around 1845-1857";
`git log --all -S conflicting_claims_message -- tests/env_drift.py` returns 0
commits, and the function at 1844 is `merge_claim_refusal`.

**Process state: (d) for V, already countermeasured.** P219
(`dev/programme/triage/s6-batch44.md`) found the cause: two writers allocated
one id space, a relay's V124-V130 and `proposals.md`'s own V124 onward. It
removed the id from the heading. **Held**, measured with `git grep -cE
'^## P[0-9]+:.*\(V[0-9]+\)'`: 0 of the 52 headings in batches 45-59 carry an
id. Control: 13 headings in batches 35-43 still carry one, and in 40-43 each
now equals its `Source:` line.

**#2883 (F, B) is not the triage path.** It is a fixer PR. Its F items are a
"never a zero" property that the fix closed for each demonstrated seam, while
the class stayed open. The second review says each finding was "ANSWERED for
the source it demonstrated" and blocks on the next seam. That is the
`class-open` obligation filed under another word. The standing refusal for it
is in `R10-RCA-FRICTION-RESIDUE.md` section 6 (#2784), and `fixer.md` steps 3
and 8 already require a null control for a "none" and a rule enumerating the
seams. Its B item is the red-check trigger. The red check itself has its own
record, `R10-RCA-CLOSURE-ARGV` in `bugclasses.json`'s `_rca`. Nothing new is
owed here.

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in seat
minutes per window.

**Countermeasure 1, landed: one sentence in the triage contract** (R + C,
state (a)). "An ACCEPT runs its rule on each instance, result beside it", and
`Cost:` carries "each capped file's `--budgets` row".

- Standing cost: per ACCEPT, one replay of each counted instance through the
  stated rule, plus one `policy_lint.mjs --budgets` read when the ruling grows
  a capped file. The replay works on artefacts the ruling already cites (a
  job's log, a line of code, a budget row). The estimate is a few minutes per
  ACCEPT, based on the reviewers doing the same replay inside a review. It
  adds no tokens to any load: the contract stays at 489 / 489 tokens and
  36 / 36 lines (`policy_lint.mjs --budgets`). It was paid by tightening the
  same paragraph, with no cap raised.
- Benefit: in this window it would have reached 3 of the 8 entries (3 rounds,
  287 min), and each of them blocked on that item alone.
  `P(recurrence)`: 3 of the window's 5 triage PRs drew `claim-false`, and the
  R/C rounds fell on 2 of them.
- Verdict: built. The countermeasure is an instruction, not a check, so no
  red/green demonstration is owed. Its instances are the three verdicts above.

**Countermeasure 2, refused: a citation-resolving lint over triage batches and
bodies** (T, state (b)).

- What it would reach: of the 5 T items, a resolver for `` `symbol` `` beside
  `path:N` in batch files catches only B1, the absent function, since the
  `456/464` pair sits in PR bodies with no path in the token. A body-wide
  "`name` at N" grammar might catch 3. The other 2, a time window and a step's
  content, are semantic.
- Rounds it would have saved: none on its own. Every T verdict had another
  blocking item: #2890's first had B2-B4, its second had N3, and #2891's first
  had V136. With P219 in force, a body-wide lint would have cleared #2891's
  first round, at most 1 round (308 min upper bound) in the window. And the
  `456/464` pair is one error found twice, so it counts as one independent
  occurrence.
- Cost: a new instrument with a grammar, self-test, closure classification and
  `prepr.sh` wiring, plus the review rounds that land it. A loose "`name` at N"
  grammar also carries the false-fire risk that
  `R10-RCA-FRICTION-RESIDUE.md` section 3 measured for a token predicate over
  prose (205 of 205).
- Verdict: **refused.** Over this window, one occurrence saving at most one
  round does not pay for a standing instrument. The reviewer's `grep -n` is
  the cheapest detector, and it ran.

**V: no new countermeasure.** P219 holds (0 / 52).

**F, B (#2883): no new countermeasure.** These are the `class-open` residue
under its existing refusal, plus a red check recorded elsewhere.

## 5. How far the class reaches

The search was `node tools/policy/policy_lint.mjs --stats` in three windows
(section 1) for `claim-false` and its spellings. It found `claim-false` 1 in
`v7.0.0`, `claim-refuted` 1 and `body-claim-wrong` 1 in `v7.0.4`, and
`claim-false` 4 plus `figure-wrong` 1 in `v7.0.5`. The step-up in this window
is concentrated in triage: 3 of 5 triage PRs, against 1 of the other 50 PRs
that carried a verdict. The new contract sentence is aimed at that
concentration. A fixer is already bound by `fixer.md` step 3's "a count, a
percentage, an 'every' or a 'none' is a measurement".

## 6. Not established here

- Job 122526090837's log was not re-read: the log's blob host is outside this
  seat's network policy. The R items are re-derived from `tools/ci/gate.py` at
  the base and from the job's API metadata. The log lines (4372-4373) are the
  reviewer's.
- The per-ACCEPT replay cost is an estimate, not a measurement.
- The 5 triage PRs come from the stats line's class tally. They were not
  enumerated by number.

## Evidence

`dev/audit/rca/claim-false/`:

- `stats_v7.0.5.txt`: the `policy_lint --stats --since v7.0.5` run at the
  base, rc=0.
- `items.tsv`: the 18 blocking items, with path and reach.
