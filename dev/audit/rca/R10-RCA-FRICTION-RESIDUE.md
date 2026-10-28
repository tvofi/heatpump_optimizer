# R10-RCA-FRICTION-RESIDUE: five friction keys, and a destination no producing seat may write (#2428, #2436, #2437, #2429, #2438)

The root-cause record for the recurring-friction residue that
`dev/audit/rca/R10-RCA-HARNESS-FRICTION.md` (#2561) left unmeasured: the keys
`carry-missing` (#2428, re-filed as #2855), `other` (#2436), `root-cause-unanswered`
(#2437), and the two rule ids the verdict histogram also counts, `.claude/rules/ci-autofix.md`
(#2429) and `.claude/rules/finding-propagation.md` (#2438). It ran apart from any
fix (the root-cause role contract); it lands no production code.

**Merge base and window.** Every figure below was taken on 2026-10-27 with the
group's merge base at `6eb552157b63d1e98a9653250789d9fe0027b5bc`, which was also
`origin/main` at the time of measurement. The histogram window is
`v7.0.4..origin/main`, tag `v7.0.4` = `b448d26063cdb56aef915ceb604b807a885f9d71`.
Nothing is carried from #2561: its figures are for `v7.0.0..origin/main` at
`df6ca4bc` and are quoted below only as the control they are.

## 1. The instrument the brief named does not exist

The brief's method is "`rounds.py --stats` over `blocked_rounds.tsv`". It cannot
be run, and the failure is silent:

```
$ python3 dev/audit/rca/harness-friction/rounds.py --stats <...>/blocked_rounds.tsv
rc=0   stdout 0 bytes   stderr 0 bytes
```

`rounds.py` takes one argument, a **directory** of per-PR `.tsv` files
(`sys.argv[1]` at its line 14, `glob.glob(os.path.join(sys.argv[1], '*.tsv'))`).
`--stats` is not a mode; it becomes the directory name, the glob is empty, and
the script prints nothing and exits 0. The same is true of
`rounds.py blocked_rounds.tsv`: a file is not a directory. **A zero here is
vacuous** — it is the exact shape `CLAUDE.md` rule 1 warns about for the gate.

Two instruments do work, and they are the ones used below:

- `node tools/policy/policy_lint.mjs --stats --since v7.0.4`, rc=0 in 669 s
  (`dev/audit/rca/harness-friction/stats_v7.0.4.txt`). It reads the same
  verdict grammar `rounds.py` does.
- `rounds.py <dir>` over the window's 218 fetched per-PR files, one
  `<PR>.tsv` each (`blocked_rounds_v7.0.4.tsv`, 132 block rows over 84 PRs,
  plus its SUM lines). The fetch is `fetch_prs.py` in the seat's scratch, and the
  enumeration `analyse.py`; both use `rounds.py`'s regex verbatim, so this is the
  same reader, not a second classifier.

**Control: the two readers agree on every key.** The independent enumeration
finds 132 blocked verdicts over 84 PRs; the histogram's rows reproduce each key's
distinct-PR count exactly (`carry-missing` 26, `mutation-vacuous` 8, `class-open`
6, `root-cause-detectable` 3, `harness` 3, `mutation-survivor` 3, `regression` 3,
`other` 2, …). The denominator is not the window's merge count: **173 of 218**
merged PRs carried a parsable verdict; 45 carried none (44 of them `record`
titled). Every rate below states which denominator it uses.

## 2. The counts, at this base

| key | PRs / entries | median min to next verdict | would-open |
|---|---|---|---|
| `carry-missing` | 26 / 30 | 103 | yes (#2855) |
| `mutation-vacuous` | 8 / 9 | 111 | yes (#2660) |
| `class-open` | 6 / 13 | 153 | yes (#2784) |
| `mutation-survivor` | 3 / 5 | 119 | yes (#2840) |
| `root-cause-detectable` | 3 / 3 | 181 | yes (#2875) |
| `harness` | 3 / 3 | — | yes (#2597) |
| `regression` | 3 / 3 | 153 | yes (#2860) |
| `root-cause-unanswered` | 2 / 2 | 219 | no |
| `root-cause-unrecorded` | 1 / 1 | 73 | no |
| `other` (literal) | 2 / 3 | 164 | no |
| the `other` route (untaught ∪ literal) | 52 / 67 | — | no single row |

Twelve would-open lines were printed; `blocked_rounds_v7.0.4.tsv` holds every
row they are counted from. The keys below are the five the brief scopes, plus the
two it does not (#2593, #2597) and the four extra issues the roster lists.

## 3. `carry-missing` (#2428, #2855): the destination is prose no producing seat may write

**Named cause.** The rule names two destinations for a finding that constrains a
live group: the group's `brief` string in the roster, or — only when no live
group covers the destination issue — a `dev/programme/carries/carry-<N>.json`
file (`finding-propagation.md`, "Where it goes"; `brief_lint.mjs`'s carry-file
comment). A fixer reads its roster group and nothing more (`fixer.md`), and the
PR and its row are written by the orchestrator's `handoff_push.sh`; two seats
state the consequence in their own friction entries — #2612 "a seat with
handoff-only write access cannot land a carry into a policy brief (D0.md) or a
roster", #2708 the dispatch allows pushes only to two return refs so "the
orchestrator corrects the roster carry". So it cannot write the first. For a
**group** destination there is no `N` at all, so the second does not exist.
**The seat's marker names a
stage; the text that the destination seat reads has no writer on the producing
PR.** The reviewer blocks step 10 (`carry-missing`) because the destination
brief does not hold it — which is true, and which no seat on that PR could have
made untrue.

**Process state: (d), with a (c) component.** The rule is sound; its precondition
— that the producing pull request can put the text in the destination — was
removed by the roster's read-only role for a fixer (`fixer.md`, and the two
measured entries above) and by the roster's move to
`dev/programme/rosters/` (R10-TICK). The (c) component is the one artefact a
seat *can* write: a carry file at an issue a live group covers is meant to be
refused (`brief_lint.mjs` calls it the failure the file replaces), and at this
base the refusal cannot fire.

**The refusal is blind — #2561's finding, still live, and its destination held
something else.** `rosterIssues()` with no argument reads
`.claude/workflows/wave-*-groups.json` and `dev/programme/carries` — not
`dev/programme/rosters/`, where `roster_lib.py` says the one owner put them.
#2561's own `## Friction` entry states this finding and measured a planted
`carry-2428.json` at `0 error(s)`, and routed it `Carry: #201`. At this base:

- `rosterIssues()` indexes **1** issue (457, from the round-3L roster);
  `rosterIssues('dev/programme/rosters')` indexes **76**, including every live R10
  group's issues;
- `dev/programme/carries/carry-201.json` holds no text about this finding — its
  entries are other RCA findings — so `#201` was accepted as a destination
  because *a* carry file exists at 201, not because this text landed. Six days
  later the instrument is unchanged and the finding is in no file a seat reads.

That is `brief_lint.mjs`'s own "case 3, existence not authorship" operating on
the *finding about itself*. Perturbation and controls, run here:

- as shipped, a carry file at issue 2492 (covered by the live `R10-SAV-COMFORT`)
  is **accepted**, rc=0;
- with the programme roster passed, the same file is **refused**: `issue 2492
  already has a live roster group (wave-r10-groups.json R10-SAV-COMFORT)`;
- control A, an issue no group covers (999999): accepted under both, so the
  acceptance above is not a blanket failure to load;
- control B, issue 457 — the only issue the shipped index sees: refused under the
  shipped index, so the arm is live, just pointed at the wrong directory.

CI runs the no-argument path (`tests.yml`, `prepr.sh`), so the arm is blind in
exactly the place it is meant to enforce. Its self-test is green because it
passes a **fixture** roster directory: the no-argument run here prints
`TOTAL: 0 error(s) across 48 file(s)` (47 carry files and the round-3L roster),
while its own acceptance assert prints the refusal against
`wave-probe-groups.json PROBE-G1` from that fixture. The arm is demonstrated on a
roster no production run reads.

**The destination-text check is not mechanically decidable, measured.** Two
predicates over the 205 finding items in the window that name a group
destination (`pred*.py` in the seat's scratch):

- "the destination brief contains the item" — matched by the 8-hex id
  `carry_audit.py` prints: fires on **205 of 205**; zero quiet.
- "the destination brief names the producing PR (`#N`)": fires on **193 of 205**,
  quiet on 12. Of the fires, **29 are on PRs that were never blocked at all** and
  merged. A predicate that reddens 29 clean merges is one seats route around —
  the same conclusion `brief_lint.mjs` records from its own 2026-09-10
  measurement of 6 of 6, now reproduced on a larger window.

**Cost test.** In `v7.0.4..origin/main`, 30 entries on 26 PRs: **11.9% of the
window's 218 merges**, against #2561's `v7.0.0` control of 12 of 229 = **5.2%**
— the key has more than doubled. Elapsed time from each block to that PR's next
verdict (fixer + CI + reviewer + idle) sums to **5076 min, median 103 min**.
23 of the 30 entries name a destination group the text is not in; the mentions
span 20 groups, at most 4 for one (`R10-ORCH-MACHINERY`), so this is not one
group's neglect. `P(recurrence)=1`: filed in both windows (#2428 at 21/24,
re-filed as #2855 at 26/30, and this seat reproduces 26/30 exactly). The
*deterministic* half — the blind index — was recorded once already (#2561,
2026-10-21, routed to #201) and did not land, so its P is 1 for the finding as
well as for the class.

**Countermeasure, two parts, both check-shaped.**
A1. **Point the index at the rosters.** `rosterIssues()`'s no-argument path reads
`roster_lib.ROSTERS_DIR` as well. Demonstration: indexed issues 1 → 76; the
carry-2492 file refused; control 999999 still accepted. One line, and its
red/green control is recorded above. Owned by `R10-FLOW-TOOLKIT-MODEL`, whose
carry holds A1 and A2 with this acceptance — a group, not a tracking issue,
because `#201` is the destination that absorbed the last attempt at it.
A2. **Fold at merge, then assert.** The orchestrator, before merging a PR whose
body names `Carry: <GROUP>`, appends that item (with the 8-hex id
`carry_audit.py` computes) to the group's brief. The post-fold assertion is the
same id predicate that is unusable *pre*-fold: after the fold writes the id it is
quiet by construction, and it fires if the fold is skipped. That is the
distinction — the predicate is exact about whether the tool ran, not about
whether prose is a carry.

Refused: redefining the body's `Carry:` line as the destination. It is the one
change that would make the count fall without a destination seat ever reading the
finding, which is what the rule exists to prevent.

## 4. `other` (#2436) and `body-stale` (#2593): one open vocabulary, two readers, no key

**Named cause.** A reviewer can write any class word: `VERDICT_RE` in
`.claude/workflows/web-fix-wave.js` tolerates a word it was never taught, and the
wave's `parseVerdict` routes it to `other`. The histogram deliberately keeps the
raw word as its own row (the drift signal, `policy_lint.mjs`'s family comment).
The threshold's unit is therefore **the spelling**, and an obligation whose
spelling changes each time never reaches three: measured here, **46 untaught
words hold 52 PRs / 67 entries**, and **44 of the words sit at one or two PRs
each, holding 47 PRs / 56 entries**. **36 PRs were blocked only by untaught
words** — no taught key saw them at all. The literal `other` row the filings see
is 2 PRs / 3 entries, while the wave's own `other` route is **52 PRs / 67
entries, 26× the filed row**.

**Process state: (c).** The grammar, the drift signal and the threshold are each
obeyed; the intended result — a recurring obligation files an issue — does not
follow, because nothing folds the open vocabulary. `mutation-vacuous` and
`mutation-survivor` were taught/declared and their family fires; the untaught
vocabulary has no family and cannot have a declared one, since a word that is
untaught is by definition not on a list.

`body-stale` (#2593, 3/3 in `v7.0.2`) is a member of the same vocabulary: in this
window it is 1 PR, and its siblings `body-head-stale` 2, `body-figure` 1,
`body-claim-wrong` 1, `figure-false`, `figure-uncited`, `figure-unverified`,
`figure-wrong`, `figures-unverified` 1 each — **nine spellings of one body-drift
obligation over 10 PRs, no row at 3**. The filed key cannot recur because the
spelling moves.

**Cost test.** 36 PRs blocked only by untaught words = **16.5% of 218 merges**
whose friction has no route to a filing; the derived family below would count
46 PRs (52 less the 6 held by the already-filed `mutation-survivor` and
`regression`, the #2410 subtraction). Countermeasure cost: one derived row, O(rows)
on a pass whose 669 s is the network, not the fold. `P(recurrence)=1` in this
window alone.

**Countermeasure (drafted; policy tooling, owner approval).** Add a **derived**
family to `statsFamilies`: every histogram key not in `VERDICT_CLASSES` folds to
one `other (untaught)` row, members computed at read time so no list can go stale,
with the #2410 subtraction applied as for the declared families. Demonstration:
the union is 52 PRs / 67 entries; after subtracting the 6 PRs the filed members
hold, the family is **46 PRs** and fires. Control: the fold is additive, so every
taught row — `other` literal included — prints byte-identically; and with no
untaught word in a window it prints no row, the declared-family rule. Refused:
teaching 46 words (a list that cannot be complete), and changing `parseVerdict` to
stop routing to `other` (it would erase the drift signal the histogram is built
to keep).

## 5. `root-cause-unanswered` (#2437) and its family: one obligation, three words

**Named cause.** The root-cause obligation is written under three class words —
`root-cause-unanswered` 2 PRs, `root-cause-detectable` 3, `root-cause-unrecorded`
1 — and `FRICTION_FAMILIES` has no `root-cause` entry. The threshold counts a
spelling, so the obligation's 6 PRs / 6 blocks are three counts of 1–3. The
checks named are as fragmented as the words: `closures` (#2632),
`instrument-self-tests` (#2664), `tests / nightly-ha` (#2753),
`governance / delivery-status` (#2837), `pr-contract` (#2841 and #2869), and
`tests/closure.py` selftest (#2869) — **the most any one check reaches is 2 PRs**,
which is #2437's own finding ("7 blocks, 4 checks, none on 3 or more PRs")
re-measured, not carried.

**Process state: (c).** The split is deliberate and taught (`fix-review.md` steps
10–11); the family map was extended for `mutation` (#1825) and `environment` but
not for this obligation, so its unit is the word.

**Cost test.** 3 of the 6 PRs are invisible to any filing at this base
(`root-cause-unanswered` 2, `root-cause-unrecorded` 1); the family is 6 PRs, one
obligation. Countermeasure cost: one member list and one family declaration,
evaluated in the same pass. `P(recurrence)=1` — this window and #2561's.

**Countermeasure (drafted; policy tooling, owner approval).** Declare
`{ name: 'root-cause', members: ['root-cause-unanswered', 'root-cause-detectable',
'root-cause-unrecorded'] }`. Demonstration: union 6 PRs; the filed member
(`root-cause-detectable`, 3) is subtracted per #2410; **family 3 PRs** and fires.
Control: #2875 already files the 3-PR member, so this window's marginal filing is
zero — the family's value is that the *next* window with a different split files
once instead of not at all, which is the case the map was built for.

**#2479's item, taken here.** Its disposition — "a cross-run count before an
answer of 'not a recurrence'" — is the count in this section: per check, across
the window, `pr-contract` 2 PRs and five others 1 each. The method is measured;
the policy sentence that requires it is the owner's.

**#2875 is unowned.** The 3-PR member that fires in this window is an open issue
no roster group lists — the routing audit's own subject (`carry_audit sweep
--issues`), and the same existence-not-ownership gap as #2561's `#201` route.
The obligation's countermeasure is filed under #2437; the ownership repair is
`R10-ORCH-ROSTER-SCHEMA`'s, whose STRANDED-carry report names an issue no live
group lists.

## 6. `harness` (#2597), `class-open` (#2784), `mutation-vacuous` (#2660), `mutation` family (#2410)

**#2597, `harness` 3 / 3.** The three blocks are three different children:
`class-rule-missing` (#2524), `design-trace-missing` (#2780),
`finder-harness-misreported` (#2843). **Zero are `harness: class-open`** — the
compound word #2561 taught a spelling for. #2561's countermeasure held; #2597 is
a recurrence of the parent word over *different obligations*, not of the class-open
obligation. Cause: `harness` is a category, and the reviewer's vocabulary offers
it when the child has no word. State (c). **Refusal, with the cost test:** the
three children are not one obligation, so a `harness` family would be the wrong
map (the family map folds siblings of one obligation); teaching three child words
files each at 1 — below the threshold — and buys no filing; the only real
alternative, a per-child check, is #2561 §8's and #2704 item 11's twice-recorded
refusal. Cost of the countermeasure (two policy/tooling edits) exceeds a benefit
of zero filings in this window; `P` of a class-open recurrence is 0.

**#2784, `class-open` 6 / 13.** Every entry names the seam the change left open
(#2697 six blocks on one merge-call parser, #2706 a torn write, #2707 an
agreement lane, #2711 two getter shapes, #2770 a sweep, #2819 a plan slot):
`class-open` is the reviewer refusing a change that closed some of a class.
#2561's countermeasure — teach the word and the step — is in force and these six
are its residue, not its recurrence. State (c), as #2561 §9 records it. The
further countermeasure is refused in
#2561 §8 and #2704 item 11; this seat does not reopen that refusal.

**#2660, `mutation-vacuous` 8 / 9.** Control against the fix: 7 PRs / 8 entries
before `662a380` merged (R10-POLICY-FIXER-MD, 2026-10-25 01:02:55Z) and
1 PR / 1 entry after, inside this 5.2-day window. #2561's spelling fix and the
`fixer.md` wording landed and the key fell from 8 entries on 7 PRs to 1 entry on
1 PR: seven of its eight pre-fix entries are gone. Held; residue 1.

**#2410, `mutation (family)`.** Measured at this base: the member union is
12 PRs; the filed members hold 11; the family row is **1 PR / 2 entries** — the
#2410 subtraction is implemented and the family fires only for what no member
files. Control: without the subtraction the family would be 12, which is the
double count #2410 records. Held; no new countermeasure.

## 7. `ci-autofix` (#2429): an unbounded wait and an unmeasured claim

Three PRs, three entries, and they are two gaps in one rule:

- #2632 `unclear`: `mutation-autofix` pins only killed mutants, so a site whose
  only driver times out stays `ADDED UNPINNED`; "nothing tells a seat to stop
  waiting for the bot after one timed-out pin run".
- #2698 `cost`: CI's `mutation-pins` shards were still `in_progress` hours after
  `tests / mutation` concluded, so the pin the body relied on never came.
- #2834 `cost`: a body wrote ten sites as "pinned by `mutation-autofix`" without
  driving them, two were survivors the bot could not pin, "which cost a CI round
  and a fixer round"; the rule says to run `--pin-killed` only when the bot goes
  red, so a body can predict a pin it has not measured.

**Named cause.** `ci-autofix.md` says to wait for the bot and to run
`--pin-killed` only on a red; it states no terminating condition for the wait and
does not require a pin claim to be measured. **State (c):** the rule is obeyed,
and the two things a seat then does — wait, and assert — have no bound.

**Cost test.** 3 PRs in this 5.2-day window; #2834's owner names its own cost (a
CI round and a fixer round); #2698 is hours of a seat's wait.
Countermeasure: one sentence with a bound (if `mutation-pins` has not concluded by
the next `tests / mutation` conclusion, the pin is owed by the handoff and the body
says `unmeasured`), plus "a body says `pinned` only when `--pin-killed` ran on
this head". `P(recurrence)=1` (3 of 3). The countermeasure is a policy edit to a
capped file, so it is **drafted and left to the owner**, not landed.

## 8. `finding-propagation` (#2438), and C3's #2612 row

Five PRs, five entries, and five different ways a carry is unreadable by its
destination:

- #2612 `unenforced`: "a seat with handoff-only write access cannot land a carry
  into a policy brief (D0.md) or a roster" — the same cause as section 3, stated
  by a seat in October.
- #2645 `stale`: the carried null control asks to reproduce figures "in no tree
  or ref this seat can read".
- #2765 `unclear`: a carry's statistic says "trips at 4 or fewer first-pass
  merges" where the arm implements incidence.
- #2708 `unclear`: the dispatch allows pushes only to two return refs, so a
  refuted reading in a roster carry cannot be corrected by the seat that found
  it — "the orchestrator corrects the roster carry". This is #2612's write-access
  condition from the other side: the seat can neither write the destination nor
  correct it.
- #2871 `contradiction`: a ruling names `R10-FLY-WIP`, which neither roster
  holds; the intended group is `R10-FLOW-WIP`.

**Named cause.** A carry is one seat's prose consumed by another, and only its
*existence* is resolved: a `Carry:` marker to a group not in the roster is
refused, but a destination that exists and received nothing passes both layers by
design (`brief_lint.mjs`, cases 3–4), and a carried control's figures and
statistic are not required to name their enumerator. **State (c).** #2612's row is
dispositioned here, not left with `R10-BRIEFS-FOLD` (done, and did not implement
it): its finding is section 3's cause, and its countermeasure is A1 + A2.

**Cost test.** 5 entries over 5 PRs; each is re-derived by the destination seat,
and two entries record the re-derivation itself (#2871 the fix review corrects
the group name; #2708 the orchestrator corrects the roster carry). This seat
cannot time that from the window and does not invent a figure; the countermeasure
is one lint arm plus one sentence, which cannot cost more than the manual rewrite
it replaces. `P=1` (5 PRs in this 5.2-day window).

**Countermeasure (drafted; policy, owner approval).** (i) `brief_lint` lints a
carry's `control` for a resolvable enumerator exactly as it lints `brief`, so
"the FUTURE-STATE section 2 figures" (#2645) and a bare statistic (#2765) fail;
control: a control naming `dev/audit/harnesses/x.py` passes. (ii) one sentence in
`fix-review.md`/`judge.md`: a ruling that names a destination stage states it as a
`Carry:` marker, so `R10-FLY-WIP` is refused by the existing check instead of
corrected by hand (#2871). Refused: a policy-wide scan for group-shaped tokens in
prose — section 3 measures that shape at 205 of 205.

## 9. C1 and C2

**C1, #2452's census cost: recorded refusal.** The `cost` entries say
`tests/card.mjs` takes 159.43 s of CPU (322.45 s real) and the 182 plants took
3 h 18 m over six lanes. The census is the *cheap* detector: it replaced a
spelling list, and a spelling list is the defect it closed (#2317's class, a
navigation in a handler the dynamic arm did not drive). A cheaper census is the
spelling list. The cost test therefore fails for every cheaper design and passes
for this one: the payment buys the class coverage, and no countermeasure is
proposed. **Not re-measured here**: the plant-driven census needs the solver
venv, which this record seat does not run; the figure is the producing seat's and
is labelled as such. `Carry: dismissed: cheaper census is the spelling list that failed`

**C1, #2479's cross-run count: taken.** Section 5 is the count, per check, over
the window. Dispositioned here; the policy sentence is the owner's.

**C2, this group's `issues` list.** The carry text says "seven numbers"; the
roster at this base holds **eleven**: 2410, 2428, 2429, 2436, 2437, 2438, 2593,
2597, 2660, 2784, 2855. The four the carry did not name (2410, 2660, 2784, 2855)
all fired in the same window, which is itself an instance of this record's
subject — a carried count is stale by the next window. Every one is dispositioned
below; none is left unowned. #2428 is closed (superseded by #2855) and is also
listed by the live `R10-FLOW-JIDOKA`, so it has two owners at this base.

## 10. Dispositions

| issue | key | disposition |
|---|---|---|
| #2410 | `mutation (family)` | held: family 1 PR after the #2410 subtraction (control: union 12) |
| #2428 | `carry-missing` | closed; superseded by #2855, whose 26/30 this record reproduces |
| #2429 | `ci-autofix` | cause + drafted countermeasure (section 7) |
| #2436 | `other` | cause + derived-family countermeasure (section 4) |
| #2437 | `root-cause-unanswered` | cause + `root-cause` family (section 5) |
| #2438 | `finding-propagation` | cause + control-enumerator lint, and C3's #2612 (section 8) |
| #2593 | `body-stale` | same vocabulary as `other`; 9 body-drift spellings over 10 PRs / 10 entries, no row at 3 (section 4) |
| #2597 | `harness` | #2561 held (0 `harness: class-open`); refusal recorded (section 6) |
| #2660 | `mutation-vacuous` | held: 7/8 before `662a380`, 1/1 after (section 6) |
| #2784 | `class-open` | measured; the countermeasure refusal stands (section 6) |
| #2855 | `carry-missing` | cause + A1/A2 (section 3) |

## 11. Not established here

- The census's 159.43 s was not re-timed (needs the solver venv); it is quoted
  from #2452's `cost` entry and labelled.
- The brief's `rounds.py --stats` was not run *as named*, because it is not a
  mode (section 1); the substitute instruments and their agreement are given.
- `brief_lint`'s no-argument run completes rc=0 (48 files, 0 errors) and lints
  only the round-3L roster and the carry files; the R10 roster linted explicitly
  is also 0 errors. The roster-index defect in section 3 was established by
  calling `rosterIssues()` and `checkCarryShape()` directly, which is the same
  code the run executes.
- The policy and tooling changes in sections 3, 4, 5, 7 and 8 are **drafted, not
  landed**. They are owner-approved changes and this record is not the PR that
  makes them.

## Evidence

`dev/audit/rca/harness-friction/`:

- `stats_v7.0.4.txt` — the `policy_lint --stats --since v7.0.4` run at
  `6eb552157`, rc=0, 669 s; one host path in its second line replaced by the
  `~` form `ref_privacy.py scrub --write` prescribes, nothing else changed.
- `blocked_rounds_v7.0.4.tsv` — `rounds.py` over the window's 218 per-PR files:
  132 block rows over 84 PRs and its SUM lines. `blocked_rounds.tsv` (#2561's
  `v7.0.0` window) is untouched.
- `rounds.py`, `stats_v7.0.0.txt` — #2561's instruments, unchanged; the control
  the `v7.0.4` figures are compared against.

Re-measurement is the two commands in section 1, plus the per-PR fetch
(`gh api` `issues/<n>/comments` and `pulls/<n>/reviews`, first line each,
`created_at`/`submitted_at`), which reproduces every row.
