# R10-RCA-HARNESS-FRICTION: one reviewer obligation, two friction keys (#2331, #2353)

The root-cause seat for **#2331** (`[policy] recurring friction: harness`, filed
2026-10-16T06:05Z) and **#2353** (`[policy] recurring friction: class-open`, filed
2026-10-17T18:26Z). Both were filed by the governance cron's friction step
(`tools/policy/friction_issues.mjs`). The seat ran apart from any fix
(`dev/governance/roles/root-cause.md`). It measured at origin/main `6e5753a4`.

**#2353 is not a `harness` issue.** Its key is `class-open`. Its window is the same
one, `v7.0.0..origin/main`. Section 2 shows that both issues measure the same
obligation, `fix-review.md` step 6, under two spellings.

## 1. The count, reproduced

`GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v7.0.0`
ran at `6e5753a4` in 2 min 39 s with rc=0. It counted 87 merged pull requests, and 51
of them carried a parsable verdict. It printed `9 / 14 harness` and `3 / 3 class-open`,
both at or over the threshold. Both issues quote these numbers.

The seat then listed every entry itself, without using `policy_lint.mjs`:

- The pull requests came from `git log --first-parent v7.0.0..origin/main` subjects
  `Merge pull request #N`. That gave 87.
- For each one, the seat read the first line of every comment
  (`/issues/N/comments`) and every review (`/pulls/N/reviews`).
- It kept each line matching `^Fix review:\s+blocked\s+[0-9a-f]{40}\s+(harness|class-open)`.

The script gave 29 blocked verdicts over all classes, the same total as the histogram.
The 17 `harness` and `class-open` entries:

| PR | verdict (UTC) | class written | reason's first word | to next verdict |
|---|---|---|---|---|
| #2283 | 10-15 16:46 | `harness` | `surviving` (mutant, and "the census misses ...") | 96 min |
| #2283 | 10-15 18:22 | `harness` | `class-open` | 159 min |
| #2293 | 10-15 19:28 | `class-open` | (seam) | 119 min |
| #2289 | 10-15 20:32 | `class-open` | (seam) | 138 min |
| #2283 | 10-15 21:01 | `harness` | `class-open` | 178 min |
| #2289 | 10-15 22:50 | `harness` | `class-open` | 98 min |
| #2283 | 10-15 23:59 | `harness` | `class-open` | 71 min |
| #2283 | 10-16 01:10 | `harness` | `over-claim` | 86 min |
| #2316 | 10-16 01:32 | `harness` | `class-open` | 126 min |
| #2320 | 10-16 03:10 | `harness` | `class-open` | 832 min |
| #2316 | 10-16 03:38 | `harness` | `class-open` | 144 min |
| #2323 | 10-16 04:43 | `harness` | `class-open` | 589 min |
| #2329 | 10-16 14:45 | `harness` | `class-rule-missing` | 28 min |
| #2320 | 10-16 17:02 | `class-open` | (seam) | 1231 min |
| #2344 | 10-17 08:42 | `harness` | `class-open` | 286 min |
| #2347 | 10-17 08:59 | `harness` | `class-open` | 296 min |
| #2346 | 10-17 12:59 | `harness` | `class-open` | 270 min |

"To next verdict" runs from the blocked verdict to the next verdict on the same pull
request. It is elapsed time, so it includes fixer, CI, reviewer and idle time.

