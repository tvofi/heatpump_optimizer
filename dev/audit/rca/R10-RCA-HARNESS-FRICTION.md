# R10-RCA-HARNESS-FRICTION: a block class the contract does not teach splits one obligation across friction keys (#2331, #2353, #2409, #2410)

The root-cause seat for four issues the governance cron's friction step
(`tools/policy/friction_issues.mjs`) filed in the window `v7.0.0..origin/main`:

- **#2331** `[policy] recurring friction: harness`
- **#2353** `[policy] recurring friction: class-open`
- **#2409** `[policy] recurring friction: mutation-vacuous`
- **#2410** `[policy] recurring friction: mutation (family)`

It ran apart from any fix (`dev/governance/roles/root-cause.md`). Figures were
re-taken on 2026-10-18 between origin/main `176851e9` (the `--stats` run) and
`106af95a` (the verdict enumeration); section 1 says which instrument read which.
#2331 and #2353 share one cause (section 2). #2409 is the same cause on a second
step (section 5). #2410 is a different cause, outside this record (section 6).

## 1. The counts, reproduced

`GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v7.0.0`
ran with rc=0 in 4 min 5 s. It counted 129 merged pull requests, 67 with a parsable
verdict, and printed, as distinct PRs / entries:

| key | PRs / entries | issue |
|---|---|---|
| `harness` | 13 / 21 | #2331 |
| `class-open` | 4 / 5 | #2353 |
| `mutation-vacuous` | 3 / 3 | #2409 |
| `mutation (family)` | 3 / 3 | #2410 |
| `test-vacuous` | 2 / 2 | none (below threshold) |
| `vacuous-check`, `mutant-survives` | 1 / 1 each | none |

The seat then listed every entry itself, without `policy_lint.mjs`:

- The pull requests are the `git log --first-parent v7.0.0..origin/main` subjects
  `Merge pull request #N` at `106af95a`: 125 (`window_prs.txt`). The two PR rules
  differ; `policy_lint.mjs` also recovers merges from `/commits/<sha>/pulls`.
- For each, the first line of every comment (`/issues/N/comments`) and review
  (`/pulls/N/reviews`); 0 of 125 fetches failed (`verdict_first_lines.tsv`).
- `rounds.py` keeps each `Fix review: blocked <40-hex> <class>: <reason>` line: 48
  blocked verdicts (`blocked_rounds.tsv`).

Every count in the table above reproduces from `blocked_rounds.tsv`. The one entry
the histogram lacks is #2396's `conflict` verdict (15:25Z), posted after the
`--stats` tip; it is in no class this record measures.

**The step-6 class-open refusal, under both spellings:**

