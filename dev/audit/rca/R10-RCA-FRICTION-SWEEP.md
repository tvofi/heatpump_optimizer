# R10-RCA-FRICTION-SWEEP: sufficiency of the existing friction records, the landed countermeasures, and three carried measurements

The ledger record for the group that answers the recurring-friction keys
`R10-FRICTION-REGRESSION` left owed. One record per key sits in its own file
(`R10-RCA-ROOT-CAUSE-DETECTABLE.md` #2875 and #2865, `R10-RCA-CLASS-OPEN.md`
#2950, `R10-RCA-MUTATION-VACUOUS.md` #2998 and #2942). This file judges the four
records that already existed, answers the carried measurements that have no
key of their own, and shows the demonstrations for the policy tooling this
group lands.

**Merge base and window.** All figures measured 2026-11-06 at `origin/main`
`7e8939d38`, window `v7.0.4..origin/main` (tag `b448d26063cd`): 517 merged
pull requests, 450 with a parsable verdict, from `node tools/policy/policy_lint.mjs
--stats --since v7.0.4` (the walk takes about 11 minutes). Earlier records'
windows are controls.

## 1. The four existing records, judged for sufficiency (not rewritten)

Each is judged against `root-cause.md`: a named cause, a process state, a cost
test with numbers, a countermeasure or a recorded refusal. All four carry all
four. They are left as they are; the re-measure at this base is appended
here, never into them.

| record | issue | verdict | why, and the re-measure at this base |
|---|---|---|---|
| `R10-RCA-MUTATION-SURVIVOR.md` | #2840 | **sufficient** | cause (autofix pins kills only), state (c), cost test (P = 4/28, 161 min), countermeasure B landed, C carried, A refused. Key now reads `mutation-survivor` **9 PRs / 11 entries** (#2579, #2817, #2820, #2912, #2962, #3001, #3097, #3150, #3153): recurring, but its tools/ population is the one `R10-RCA-MUTATION-VACUOUS.md` section 5 re-prices, and C is the group's `R10-FLY-LEDGER-SAMPLE`'s. Not credited or refuted: which of the 9 are on heads after B landed is not derived. |
| `R10-FRICTION-GATE-SCOPING.md` | #2835 | **sufficient, with section 2 below** | cause (inherited `BASH_ENV` re-prepends the toolchain), states (d)/(c)/(b), a countermeasure landed (`_stub_path_env` and its red/green check). It prices 10 PRs / 11 entries; the key reads **12 / 13** now. |
| `R10-RCA-FIXER-MD-KEY.md` | #2895 | **sufficient** | cause (cloud seats lack the toolchain the prompt promises), state (d), cost estimate labelled untimed (5-15 min), the session-start `toolchain:` hook built, owner action named. Key now reads `tools/audit/briefs/fixer.md` **17 PRs / 25 entries** against its 8 / 11. The record found one group (A) owed a defect; the growth is not decomposed here and was not the question. This session's own start-up printed the `toolchain:` line and `cloud-setup.sh --check` read OK: one observed instance of the hook doing its job, not a measurement. |
| `R10-RCA-FRICTION-CLAIM-FALSE.md` | #2907 | **sufficient** | cause (a ruling cites figures and never runs its stated rule on its instances), states (a)/(b)/(d), the one-sentence `proposal-triage.md` countermeasure landed. Key now reads `claim-false` **5 PRs / 9 entries** (4 PRs in its window). Whether the 5th is after the sentence landed is not derived. |

`R10-RCA-FRICTION-REGRESSION.md` (#2860) landed in #3000 and is not part of
this judgement; the key now reads `regression` 4 PRs / 4 entries (3 in its
window). The record's `L` mechanism (a CI browser lane no local path runs) is
the same shape as `R10-RCA-ROOT-CAUSE-DETECTABLE.md`'s cause A.

## 2. #2835 on `gate-scoping.md`: Carry 7's measurement (measure first)

The carry asks: name the PRs and the rule hit each made, then decide whether
the keying rule or the gate changes. It was written when the key read 6 PRs.
At this base `.claude/rules/gate-scoping.md` reads **12 PRs / 13 entries**
(threshold 3).

Entries named in PR bodies' `## Friction` sections, read by body search over
the window and then each line: BASH_ENV `#2698, #2707, #2834, #2837`;
interpreter `#2627, #2870`; lease and runtime `#2873` (two entries),
**`#2968`**; closures recording `#2780`; no step for the check `#2622, #2700`.
That is 11 PRs; `#2968` is the only one the existing record does not name
(its entry: the scoped gate "outlives the 30-minute background-task limit",
`arch_score.py` alone 1407 s). The 12th PR the histogram counts was **not
identified** by this search; the record does not claim it.

Decision on the carry's question:

- **The keying rule does not change.** The key is the rule file; the 12 PRs
  fall into five causes (BASH_ENV 4, interpreter 2, lease/runtime 2, closures
  recording 1, no step 2) and one unidentified. Splitting by cause leaves
  BASH_ENV at 4 and everything else below 3, which is the existing record's
  finding.
- **The gate does not change for #2968 and #2873's runtime half.** Two PRs of
  "the scoped gate outlives a 30-minute cap": below the threshold of 3, and the
  cap is a property of the seat's background-task limit, not of the gate. This
  seat's own brief says to wait with Monitor windows up to an hour, which is
  the working answer for a seat that has one. Refused at 2 instances; the cost
  test, with the one measured number (1407 s for one script), is: standing cost
  of a gate change > 0, defect cost = one re-run, P below the class threshold.
- BASH_ENV (4 PRs) is the landed countermeasure's, unchanged.

## 3. Carry 4: the `R10-FLOW-ANDON` cost test against `R10-RCA-ORCH-CONTINUITY.md`

`R10-RCA-ORCH-CONTINUITY.md` (state (a): liveness is not readable from origin)
records no cost test against R10-FLOW-ANDON (`git grep -i andon -- dev/audit/rca/`
is empty). The study's countermeasure was **built after the record**:
`dev/programme/delivery/2582.md` (#2582, merged `fea3d3c`) added
`tick_loop.sh`'s per-pass `heartbeat.sh --once`, which pushes
`heartbeat/orchestrator` to a commit whose message is the pass line
(`TICK-PASS <time> relay=<rc> tick=<rc> code=<code> behind=<n>`), bounded by
`timeout 60`, failure printed and never fatal (`tools/audit/seat/tick_loop.sh`
line 174). The off-host watcher that alerts when the ref is older than 20
minutes is "an owner-scheduled cloud task", outside the tree.

Cost test, in the unit of the record it answers (wall-clock per day), with
the record's own measured figures quoted and labelled:

- Defect: **3.0 h/day** idle (4 incidents in 6.33 days, mean idle 3.9 h;
  `R10-RCA-ORCH-CONTINUITY.md`).
- That record's cost for the off-host hourly check is **3.3 min/day**. A
  20-minute bound is three checks an hour; scaled linearly it is **9.9 min/day**
  (arithmetic on a quoted figure, not a measurement).
- Standing cost of the heartbeat push itself: bounded by 60 s per tick pass;
  the pass frequency is not stated in the tree, so a per-day figure is not
  computed. The bound makes a failed push cost at most that, once per pass.

`9.9 min/day < 180 min/day x P` holds for any `P > 0.055` (about one day in
eighteen with a stop); the measured rate was 4 in 6.33 days. The decision:
**the countermeasure was right to build and stays**; nothing is rebuilt.

A reading of the live ref, since a record about continuity should read it:
`heartbeat/orchestrator` on origin had a committer date of 2026-11-06
11:25 UTC when read at 12:03 UTC, **38 minutes** old and past the 20-minute
bound. Whether that is a stop or a quiet period, and whether the off-host
watcher exists and alerted, is not established here (the watcher is outside
the tree); it is stated so the owner can look.

## 4. The landed countermeasures (Carry 2) and their demonstrations

Approved by tvofi on 2026-10-29 ("All of these are approved.", quoted in the
brief). Re-measured at this base with `node tools/policy/policy_lint.mjs
--stats --since v7.0.4`, before the change and after; the record
`R10-RCA-FRICTION-RESIDUE.md`'s figures are snapshots.

**(1) #2436, a derived `other (untaught)` family** in `policy_lint.mjs`'s
`statsFamilies`: every verdict-histogram key `VERDICT_CLASSES` does not teach,
other than the passing verdict, members computed at read time, the #2410
subtraction applied. After: `other (untaught) (family)` **65 PRs / 78 entries**
(of a union of 121; nine untaught words that file their own, `ci-red`,
`body-stale`, `defect`, `claim-refuted`, `regression`, `mutation-survivor`,
`figure-wrong`, `merge-conflict` and `claim-false`, are subtracted), over
threshold, would open once. Against the earlier record's 46 PRs at a 218-PR
window this is the same shape at a window 2.4 times longer. Control, by diff
of the two runs' non-family rows: **every taught and every id row prints
byte-identically** (`diff` empty), and the literal `other` row still reads
2 PRs / 3 entries.

**(2) #2437, a declared `root-cause` family** over
`root-cause-unanswered`, `-detectable`, `-unrecorded`. After: union 21 PRs;
all three members file their own line (5, 12, 5), so the #2410 subtraction
takes all 21 and the family row reads **0 PRs / 0 entries (of 21)** and does
not fire. The earlier record's prediction (union 6, family 3) was for a window
in which only one member filed; at this base every member does. That is the
family working as designed, and it is recorded plainly: **in this window it
adds no filing**, and it is the case the map exists for the day a window splits
the obligation across words at 1 and 2 each.

**(3) #2429, `ci-autofix.md`**: the wait is bounded (until `mutation-pins`
concludes the body says `unmeasured`), and a body says `pinned` only when
`--pin-killed` ran on this head. The file's cap
(`dev/governance/config/policy_budgets.json`) had 3 tokens of headroom. The
rule keeps "(kept until M-3)" (`ci.yml`, `tests.yml`, `merge-main.yml` and
`HANDOVER.md` still say "until M-3") and "the reviewer re-checks it". The two
new sentences were shortened, and the cap was still exceeded, so the paragraph
about `linecache` artefacts in the failed-recording bullet is deleted: a policy
change the 2026-10-29 approval does not cover, named under `## Approval` in the
body. Its action half ("fix it first") stays in the bullet above; the warning
that an UNDER-SCOPED beside a failed recording may be an artefact is gone.
`.claude/rules/` and `.cursor/rules/` are regenerated by
`node tools/policy/rules_sync.mjs`.

**Fixture pins and mutation proof.** `policy_lint.mjs` acceptance gains three
pins. (i) The fold: three untaught words on one PR each fire the derived family
at 3; a taught word and the passing verdict are out; a word that files alone is
subtracted; with no derived list there is no row; the three root-cause words
fold to 3. (ii) The wiring: `statsFindings` driven over synthetic merged PRs
yields exactly one `verdict family` would-open for `other (untaught)` for three
untaught words, exactly one for `mutation` for `mutation-unpinned`,
`unpinned-site` and `mutation-survivors`, and none for a taught-only window.
(iii) `cmdStats` builds its table from the shared `derivedInput`. Mutants, each
run with `node tools/policy/policy_lint.mjs` and restored byte for byte, the
unmutated tree as the null control (rc 0): `statsFindings` passing `null`
(killed), `cmdStats` passing no derived list (killed), `mutation-unpinned`
dropped from the family (killed), all three spellings dropped (killed),
`unpinned-site` and `mutation-survivors` dropped (killed), passing-verdict
exclusion removed and `root-cause-unrecorded` removed (killed by (i)).

## 4b. #3156 (`ci-red`): not disposed by this group

The group's `issues` lists #3156, which asks for a record of the `ci-red`
friction key. This group lands no record for it: `ci-red` appears here only as
an example word. It is not a countermeasure of the four records above, and a
`ci-red` record needs its own measurement of the key's PRs. Disposition:
re-route #3156 to its own group; the delivery must not close it from this PR.

## 5. Not established here

- The 12th gate-scoping PR (section 2).
- Whether the off-host heartbeat watcher exists (section 3).
- For each existing record, which re-measured entries fall after its
  countermeasure landed (section 1).
