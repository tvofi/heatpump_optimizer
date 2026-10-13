# R9-RC-POSTREVIEW-MERGE: a post-review main merge reddens the head, and no local instrument sees it

Root-cause seat for roster group **R9-RC-POSTREVIEW-MERGE** (issue #2096), beside
the fixes, never inside one (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`). No production, workflow or policy
file is changed here; the countermeasure is proposed, not landed, and its
propagation is named in section 7.

**Trigger.** The red-check trigger: each instance turned a pull request red on a
check a cheaper detector could have run. For instance (1) the cheaper detector
is `tools/pr/prepr.sh --self-test`'s own class arm, which CI ran 100 s after the
push and a local run refuses in 122 s — and a single arm of it in **0.055 s**
(measured below).

**Class.** Process, not a production seam. The three instances the brief lists
are one shape: *the head's green, clean or reviewed status was established
against a main (or a handoff ref) that had moved by the time the merge was
published, and the merge with the live main is graded first by CI, minutes
later, after the review and inside the batch pass.* Nearest existing class:
**I3** ("a required governance/CI check is skipped, runs a stale ref, or has a
bypassable boundary") — the difference is recorded in `bugclasses.json`
(`nearest_existing`): no check was skipped improperly and none ran a stale ref;
the recarry's designed fast-path publishes a merge that no local instrument
grades, so the first grade the merged tree ever receives is CI's.

Enumerators for every figure sit in `## Figures`. Scratch copies of the API
payloads and the extracted scripts: `/Users/timmalmstrom/hpo-seats/r9rca-postreview/`.

## 1. Cause (reproduced)

### Instance (1): #2072 — a detector main shipped met an instance the reviewed head added

Measured, reproduced end to end.

| tree | `pipe_grep_q_sites` over the six drained scripts | seconds |
|---|---|---|
| merge base `bd59a4af1` (#2064, 2026-10-09 00:56 CEST) | rc 1, 4 sites (`stamp_paths` x2, `body_line`, `copies_line`) | 0.050 |
| reviewed head `316a36414` (#2072's own, judged) | rc 1, **10 sites** — and no detector existed in this tree | 0.056 |
| main `23d354970` (parent 2 of the recarry) | **rc 0** (null control) | 0.057 |
| recarry head `04d10721b` (the red) | **rc 1, exactly 1 site** | 0.055 |
| fixed head `00e31e8a3` (2026-10-10 07:29Z) | rc 0 | 0.040 |
| live `origin/main` at this writing | rc 0 | 0.037 |

The one surviving site at the merged head is the branch's own new arm:

```
tools/pr/prepr.sh:1398:  printf '%s\n' "$flow" | grep -q 'moved_line "'
```

The three-way merge did exactly what a text merge does. The merge base carried
two `printf | grep -q` arms (`body_line`, `copies_line`); the branch added a
third (`moved_line`) and kept the two; main, in `09d2061b2` (PR #2067, merge
`d0f085ffb`, "drain every early-exit grep under pipefail in the gating
scripts"), converted the two inherited arms to `case` form **and shipped the
detector `pipe_grep_q_sites` whose `PIPE_GREP_Q_FILES` names
`tools/pr/prepr.sh`**. So the merge took main's conversions (branch side
unchanged there) and the branch's new line (main side unchanged there) — clean
as text, and the merged tree holds exactly one site of a class main had just
outlawed, in the one file main's new detector scans.

CI confirms the local reproduction is the real red: at `316a36414`
`instrument-self-tests` and `pr-contract` were `success` (11:24:14–11:26:19Z and
11:24:13–11:24:40Z, check-runs API); at `04d10721b` both `failure`
(21:46:11–21:47:51Z and 21:49:08Z), the job log reading

```
FAIL no early-exit grep reads a pipe under pipefail in the drained scripts (got 1, wanted 0)
     | tools/pr/prepr.sh:1398:  printf '%s\n' "$flow" | grep -q 'moved_line "'
243 passed, 1 failed
```

and `bash tools/pr/prepr.sh --self-test` run at `04d10721b` in this seat's
scratch worktree reproduces it byte for byte: rc 2, 122 s, `243 passed, 1
failed`, the same FAIL row. The branch's own arm above it
(`the layout step calls moved_line`) passes — nothing is wrong with the arm's
logic; the red is the class detector meeting the class.

**The named cause.** *The independence premise of the recarry skip.* The head's
delta and main's delta are assumed not to interact; they did, because a main
that ships a detector over a file the reviewed head also edited — or a budget
raise, or a ratchet move, or an arch-score change — reddens the merged head,
and the merge is graded first by CI, after the review, inside the batch pass.

### Instance (2): #2066 — `merge-tree` clean at the measured main, conflicting at the published one

Reproduced with `git merge-tree --write-tree` (rc 1 = conflicts; the count is
`--name-only` lines after the tree line):

| head (#2066, `fix/cop-duty-floor`) | vs `d0f085ffb` (main after #2067) | vs `23d354970` (main after #2078, 22:13Z) |
|---|---|---|
| `386b7e2ff` (17:24Z, the head the reviewer measured) | **0 conflicts** | **27 conflicting files** |
| `67a832653` (21:17Z, the round-9 head at publish) | 0 conflicts | **30 conflicting files** |

Same cause, textual arm: the "clean" measurement is a function of the main it
was taken against, and nothing between the measurement and the publish re-takes
it against the live main. #2066 is open at this writing, 35 commits, and its
commit `af498a65e` is titled "Merge 67a832653 … into **the round-10 head**":
one instance cost a whole review round. (Against the *current* `origin/main`
its live head `7706b39a1` merges clean again — the conflict was against the
main of that moment, which is the point.)

### Instance (3): #2075 — blocked `head-moved` at round 3

The brief's account: the pull request never carried the handoff head, so round 3
was blocked `head-moved`. Not re-measured here beyond the PR record: #2075
merged 2026-10-10T13:48:21Z after 15 commits. Recorded as the brief states it;
it is the third face of the same cause — a status established against a ref
that moved, discovered by the gate that consumes it.

## 2. The removal point: what #2069's skip skipped

`tools/pr/app_push.sh --recarry` (added by PR #2069, `a9baf164c`, 2026-10-09
21:15Z) skips `prepr` when the verdict holds: two parents, parent 1 the live
pull-request head, parent 2 on main's first-parent chain, HEAD's tree equal to
`git merge-tree --write-tree` of its parents, body the live body. Its header
states the safety argument:

> The branch's own diff and body passed prepr and review, main's commits passed
> on main, and CI's pr-contract and suite run at the new head before the train
> merges.

Every clause is true and none of them grades the *interaction* of the two
deltas. And the local detector this instance needed was not merely available —
it was in the very script the flag skips, and it runs on the default path:
`prepr.sh` step 3h runs `bash tools/audit/prepr.sh --self-test` whenever
`selftest_owed` finds a changed path among the self-test inputs (`prepr.sh`
itself, every tracked script it names, its fixtures). At `04d10721b` the carry's
three-dot diff names `tools/pr/prepr.sh`, so step 3h is owed; measured, the
self-test it would have run refuses in 122 s with exactly CI's FAIL row.
Before #2069, `remerge_main.sh` pushed without the flag and `prepr` ran
(`PREPR_SKIP_CLOSURES=1` skips the closures step only, not 3h). The skip is
therefore the exact removal point, and it removed a detector that was already
wired, in the same file, for precisely this diff shape.

## 3. Process state: **(c)** — followed, and did not produce the intended result

The process is the recarry verdict plus the train's CI step, and it was
followed exactly: the merge was the clean 2-parent merge the verdict describes
(`merge-tree` agrees), the body was the live one, the `RECARRY: prepr SKIPPED`
line printed, and the train's step 2 then waited for CI and stopped on the red
— nothing red merged. Its intended result — a merged head that needs no local
grade — was not produced: the head pushed was red on a check whose local arm
costs 0.055 s, and the verdict had no way to know, because its predicate reads
text and identity, never interaction.

Not **(a)**: the cheaper detector existed, locally, in the same instrument
(`prepr.sh` step 3h), and `app_push.sh`'s own self-test pins that the unflagged
path calls it; what removed it was a change to the predicate, not the absence
of a check. Not **(b)**: nobody disobeyed an instruction — `fixer.md` step 6's
"after any rebase or merge, steps 2–8 are re-executed" binds the fixer's own
merges, and the orchestrator's recarry path was redesigned, deliberately, 2 h
30 m before the first instance. Not **(d)**: #2069's premise ("a clean carry
was paying minutes for nothing") was not sound and then broken — it was
incomplete as shipped, because the payment a carry that owes the self-test buys
is exactly this red, and the predicate that says which carries owe it already
existed beside the skip.

Per `root-cause.md`: the countermeasure changes the **unit** — what "clean"
must mean — not the arm count.

## 4. Class reach — the census

Enumerator in `## Figures` (F5): every commit reachable from any fetched ref
whose subject matches `^Merge remote-tracking branch 'origin/main' into `,
2026-10-08..2026-10-10 — **76 recarry-shaped merges** (~25/day). For each, the
check-runs API at the merge and at its parent 1 (the reviewed head):

- 17 of 76 carry a `failure` beyond `nightly-status` (which grades main, not the head).
- **15 of those 17 were green — or red only on main-graded checks — at the
  reviewed parent**: the merge itself reddened them. **19.7 % of recarries,
  ~5/day.** (The other 2, `33dc29876` and `fdbf59f63`, inherit a red already
  present at their parent and are excluded.)

The 15 and the checks main's advance reddened:

| merge | date | checks reddened by the merge | files shared with main's delta | owes `prepr`'s self-test |
|---|---|---|---|---|
| `03f7be4d3` | 10-08 | instrument-self-tests, pr-contract | 4 | yes |
| `0cff5a993` | 10-08 | budget-raise-gate | 0 | no |
| `8e0dcb72c` | 10-08 | budget-raise-gate | 0 | yes |
| `0e12b4f8a` | 10-09 | budget-raise-gate | 4 | yes |
| `f14e77c95` | 10-09 | closures, fast (3.14), instrument-self-tests, pr-contract | 0 | yes |
| `588692957` | 10-09 | briefs, fast (3.14), mutation | 1 | yes |
| `386b7e2ff` | 10-09 | mutation | 1 | yes |
| `c901f8f34` | 10-09 | arch-score, pr-contract, typing | 0 | no |
| `04d10721b` | 10-09 | instrument-self-tests, pr-contract | 3 | yes |
| `ae6fbdd5e` | 10-10 | env-matrix, fast (3.14), instrument-self-tests, policy-docs, pr-contract | 1 | yes |
| `a9b1b48c4` | 10-10 | arch-score, mutation, pr-contract | 5 | yes |
| `dc1abe654` | 10-10 | fast (3.14), pr-contract | 0 | no |
| `574345d95` | 10-10 | mutation, pr-contract | 0 | yes |
| `4f0bde165` | 10-10 | fast (3.14) | 0 | no |
| `78a067541` | 10-10 | budget-raise-gate | 0 | no |

Two honest limits on the census, stated rather than hidden: `fast (3.14)` may
carry runner flakes the parent's green run does not exclude, and "green at the
parent" is the parent's *latest* recorded run, not a run at the parent taken at
the same moment as the merge's. Neither changes any row's classification above,
because in every row at least one reddened check is a deterministic gate
(instrument-self-tests, pr-contract, budget-raise-gate, arch-score, mutation,
closures, briefs, policy-docs).

The reach is wide because the premise is general: any main advance that a local
predicate cannot see — a detector over a shared file, a budget raise, a
ratchet or arch-score move, a mutant set — reddens the merged head, and the
recarry verdict has no predicate for any of them.

## 5. Cost test

Both sides per release cycle, wall-clock, at the measured recarry frequency
(~25/day, F5).

**Defect.** ~5 merge-reddened heads/day. Per occurrence, measured on #2072: red
observed 2026-10-09T21:47:51Z, fix head `00e31e8a3` at 2026-10-10T07:29:47Z
(**9 h 42 m**), merged 12:11:35Z (**14 h 24 m** after the red); the work inside
that is one fixer round (re-run the contract, one commit), one re-review of the
delta, and the batch pass that died — every other entry in the batch re-proved.
#2066's occurrence cost a whole review round (round 10, 35 commits and open).
Taking only the seat-and-review time, conservatively 30 min per occurrence:
**~2.5 h/day**.

**Countermeasure (the recommended one, below):** the recarry runs
`prepr.sh --self-test` on the merged tree only when the carry owes it, measured
at **50 of 76 recarries (66 %)** under `prepr`'s own `selftest_owed`; the run
is **122 s** (measured at the red head). Standing cost: 0.66 × 122 s × 25/day ≈
**34 min/day**, and it eliminates the review-round and batch re-proval, not
just the CI round.

34 min/day < 2.5 h/day. The test passes without the elapsed-overnight figure,
which is why that figure is quoted and not used.

## 6. Countermeasure (proposed, not landed) — the candidates, priced

Root-cause.md's demonstration duty is met by the runs in section 1 and the
table below: the proposed unit **fails on the defect** (`04d10721b`, rc 2, 122 s,
CI's own FAIL row) and **passes once fixed** (`00e31e8a3` rc 0, 0.040 s for the
arm; live main rc 0, 0.037 s). It does not go green by skipping: the skip line
names what ran, as `app_push`'s one `RECARRY:` line already does.

| candidate | cost per recarry | standing (25/day) | measured reach on the 15 | verdict |
|---|---|---|---|---|
| (c) files-shared-with-main probe (`comm -12` of the two three-dot diffs) | 0.088 s mean | ~2 s/day | fires on 43/76 but sees only **7/15** (47 %) | **insufficient as a barrier** — recorded, not proposed |
| class arm alone (`pipe_grep_q_sites`) | 0.037–0.057 s | ~1 s/day | catches instance (1) only | too narrow for the class |
| (a) **recarry runs `prepr.sh --self-test` on the merged tree when `selftest_owed`** (prepr's own predicate, no new list) | 122 s × 66 % ≈ 81 s mean | ~34 min/day | owed by **10/15**, including instance (1); refuses the push before it happens | **proposed** |
| (b) train always re-runs `prepr.sh --self-test` after recarry | 122 s | ~51 min/day | the 4 instrument-self-tests reds wherever they sit | dominated by (a): the 5 reds on carries that owed no self-test (4 × budget-raise-gate, `c901f8f34` arch-score/pr-contract/typing, `dc1abe654`/`4f0bde165` fast) name no check the self-test grades, so the unconditional run buys nothing the owed-gated one does not |
| whole `prepr` (pre-#2069 behaviour) | 221–551 s (the brief's figure; unmeasured here) | 1.5–3.8 h/day | as (a) plus prepr's other steps | rejected: pays the very minutes #2069 removed, for the same reach as (a) on this census |

**(a) is the proposal**, and it is a unit change, not an arm: `recarry_verdict`
gains one condition — a carry skips the local grade only when it owes none,
and "owes" is `prepr.sh`'s own `selftest_owed` over the carry's three-dot diff,
so no second list is maintained and a new gating script added to `prepr`
tomorrow is covered the day it lands. When owed, `remerge_main.sh` runs
`bash tools/pr/prepr.sh --self-test` on the merged tree before `app_push`, and
a refusal stops the train at step 1, where a conflict already stops it. This
keeps #2069's purpose intact — the 33 % of carries that owe nothing pay zero —
and cannot make a broken recarry look green, because the self-test either runs
and its refusal stops the push, or does not run and the RECARRY line says so.

**Sub-shape left open, deliberately, and propagated (section 7):** 4 of the 15
(`0cff5a993`, `8e0dcb72c`, `0e12b4f8a`, `78a067541`) are `budget-raise-gate`
reds where main merged a `*_budgets.json` raise the head never touched. No
local predicate measured here sees them — the raise is in main's delta, not the
head's — so (a) does not cover them. That is the carry-and-approval side's
seam (the carry must absorb main's raises the way `remerge_main.sh` already
drops inherited claims), and it goes to that lane's brief, not into this
document's countermeasure.

The class therefore enters `bugclasses.json` as **open** with this document as
its class RCA on record; the barrier flips to `barriered` only when (a) lands.

## 7. Propagation (diffs the orchestrator would apply; nothing applied here)

1. **To the fixer brief of the countermeasure pull request** (a new group in
   `.claude/workflows/wave-r9-groups.json`, or the standing fix lane). Exact
   sentence to add:

   > `remerge_main.sh`/`app_push.sh --recarry`: a carry skips the local grade
   > only when it owes none — consult `prepr.sh`'s `selftest_owed` over the
   > carry's three-dot diff; when owed, run `bash tools/pr/prepr.sh
   > --self-test` on the merged tree before the push and stop the train on its
   > refusal, with the one RECARRY line naming which ran (R9-RC-POSTREVIEW-MERGE;
   > measured 122 s at 04d10721b, 50 of 76 recarries owe it).

2. **To the carry/approval lane** (the `--carry` group's brief), for the
   budget-raise sub-shape:

   > A recarry whose main merged a `*_budgets.json` raise leaves the head red on
   > `budget-raise-gate` with no local predicate able to see it (4 of 15
   > measured instances, R9-RC-POSTREVIEW-MERGE section 6); the carry must
   > absorb main's raises the way `remerge_main.sh` drops inherited claims.

3. Issue #2096 owes the short **Root cause** section
   (`defect-root-cause.md`): state (c), the census numbers, the proposed
   countermeasure, and `dev/audit/rca/R9-RC-POSTREVIEW-MERGE.md`. The RCA seat
   does not post to GitHub; the orchestrator writes it.

## Figures

Every number above is one of these commands, run 2026-10-10 on this seat's box
(macOS, bash 3.2-compatible invocations); API figures from the check-runs
endpoint as shown.

- **F1 class arm, per tree** — extract `pipe_grep_q_sites` from
  `tools/pr/prepr.sh` at the named SHA (`git show <sha>:tools/pr/prepr.sh`),
  materialise the six `PIPE_GREP_Q_FILES` at that SHA, and run
  `pipe_grep_q_sites session-start.sh stop-selfcheck.sh pre-edit.sh
  approve_held_runs.sh worktree_gc.sh prepr.sh` from that directory (six
  arguments, so grep prefixes filenames and the comment filter applies). Rows:
  the table in section 1. Single-file runs leak comment lines under BSD grep
  (no filename prefix) — always pass all six.
- **F2 whole self-test at the red head** — `git worktree add --detach
  <scratch> 04d10721b`, then `bash tools/pr/prepr.sh --self-test`:
  rc 2, 122 s, `243 passed, 1 failed`, FAIL row as quoted.
- **F3 CI verdicts** — `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?per_page=100`:
  `316a36414` instrument-self-tests/pr-contract success (11:24:14–11:26:19Z /
  11:24:13–11:24:40Z); `04d10721b` both failure (21:46:11–21:47:51Z /
  21:49:08Z); job 11404006359 log via `gh run view 37995415433 --log-failed`.
- **F4 #2066 conflict matrix** — `git merge-tree --write-tree --name-only <head> <main>`,
  rc 1 = conflicts, count = lines after the tree line; the matrix in section 1.
- **F5 census** — heads: `git log --all --since=2026-10-08 --grep="^Merge
  remote-tracking branch 'origin/main' into " --format='%H %ci %s' | sort -k2`
  (76). Reds: the check-runs API per head, failures minus `nightly-status`;
  parent status the same call at `<head>^1`. TSVs:
  `recarry_reds.tsv`, `parent_status.tsv` in the scratch directory.
- **F6 owed / overlap probes** — owed: prepr's `selftest_inputs` (rebuilt by
  the command block at `tools/pr/prepr.sh:969`) intersected with
  `git diff --name-only <merge-base> <head>` per recarry (`owed.tsv`): 50/76.
  Overlap: `comm -12` of the two three-dot diffs (`overlap.tsv`): 43/76 overlap,
  7/15 of the reds; mean probe 0.088 s.
- **F7 #2072 timeline** — `gh pr view 2072 --json createdAt,mergedAt,commits`:
  commits `316a36414` 10-09T10:57Z, `04d10721b` 21:45:55Z, `00e31e8a3`
  10-10T07:29:47Z; merged 10-10T12:11:35Z.