- `harness` totals 21 entries over 13 PRs. **18 of the 21 open with `class-open`**,
  over 12 of the 13 PRs. The other 3 are a survivor and an over-claim (#2283) and
  `class-rule-missing` (#2329): **2 PRs**.
- `class-open` written as the class: 5 entries over 4 PRs (#2289, #2293, #2320,
  #2345).
- Folded: **23 of the window's 48 blocked verdicts, over 13 PRs**; 10 of the 23
  re-blocked a PR already blocked on a class-open seam. Elapsed time from each
  block to the next verdict on the same PR sums to 5695 min, median 131 min (it
  includes fixer, CI, reviewer and idle time).

## 2. Named cause

**A contract step that defines a block class does not teach the word
`VERDICT_CLASSES` carries for it.** `VERDICT_RE` in `.claude/workflows/web-fix-wave.js`
takes the first word after the SHA as the class, so both readers (`parseVerdict` and
`policy_lint.mjs` `statsHistogram`) key a verdict on whatever word the reviewer wrote
there. Where the step teaches a different word, or none, one obligation lands on
several keys.

**#2331 and #2353.** `fix-review.md` step 6 taught `blocked <sha> harness: class-open
<seam>`, which keys `harness`, while `class-open` is a block class of its own. Both
halves came from one commit: `6bc932db` (#1414, 2026-09-22) added `'class-open'` to
`VERDICT_CLASSES` and wrote that example. In this window 18 class-open blocks followed
the example and 5 did not, so the cron filed one obligation twice.

R9-RCA-2004 (#2004, section 2) named the effect ("a parent verdict class, and the
friction key counts the parent") but not the cause. The `harness` key was filed in
5 release windows: #1881 (v6.7.14), #2004 (v6.7.16), #2034 and #2136 (v6.7.17),
#2331 (v7.0.0); v6.7.15..v6.7.16 stayed below threshold at 2/2. Each disposition
seat found `class-open` the largest child (#2004: 4 of 7 entries; #2034/#2136: 3 of
6 PRs, #2057 #2068 #2075; #2331: 18 of 21 entries) and closed the parent as "the
mechanism working".

## 3. Process state, with evidence

**(c): the process was followed and did not produce the intended result.**

- Reviewers obeyed step 6 as written: 18 of the 23 class-open blocks used its spelling.
- The cron keyed and filed as `policy_lint.mjs` specifies; every count reproduces
  (section 1).
- A check existed. `tools/policy/check-wave-script.mjs`, block "the contract's verdict
  examples parse under the script's own grammar", checks that every backticked
  `blocked ...` example parses and that its first word is taught. `harness:
  class-open` passes both arms because `harness` is taught. The unit is the first
  word; a taught word in the reason position is invisible to it, and a step that
  teaches no word at all (section 5) offers it no example to read.

Not (b): nothing was disobeyed, and a firmer instruction would contradict the
contract's own example. Not (a): the example check existed. The countermeasure
corrects the examples and changes the check's unit.

## 4. How far the class reaches

Every `VERDICT_CLASSES` word against the backticked `blocked <sha> <w>:` examples in
`dev/governance/roles/` and `dev/governance/dimensions/` (a `node -e` read of the
literal and the examples, at this head): 8 of 17 words are taught (`mutation-vacuous`,
`class-open`, `harness`, `carry-missing`, `root-cause-unanswered`, `head-moved`,
`metric-gamed`, `architecture-unsound`); 9 are not.

- **A taught word in the reason position:** exactly one example,
  `fix-review.md` step 6 (the held detector, section 7, ran over every example and
  fired there alone). `harness: class-rule-missing` and `harness:
  design-trace-missing` put untaught words there and stay `harness` sub-reasons.
- **A step that names a block with no word:** `fix-review.md` step 1 ("the test is
  vacuous and the PR is blocked"), whose word `mutation-vacuous` no example taught
  (section 5).
- **Synonym splits in this window, untaught words over all 48 blocks:** the mutation
  obligation is the only one whose split hides a threshold count (7 PRs, section 5).
  `figures-false` and `figure-unverified` (1 PR each) are one figures obligation
  with no vocabulary word, below threshold; left to the next window's count.
- **Literal `harness: class-open` elsewhere** is fixture or frozen evidence, not
  teaching: `tools/audit/seat/bus.sh`'s self-test verdicts (the bus routes on the
  head, not the class), `dev/audit/rca/1985/`, `dev/audit/rca/2028/`, and
  `dev/audit/rounds/round9/prestudy/friction-prestudy.md`.

## 5. #2409: the same cause on step 1

The mutation obligation (a reviewer mutant survives the PR's checks) was blocked on
**7 distinct PRs** under four words. Only one is in `VERDICT_CLASSES`:

| word | PRs |
|---|---|
| `mutation-vacuous` | #2275, #2305, #2365 |
| `test-vacuous` | #2297, #2360 |
| `mutant-survives` | #2376 |
| `vacuous-check` | #2400 |

`test-vacuous` is step 1's own prose ("the test is vacuous"). The fix teaches the
word: step 1 now reads `blocked <sha> mutation-vacuous: <mutant>`. Future windows key
all seven under `mutation-vacuous`, so the count the cron files is the obligation's
whole count rather than 3 of 7.

**The rework itself is the review working, and its substance has an owner.** 6 of
the 7 PRs are tooling-only diffs (no `custom_components/` path: #2275 #2297 #2305
#2360 #2376 #2400), where the CI `mutation` lane draws no mutant, so the reviewer's
own mutant is the only one. That is O10-policy-fixer-md's item 1 (#2305's friction:
"pinned by mutation-autofix" pins nothing under `tools/`), already in that group's
brief. #2365 (`custom_components/`) is a receiver half the fixer's tests missed, an
instance, not a recurrence.

## 6. #2410: a different cause, not this record's

The `mutation (family)` key's 3 PRs are exactly `mutation-vacuous`'s 3: the family's
other members, `mutation` and `mutation-survivor`, have no entry in
`blocked_rounds.tsv`. So the family arm filed the same three occasions twice. In
`tools/policy/policy_lint.mjs` the arm's comment says "a member already over
threshold fires its own id line above and the family does not double it", and the
code (`if (n < FRICTION_THRESHOLD) continue`, then push) has no such test. The
family's hand-kept member list also misses the synonyms of section 5. Both are the
keying rule, a different file and cause; section 8 names the owner.

## 7. Countermeasure

1. **The fix (policy), in this PR.** `fix-review.md` step 6 reads `blocked <sha>
   class-open: <seam>`; step 1 reads `blocked <sha> mutation-vacuous: <mutant>`.
   Step 8 drops "rather than reporting a number as confirmed", which restates its
   bold lead, to pay the tokens (`policy_lint.mjs --budgets`: 2444 of 2451, was
   2449). **These lines are policy**, for tvofi's approval at merge under mandate
   6175172275.
2. **The detector, held.** The arm (`detector.patch`, commit `3145aeff` of the
   unpublished seat branch) adds to the contract-examples block of
   `check-wave-script.mjs`: an example `blocked <sha> <A>: <B> ...` fails when `<B>`
   is a `VERDICT_CLASSES` word other than `<A>`, with a negative control (the #1414
   spelling must fire) and a null control (`harness: class-rule-missing` must not).
   It is not in this PR: open PR #2390 edits the same file, and the orchestrator
   ruled this group leaves it alone. It is carried to the orchestrator for the first
   group that edits `check-wave-script.mjs` after #2390 merges.

`node tools/policy/check-wave-script.mjs`, each on a scratch copy of the tree named:

| tree | rc | result |
|---|---|---|
| origin/main + detector | 1 | 189 passed, 1 failed: `fix-review.md teaches "class-open" as a reason under another class` |
| this head + detector | 0 | 191 passed, 0 failed |
| this head | 0 | 189 passed, 0 failed; `fix-review.md teaches block class "mutation-vacuous", and VERDICT_CLASSES carries it` |
| this head, step 1's word misspelt `mutation-vacous` | 1 | 188 passed, 1 failed: that arm, `routed to other` |
| this head, step 1 back to main's prose | 0 | 187 passed, 0 failed |

The existing arm pins step 1's spelling (row 4). It does not pin step 1's presence
(row 5): no arm asks that a step defining a block teach its word. That arm would also
live in `check-wave-script.mjs`, so it goes with the held detector. The script's
`FAIL (probe, expected) threw: deliberate` line prints on every row and is not
counted.

**What the fix changes:** future verdict bodies, not the keying rule. The window's
counts are a property of merged bodies and do not move. Counterfactual on this
window: with both spellings taught, `class-open` keys 13 PRs and the `harness`
residue is 2 (below threshold), one filing where there were two; `mutation-vacuous`
keys 7, where it keyed 3 and the family re-filed the same 3.

## 8. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **The two example lines: pass.** Standing cost: none at run time; the fix shortens
  a step-6 verdict by a word. Defect cost: one mis-keyed or split filing takes one
  disposition seat, estimated at **30 min** (an estimate from this seat's own
  re-derivation: `--stats` 4 min, the enumeration a few minutes, the write-up).
  P(recurrence): the `harness` key was filed in 4 of 5 windows (0.8). 30 min x 0.8 =
  24 min per window against a one-time edit.
- **The held detector: passes** on the same terms; the arm is a regex over examples
  the block already extracts. The whole script took 0.343 s without it and 0.383 s
  with it at this head (mean of 5 runs each, on scratch copies): at most 0.04 s a
  run, a few seconds a window at several pushes per PR.
- **Making `fixer.md` step 8 unconditional (every fix names an enumeration rule):
  refused.** In this window 13 PRs took a class-open block, median 131 min to the
  next verdict, against R9-RCA-2004's estimate of 3 min per PR over 125 PRs (375
  min, not measured). Prevention is not shown: #2283 named a census and was
  re-blocked on seams it missed. `class-open` is a review refusal, not an audit
  class in `bugclasses.json`, so `defect-root-cause.md`'s barrier obligation does
  not bind.
- **Sub-keying `harness: <free text>` in `statsHistogram`: refused.** It would make
  the histogram disagree with `parseVerdict`, which group 14 of
  `check-wave-script.mjs` refuses (#1475). The fix makes both readers deliver the
  right word at the source.

## 9. Recorded

- **Cause:** a contract step defining a block class does not teach its vocabulary
  word (step 6 taught another, #1414 `6bc932db`; step 1 taught none).
- **State:** (c).
- **Cost test:** the two example lines and the held detector pass; step-8
  unconditional and sub-keying are refused.
- **Countermeasure:** the step-1 and step-6 lines in this PR; the detector and a
  presence arm held for `check-wave-script.mjs` after #2390.
- **#2331:** 12 of the key's 13 PRs carry a class-open block keyed under the parent;
  the residue is 2 PRs. Closes on this record.
- **#2353:** the same obligation in the same window under its own word; a duplicate
  in substance, not by the filer's rule. Closes on this record.
- **#2409:** 3 of the obligation's 7 PRs keyed; the spelling is fixed here and the
  tooling-mutant substance is O10-policy-fixer-md's item 1. Closes on this record.
- **#2410:** not this record's cause (section 6). Owner: a group on
  `tools/policy/policy_lint.mjs`'s family arm (R10-POLICY-LINT-STATS is done; open
  #2406 and #2408 edit the same file).

## Evidence

`dev/audit/rca/harness-friction/`:

- `stats_v7.0.0.txt`: the `--stats` run.
- `window_prs.txt`: the 125 pull requests of the first-parent rule.
- `verdict_first_lines.tsv`: every `Fix review:` first line, by PR and time.
- `rounds.py`: the independent enumeration; `blocked_rounds.tsv`, its output.
- `detector.patch`: the held `check-wave-script.mjs` arm.