- **`harness` totals: 14 entries over 9 PRs.** This matches the histogram. Eleven of the
  14 open with `class-open`. The other three are a survivor (#2283), an over-claim
  (#2283) and `class-rule-missing` (#2329). Those three fall in **2 PRs**.
- **`class-open` totals: 3 entries over 3 PRs.** This matches the histogram.
- **The step-6 class-open refusal, counted under both spellings: 14 entries over 9 PRs.**
  That is 14 of the window's 29 blocked verdicts. Elapsed round time was 4537 min, with
  a median of 168 min.

## 2. Named cause

**`fix-review.md` step 6 teaches `blocked <sha> harness: class-open <seam>`, but
`class-open` is a block class in its own right.** `VERDICT_RE` in
`.claude/workflows/web-fix-wave.js` takes the first word after the SHA as the class.
So both readers deliver `harness` for the spelling the contract teaches: `parseVerdict`
routes it, and `policy_lint.mjs` `statsHistogram` keys it. The word `class-open` reaches
a key only when a reviewer writes something other than the contract's example. This
window shows both spellings: 11 reviewers followed the example, and 3 did not.

Both halves came from one commit. `6bc932db` (#1414, 2026-09-22) added `'class-open'` to
`VERDICT_CLASSES` and wrote the step-6 example
`blocked <sha> harness: class-open <seam>`. Its commit message calls the word "the
`class-open` verdict word". So the vocabulary has carried the word since the day the
contract started teaching a spelling that never produces it.

R9-RCA-2004 (#2004, section 2) named the effect: `harness` is "a parent verdict class,
and the friction key counts the parent". It did not name the cause. It recommended
sub-keying the histogram on free text and did not build it, because the text after
`harness:` follows no grammar. The cause is narrower than that. One child already had its
own word, and the contract spelled it as a child.

**The cause has a measured cost.** The `harness` key was filed **5 times in 5 release
windows**: #1881 (v6.7.14), #2004 (v6.7.16), #2034 and #2136 (both v6.7.17), and #2331
(v7.0.0). Window v6.7.15..v6.7.16 stayed below threshold at 2/2. Each filing took a
disposition seat. Each seat found `class-open` the largest child:

- #2004: 4 of 7 entries.
- #2034 and #2136: 3 of the 6 PRs (#2057, #2068, #2075), as their disposition comments
  list them.
- #2331: 11 of 14 entries.

Each seat then closed the parent as "the mechanism working". This window adds a sixth
issue, #2353, for the same obligation under its other spelling.

## 3. Process state, with evidence

**(c): the process was followed and did not produce the intended result.**

- The reviewers obeyed `fix-review.md` step 6 as written. Eleven of 14 used its spelling.
- The friction cron keyed and filed as `policy_lint.mjs` specifies. Both counts
  reproduce exactly (section 1).
- A check existed for this seam. `tools/policy/check-wave-script.mjs`, block "the
  contract's verdict examples parse under the script's own grammar", extracts every
  backticked `blocked ...` example from the role contracts. It checks that each example
  parses (`example parses`), and that the first class word is taught (`teaches block
  class "<w>", and VERDICT_CLASSES carries it`). `harness: class-open` passes both arms,
  because `harness` is taught. The check's unit is the class word. It cannot see a
  second taught word sitting in the reason position, which is the shape that keys one
  obligation on another class.

This is not (b), because nothing was disobeyed. A firmer instruction to reviewers would
contradict the contract's own example. It is not (a), because the example check
existed. The countermeasure therefore changes the unit of the existing check and
corrects the example. It does not add an instruction.

## 4. How far the class reaches

- **Contract examples.** The extended arm (section 5) ran over every backticked
  `blocked <sha> <A>: <B>` example in `dev/governance/roles/` and
  `dev/governance/dimensions/`. It found exactly **one** whose reason opens with a taught
  word: `fix-review.md:29`.
  - `harness: class-rule-missing` (line 30) and `harness: design-trace-missing`
    (line 41) put untaught words in the reason position. They stay `harness` sub-reasons
    and do not split a key.
  - `git grep -nE '\`blocked <sha> [a-z-]+: [a-z-]+'` over the tree finds no other
    contract example of this shape.
- **Literal `harness: class-open` elsewhere.** These hits are not teaching:
  - `tools/audit/seat/bus.sh:779,784,890,915` are the bus self-test's fixture verdicts.
    The bus routes on the head, not the class, so they are left as they are.
  - `dev/audit/rca/1985/seq.txt`, `dev/audit/rca/2028/verdicts_review_refs.tsv` and
    `dev/audit/rounds/round9/prestudy/friction-prestudy.md:164` are frozen evidence.
- **The two readers still agree.** `group 14 -- the two readers of a blocked verdict
  deliver one class` in the same check stays green. The defect was never that the readers
  disagreed. Both read the contract's spelling the same wrong way.
- **The rework the key measures.** The `class-open` refusal is the window's largest
  rework class: 14 of 29 blocked verdicts over 9 of 51 reviewed PRs. Nine entries are
  each PR's first `class-open` block. The other 5 re-opened a class after a repair. Section 6 costs this separately.

## 5. Countermeasure, built and demonstrated

There are two commits on `rca/r10-harness-friction`. The detector came first.

1. **`3145aeff`, the detector.** `tools/policy/check-wave-script.mjs` adds an arm in the
   contract-examples block. An example `blocked <sha> <A>: <B> ...` fails when `<B>` is a
   `VERDICT_CLASSES` word other than `<A>`. The failure message names the spelling that
   keys correctly. The arm carries two controls on the predicate itself:
   - A negative control: the #1414 spelling must fire.
   - A null control: `harness: class-rule-missing`, an untaught reason, must not fire.
2. **`99636a0e`, the fix (policy).** `fix-review.md` step 6 now reads
   `blocked <sha> class-open: <seam>`. **This line is policy.** It is proposed for the
   orchestrator's approval under mandate (#201 comment 6175172275, scope all) and is not
   landed by this seat. If the line is refused, drop both commits, because the detector
   alone reds `wave-script`.

The runs, `node tools/policy/check-wave-script.mjs`:

| tree | rc | result | the arm |
|---|---|---|---|
| `6e5753a4` (main) | 0 | 186 passed, 0 failed | absent |
| `3145aeff` (detector, defect present) | 1 | 188 passed, 1 failed | `FAIL fix-review.md teaches "class-open" as a reason under another class: blocked <sha> harness: class-open <seam>` |
| `99636a0e` (fixed) | 0 | 188 passed, 0 failed | both controls `ok`; `fix-review.md teaches block class "class-open", and VERDICT_CLASSES carries it` |
| `99636a0e` with the predicate mutated to `return null` | 1 | 187 passed, 1 failed | `FAIL the shadow predicate fires on the #1414 spelling (negative control)` |

The mutant shows that the arm cannot go green by finding nothing. A predicate that never
fires fails its own negative control. The `FAIL (probe, expected) threw: deliberate` line
is printed at every row, including main. It is the script's own throwing-block probe and
is not counted as a failure.

**What the fix changes.** The fix changes future verdict bodies. It does not change the
keying rule. The current window's counts are a property of bodies that are already
merged, so they do not move (as #2331's own body says).

Counterfactual, measured on this window's entries (section 1): had step 6 taught
`class-open:`, the class-open blocks would have keyed `class-open` at 9 PRs and 14
entries. The `harness` residue would have been 2 PRs (#2283, #2329), below the threshold.
The cron would have filed one issue, under the name of the obligation, where it filed two.

In the two earlier windows whose dispositions list the sub-reasons, the residue would
still have reached 3 PRs:

- v6.7.16: #1960, #1994 and #1993's `env-matrix` entry.
- v6.7.17: #2025, #2070 and #2071.

So the fix would have stopped the `harness` filing in 1 of the 3 windows checked. In all
3 it would have filed the `class-open` count under its own name.

## 6. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

The unit is wall-clock per release window. There were five windows from v6.7.14
(2026-10-02) to `6e5753a4` (2026-10-17), about 3 days each.

**The countermeasure built (the example check and the policy line): passes.**

- Standing cost: the check ran in 1.054 s at main and 1.035 s at the fix, which is no
  measurable delta. The new arm is a regex over the examples the block already extracts.
  The reviewer spelling is one word shorter. Taking 0.02 s as a ceiling over about 300
  runs per window (87 PRs with several pushes each, in the `wave-script` job) gives at
  most about 6 s per window.
- Defect cost per occurrence: one mis-keyed filing takes one disposition seat.
  - The seat estimates **30 min** per seat. This is an estimate, not a measurement.
  - Its basis is this seat's own work: re-deriving `--stats` took 2 min 39 s, enumerating
    the verdicts from the API took a few minutes, and the disposition had to be written.
  - #2004 took a full RCA seat and a reviewed pull request (#2014), so it cost far more.
- P(recurrence): the `harness` key was filed in **4 of 5** windows, P = 0.8. In this
  window the same obligation was filed twice.
- Expected cost at 30 min x 0.8 = **24 min per window**, not counting a split second
  issue such as #2353. That is greater than 6 s.

**Making `fixer.md` step 8 unconditional, so every fix names and lists an enumeration
rule: not built, with the reason recorded.** R9-RCA-2004 section 4a costed and refused
this.

- Defect side: in this window, 9 PRs took their first `class-open` block. The median
  elapsed round on those 9 was 270 min.
- Countermeasure side: at R9-RCA-2004's estimate of 3 min per PR (not measured), 87 PRs
  is about 261 min per window.
- Prevention is not shown. The merged bodies of 8 of the 9 PRs name a census, an
  enumeration or a rule (a body grep for `enumerat`, `census` and `rule`). #2283 was
  re-blocked three times on seams its own census did not cover. A named rule that is
  narrower than the class reaches the same review. The independent reviewer is the
  cheapest detector that judges class membership. This seat did not read the
  blocked-head bodies, so the prevention rate is unmeasured, and the refusal rests on
  that.
- `class-open` is not an audit class in `dev/audit/config/bugclasses.json`. It is a
  review refusal, so the barrier obligation in `defect-root-cause.md` does not bind.

**Sub-keying `harness: <free text>` in `statsHistogram`: refused.** R9-RCA-2004 raised
the noise-key objection, and it still holds for the untaught residue. Promoting only
taught words inside `policy_lint.mjs` would make the histogram disagree with
`parseVerdict`. Group 14 of `check-wave-script.mjs` exists to refuse exactly that
disagreement (#1475). The fix above makes both readers deliver `class-open` from the
contract's spelling, at the source.

## 7. Recorded

- **Cause:** `fix-review.md` step 6 spells a taught block class as `harness`'s reason
  (#1414, `6bc932db`).
- **State:** (c).
- **Cost test:** the example check and the step-6 line pass, at about 6 s against
  24 min per window. Making step 8 unconditional and sub-keying are refused, with the
  numbers above.
- **Countermeasure:** the `check-wave-script.mjs` arm (`3145aeff`), shown failing on the
  defect and passing on `99636a0e`. The step-6 policy line awaits the orchestrator's
  approval.
- **#2331:** 8 of the `harness` key's 9 PRs carry a `class-open` block keyed under
  the parent. Without those, the residue is 2 PRs (#2283, #2329). With the cause fixed at the contract, it closes on
  this record.
- **#2353:** the same obligation in the same window, under its own word. It is not a
  duplicate by the filer's rule, which is one issue per key per window and was applied
  correctly. It is a duplicate in substance. The rework it measures is the reviewer
  catching real open seams. All 9 PRs were repaired and merged, and the step-8
  countermeasure is refused above. It closes on this record. A later window that
  crosses the threshold re-files under `class-open`, which is now the name every
  step-6 block keys on.

## Evidence

`dev/audit/rca/harness-friction/` holds the evidence:

- `stats_v7.0.0.txt`: the `--stats` run.
- `window_prs.txt`: the 87 pull requests.
- `verdict_first_lines.tsv`: every `Fix review:` first line, by PR and time.
- `rounds.py`: the independent enumeration, which produced section 1's table.
- `blocked_rounds.tsv`: the output of `rounds.py`.
