# R10-RCA-FRICTION-REGRESSION: one verdict word, three mechanisms, one lane no local path runs (#2860)

The root-cause record for the recurring-friction key `regression` (#2860). The
governance cron filed it at 3 distinct pull requests / 3 entries in
`v7.0.4..origin/main`, at threshold 3. This record ran apart from any fix,
under the root-cause role contract. It lands one sentence in `fixer.md` step 5
and no production code.

**Merge base and window.** Every figure was taken on 2026-10-30 at merge base
`507a9ec264eb373b132248d752259254d8a9fa4d`, which was also `origin/main` at
measurement. Tag `v7.0.4` is the window's start.

## 1. The count, re-derived

`node tools/policy/policy_lint.mjs --stats --since v7.0.4` ran with rc=0
(`regression/stats_v7.0.4.txt`). It prints
`STATS: 319 merged pull request(s) in v7.0.4..origin/main` and the row
`3 / 3     regression   <- at or over threshold`. That matches #2860's 3 / 3.
The run printed no `would open` line for this row. The 218-PR snapshot
`harness-friction/stats_v7.0.4.txt`, taken earlier in the same window, printed
one. Why the line is absent here is not established, and nothing below depends
on it.

`--stats` does not list a key's PRs. The three were found by an independent
rescan: the issue comments of all 319 window PRs
(`gh api repos/tvofi/heatpump_optimizer/issues/<pr>/comments --paginate`),
keeping each comment whose first line starts `Fix review:` and carries the word
`regression`. That gave 3 PRs, the histogram's count.

| PR | what | blocked head | min to next verdict |
|---|---|---|---|
| #2698 | fix, R10-RATIO-ANCHOR | `3383fb2a` | 728 |
| #2825 | fix, R10-UPDATE-PR-SIGNALS | `ab80907a` | 96 |
| #2841 | fix, R10-CARD-VOICE | `2cfb8b96` | 153 |

"Minutes to next verdict" runs from the blocked comment's `created_at` to the
same PR's next `Fix review:` comment, all posted by `hpo-approver[bot]`. It
counts fixer, CI, reviewer and idle time together, so it is an upper bound on
what a block costs. Sum 977 min, median 153 min, which is the median
`R10-RCA-FRICTION-RESIDUE.md` section 2 lists for this key.

`regression` is a word no list teaches. `VERDICT_CLASSES`
(`.claude/workflows/web-fix-wave.js:175`) holds `product-tradeoff-regression`
but not `regression`. The key reached the threshold under its own spelling.

**Controls in other windows.** `harness-friction/stats_v7.0.0.txt` shows
`regression` at 1 / 1. `claim-false/stats_v7.0.5.txt` shows no `regression`
row: 0 in the newest window, out of 59 merged PRs. All three entries in this
window fall within 2026-10-24 to 2026-10-26.

## 2. The three blocks, mechanism by mechanism

The verdict word names an outcome: the head is worse than its comparison end
on some measure. It does not name a mechanism. The three blocks have three
mechanisms (`regression/items.tsv`, one row each).

**M, #2698: the fix's own rule left open on its mirror branch.** The body at
the blocked review (`handoff-body/r10-ratio-anchor` at `51735b96f`, the last
body pushed before the 13:32Z verdict) claims "**Clamp means reset,
consistently**". It describes the defect commit `b49602160` repaired: a ratio
whose re-anchor leaves its bounds reset, while "the scale beside it ... kept
the value solved jointly with the inexpressible ratio". Its step-3 "both ends"
arm names only the ratio's clamp. The mirror was open at the head:
`git show 3383fb2ac:custom_components/heatpump_optimizer/coordinator.py`. In
`_reanchor_house_heat_loss_scale`, the branch
`if not HOUSE_HEAT_LOSS_SCALE_MIN <= new_scale <= HOUSE_HEAT_LOSS_SCALE_MAX:`
resets `new_scale` and the house samples, and the function then still runs
`self._apply_lower_floor_loss_ratio(new_ratio)` with the ratio solved beside
the inexpressible scale. The review measured the lower zone at 128.3 / 201.2
W/K at the head, against 100.8 / 172.8 at the base. That figure is the
reviewer's and was not re-run here. The repair `1f6f69244` moved the scale
reset into `reanchor_heat_loss`.

**N, #2825: a revision's new mechanism, whose arm drove the neighbouring
input.** Round 1 (`ecf96c46`) was blocked `carry-missing` on the self-test's
timeout half. Round 2's `0ca3e5b71` ("the self-test bound ...") put the
self-test in its own session (`os.setsid()`) and forked a watchdog. At
`ab80907a`, `tools/audit/seat/pr_args.sh` has `dog = os.fork()` (line 249) and
nothing moves the watchdog into a new group or session. The revision's own arm,
"a SIGKILLed supervisor's self-test is ended all the same, by its watchdog"
(line 1123), kills the supervisor by pid. A SIGKILL to the caller's whole group
kills supervisor and watchdog together, and the self-test runs on unbounded:
the reviewer saw 11 live processes 3 s after the kill, and 0 survivors at round
1's head. The final head `3e936f0c` carries the missing arm, "a SIGKILL to its
caller's whole group still ends the self-test, 0 survivors in either session"
(`pr_args.sh:1178`).

**L, #2841: a CI lane that no local path runs.** `tests / browser` (check run
121335806091) concluded `failure` at `2cfb8b96`, started 00:24:05Z and
completed 00:28:19Z. The PR was opened 23:57:28Z, which is past the handoff,
since `handoff_push.sh` opens it. The body at the blocked review
(`handoff-body/r10-card-voice` at `b369299b1`, 22:38Z) records the scoped gate
as `MODE: SCOPED -- 24 script(s) run, 9 scoped out`, 23 of 24 green, and its
`## Red checks` names only `tests/entities.py`. Re-run here at `2cfb8b96`,
`python3 tests/closure.py select --diff 5261ba84` prints that same mode line.
Its `scope.run` holds 24 scripts, and `card_browser.mjs` is not one of them.
It cannot be. `tests/closure.py:116-118` excludes it ("It runs in its own
job"). `tests/run.sh:446-448` skips it. `.github/workflows/tests.yml:472-487`
runs the `browser` job on every PR, gated by `closure-scope`'s `lane_skip`
decision, never by `GATE_SCOPE`. Reproduction: section 7.

## 3. Named cause and process state

**For the key: no single cause.** Three blocks with three mechanisms, at most
one per mechanism in any measured window, do not make a recurring cause. The
word recurred, not a mechanism. Each block gets its own state below.

**L (#2841): state (c).** `fixer.md` step 5 at the base says: "Run what
`scope.run` and `tests/run.sh`'s `run_always` lines name ... leaving the rest
to CI". The seat did exactly that: 24 of 24 run, its result in the body. For
every other lane, "the rest" is a lane the scope chose not to run, and CI
running it after the handoff is the gate's bargain (`CLAUDE.md` rule 1). For
`card_browser.mjs` there is no choice to make. `NOT_A_TEST` puts it outside
every scope, so a step-5 seat never runs it on any diff, card diffs included.
Its first run is CI's, after the PR exists, so a red there is always a review
round. A local detector existed: `.claude/workflows/web-fragments.md:68-70`
carries the recipe, and the cloud image ships Chromium and Playwright. No
contract said when to use it, and `tests/README.md` "Note on browser checks"
describes the CI job as "what actually verifies" a geometry change. The
process was followed and did not produce the intended result. That is (c), not
(b): a firmer "run the tests" would repeat an instruction the seat obeyed.

**M (#2698): state (b), inside a standing refusal.** `fixer.md` step 3 counts
"an 'every' ... is a measurement, owed the command that produced it and the
result that would have appeared had it been false". "Consistently" is an
"every" over the pair's two clamp branches, and only one branch was measured.
Since 2026-10-06 (`bc0f17ddb`), the same step has asked for "one on the clamp"
for a learner or guard change. The seam is semantic: the mirror branch of a
rule the fix introduced. #2239's enumerator, which the body names as the
step-8 instrument, keys `thermal_learning` stems that lack an `*_anchor`
sibling. It does not key clamp branches, so no instrument in the tree returns
the mirror. That makes this the `class-open` residue under another word. Its
standing refusal is `R10-RCA-FRICTION-RESIDUE.md` section 6 (#2784).

**N (#2825): no process failure.** The revision answered a `carry-missing`
block by adding a mechanism, and wrote an arm for it. The arm drove a pid
kill. The failing input was a group kill, a neighbouring input that no
instruction names and that only an adversary looks for. The fix review is the
designed detector for exactly that, and it caught the problem in one round of
96 min. This is the "does not qualify" shape in `defect-root-cause.md`: the
cheapest detector that would have caught it is the gate that did.

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in seat
minutes per window.

**Countermeasure 1, landed: one sentence in `fixer.md` step 5** (L, state
(c)). "**No scope selects `card_browser.mjs`**, which CI runs past the
handoff: run it on a `GRID_SURFACE` diff (recipe: `web-fragments.md`;
#2841)." `GRID_SURFACE` is the lane's own list (`tests/card_browser.mjs:1063`:
the card's `www/`, `card_browser.mjs`, `card_rig.mjs`). The sentence names
that list, so no second copy can drift from it.

- Standing cost: one local run per card-surface diff. Measured in section 7 at
  268 s at the blocked head, including `tests/plan_view.py`. In this
  window, 7 merged PRs touched the card
  (`git log --first-parent --format=%h v7.0.4..507a9ec26 --
  custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | wc -l`
  → 7 of 332 first-parent commits). At one run per PR, that is about
  31 min per window (7 x 268 s). Reruns after a revision double it at most.
  It adds no tokens to any load: `fixer.md` stays at its 5216 / 5216-token
  cap (`policy_lint.mjs --budgets`, the row `tools/audit/briefs/fixer.md`).
  The sentence was paid inside step 5 and by dropping step 13's copy of
  `ha_contract.py`'s fidelity vocabulary, with no cap raised.
- Benefit: in this window it reaches 1 of the 3 entries, one round, 153 min
  upper bound. `P(recurrence)`: among the window's fix-review blocks that
  quote `tests / browser`, #2841's is the only one that blocks on it. The other
  five (#2689, #2697, #2798, #2818, #2883) block on a class their first line
  names, and quote the lane in their check lists (the rescan of section 1).
  So 1 red-lane block in 7 card PRs.
- Verdict: built, because 31 min (63 with every PR run twice) < 153 min. The basis is one
  instance in one window, and this record says so. The countermeasure is an
  instruction, not a check, so no red/green demonstration of a detector is
  owed. Section 7 shows that the run it instructs is red at the blocked head
  and green at the base.

**Refused: teaching the closure selector a browser line** (L). `closure.py
select` could print a `BROWSER:` line for a `GRID_SURFACE` diff. That needs a
Python copy of a JavaScript list, which is a concept duplicated (`fixer.md`
step 17). It also turns the gate file `tests/closure.py` into a `MODE: FULL`
diff, with an arm and a mutant to land. It reaches the same one instance as
the sentence, at a larger standing and once-off cost. Refused.

**Refused: a CI precondition that holds the review until `tests / browser`
concludes** (L). The reviewer already reads the checks: #2841's block came 33
min after the lane went red. The round is spent either way, because the red
arrives after the handoff. Only a run before the handoff saves it, so this
refusal leaves Countermeasure 1 as the only form that pays.

**M: no new countermeasure.** It is the `class-open` residue under its
existing refusal. Its 728 min is mostly idle overnight time: the repair commit
`1f6f69244` landed at 13:43:50Z, 12 min after the block.

**N: none.** The cheapest detector is the gate that caught it.

**Teaching `regression` as a verdict class: not done here.** The derived
`other (untaught)` family drafted in `R10-RCA-FRICTION-RESIDUE.md` section 4
is the general answer for untaught words. This record adds nothing to it.

## 5. How far the class reaches

For L, the search was every lane CI runs that no local scope can select. The
lists are `NOT_A_TEST` (`tests/closure.py`) and the unwired-test list in
`tests/run.sh`. `tests/README.md:442-445` names the two real tests on them,
`card_browser.mjs` and `nightly_ha.py`. `nightly_ha.py` also has no local path,
because it needs Docker. On a pull request it runs in the unrequired
`nightly-ha` job (`tests.yml:1270-1276`), and only when the diff touches its
inputs. The window holds one fix-review block that quotes it, filed under
`root-cause-unrecorded`, not under this key. The sentence landed here covers
`card_browser.mjs` only. A seat's Docker access is not established, so
extending the sentence to `nightly_ha.py` is left to that key's record.

For M and N, the search was the window's other fix-review blocks. M's shape is
the `class-open` key, 6 PRs in `R10-RCA-FRICTION-RESIDUE.md` section 2. N's
shape (a revision's arm driving a neighbouring input) has no key of its own,
and no other instance was looked for or found. That is stated rather than
counted.

## 6. Not established here

- The reviewer's #2698 figures (128.3 / 201.2 W/K) and #2825 figures (11 live
  processes) were not re-run. Both mechanisms were re-derived from the code at
  the blocked head (section 2).
- Why the 319-PR `--stats` run printed no `would open` line for a row at
  threshold.
- Whether `regression` recurs in `v7.0.5..`: 0 at this base, after 59 merges.

## 7. Reproduction: the lane at both ends, and at the repair

Each run was a detached worktree at the SHA:
`PYTHONPATH=tests/hastub python3 tests/plan_view.py`, then
`NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs`.
That is `web-fragments.md`'s recipe, with `HPO_BROWSER_SCOPE` unset, so each
run printed `P9 grid MODE: FULL (HPO_BROWSER_SCOPE=full)`. Wall clock covers
both commands.

| end | SHA | rc | FAIL lines | summary | s |
|---|---|---|---|---|---|
| blocked head | `2cfb8b96` | 1 | 2 | `2 BROWSER CHECK(S) FAILED` | 268 |
| merge base | `5261ba84` | 0 | 0 | `ALL BROWSER CHECKS PASSED` | 249 |
| repair | `59c744f4c` | 0 | 0 | `ALL BROWSER CHECKS PASSED` | 272 |

The head's two failures are the two the review named:
`P9 grid: every cell mounted and every driver step found its target` and
`P9 grid: no pop-up leaves the viewport or its chart`. The run that the new
step-5 sentence instructs is red on the defect and green at both of the
defect's other ends. It was available locally, before the handoff, in about
4.5 min.
