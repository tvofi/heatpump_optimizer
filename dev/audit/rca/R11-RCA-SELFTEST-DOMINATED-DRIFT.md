# R11-RCA-SELFTEST-DOMINATED-DRIFT: data landings redden main's self-test drift step through reads no selection uses

Root-cause seat beside #3806 (R11-HOTFIX re-take of `tools/ci/selftest_closures.json`), run
beside it and never inside it: this branch does not touch #3806's table. Measured at `origin/main`
`053c33bcc6` (#3810) on 2026-11-20T23:45Z. It extends `R11-RCA-SELFTEST-TABLE-DRIFT.md` and
`R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`; those records' cause (the table is measured only on a
push to main, and the repair is a seat's) still holds and is not restated.

Enumerators, with `A=repos/tvofi/heatpump_optimizer`, from the seat's scratch directory:

- E1, main's push runs and the drift step's conclusion:
  `gh api "$A/actions/workflows/ci.yml/runs?branch=main&event=push&per_page=100&created=>=2026-11-16T00:00:00Z" --paginate`,
  then per run `gh api "$A/actions/runs/<id>/jobs?filter=latest&per_page=100" --paginate`, job
  `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses".
- E2, each failed drift step's refusal lines: `gh api --allow-escape-sequences $A/actions/jobs/<job>/logs | grep -aE 'Z   (UNDER-SCOPED|UNRECORDED|UNMEASURED|STALE|EXTRA|UNGATED|UNREADABLE) '`.
- E3, each refusal tagged `owed` or `dominated` against the committed table at that run's commit:
  `dev/audit/harnesses/r11_selftest_dominated_drift.py`'s rule (`dominated_kinds`), applied to E2's lines.
- E4, tracked directories each first-parent merge adds: the directory set of `git ls-tree -r --name-only M`
  less that of `M^1`.

## 1. The defect, reproduced

Main run 44798542157 at `18a60ea5f6` (#3809), job 136504897866: the drift step prints
`127 gated step(s), 4 refusal(s)`: `prepr` and `dependency-graph-census` miss 198 `dirs` each, all
under `dev/audit/rounds/round11/`; `policy-lint-mutants` misses 198 `probes`, one
`.gitattributes` per such directory; `roster-library` misses the directory
`dev/governance/dimensions`. Job 136092952034 at `698eeeb2ab` prints the same four. Replayed off
Linux with `selftest_scope.drift` over that run's `selftest-closures` artifact and the table at
`6d7d52709f`: 4 refusals (`r11_selftest_dominated_drift.py 6d7d52709f <artifact>`: 4 refusals, 1
owed, 3 dominated).

**Which side moved.** No step started reading something new for three of the four. By E4,
#3723 (`8fa10e00ce`, the round-11 register) added 196 tracked directories under
`dev/audit/rounds/`, #3809 2 and #3810 34. The three steps walk the tree: `prepr` and
`dependency-graph-census` list 694 of the 926 tracked directories at `053c33bcc6`, and
`policy-lint-mutants` holds 502 `.gitattributes` probes (counted from the table: `dirs` per
step, and `probes` ending `.gitattributes`). Each new directory is a new read of
the same walk. `roster-library` is the one step that read something new: `dev/governance/dimensions`
after #3739.

## 2. Named cause

`selftest_scope.select` consults an entry's lists only where its flags do not already decide:
an entry with `objects` is selected on every change, and an entry with `index` on every added or
deleted path, which is the only case `probes` and `dirs` are read for. All three walkers carry
`objects`; `prepr` and `policy-lint-mutants` carry `index` too. So a `dirs` or `probes` miss on
them changes no pull request's selection. The drift step refused it anyway: `drift` compared every
list for every entry (`selftest_scope.py:659-668` at `053c33bcc6`: `misses = {` then `refuse +=` for
any non-empty value). The check's refusal and the table's purpose came apart: the table is a
selection instrument, and these refusals guard no selection.

A refusal no selection needs is cheap while directories arrive rarely. Each one now costs a seat
re-take of main's `selftest-absorbed` table that the next landing invalidates.

## 3. Process state: (d)

The process is the drift step plus `absorb` and a seat's commit of its artifact (#3708, owner
ruling 2026-11-18, option (b)). It was followed: #3806 re-took the table four times (its own body:
runs 44451107719, 44677469341 and 44798542157, then `absorb` over `6d7d52709f`), and #3810 owes a
fifth. It was sound under a precondition that changed: that a new directory under a walked root is
rare.

Measured by E4:

| window | first-parent merges | tracked directories added | under `dev/audit/rounds/` |
|---|---|---|---|
| #3315 (`ba6fd7e8b0`) to `921214bf42` (the last before 2026-11-16T00:00Z) | 275 | 17 | 3 |
| 2026-11-16 to `053c33bcc6` | 120 | 247 | 235 |

Per merge, directories under `dev/audit/rounds/` arrive about 180 times as often (235/120 against
3/275). Round 11 lands audit data in the tree (#3723, #3809, #3810); round 10's checks never saw
that rate.

By E1 to E3, over the 116 push runs from 2026-11-16 whose drift step concluded: 111 failed, 4
succeeded and 1 was cancelled. All 4 successes were on 2026-11-18, between 18:57Z and 19:20Z,
after #3718. Of the 1798 refusal lines
in the 111 failures, 733 were dominated and 1065 owed (913 file misses, 45 dirs, 32 probes, 75
`UNMEASURED`). Before 2026-11-18T20:58Z every failed run had owed refusals: the round-10 cause
(tools adding reads), which `absorb` now answers. From `5bc69f9b94` (2026-11-18T20:58Z) to
`e83a2c919f` (2026-11-19T13:46Z), all 21 failed runs refused dominated misses only. From
`e893cd3d1e` (#3739, 2026-11-19T16:35Z) on, every run refuses one owed line (`roster-library`) and
three dominated ones.

Not (a): a check and a repair route exist. Not (b): both ran. Not (c): the check produced the
intended result for as long as directory additions were rare: 3 under `dev/audit/rounds/` in 275
merges. The countermeasure follows (d)'s form: the step now checks, per entry, whether a miss can
change a selection.

## 4. Class reach

- The same cause on other entries. 22 of the 127 entries carry `objects` and 10 carry `index`
  alone. The other walkers with many lists all carry `objects`: `self-tests-outside-seat` (155
  dirs), `verdict-bus` (50), `merge-train` (48), `beatd` (2305 probes), `temp-or-machine-path`
  (201 probes). Undominated listers with many dirs are `beat-job-rows` (47), `selftest-wiring`
  (47) and `regret-oracle` (13). None lists a directory under `dev/audit/rounds/`, so no data
  landing reaches them. A new directory where they walk is a real selection gap and stays refused.
- Steps with no flag that read round data: `merge-fast-path` (5 reads under `dev/audit/rounds/`)
  and `review-strength-enumerator` (1). These are why candidate C below is refused.
- The same shape elsewhere: a check that refuses an under-approximation its consumer cannot
  observe. `tests/closure.py check` refuses an UNDER-SCOPED closure by read paths. Closures carry
  no "selects every diff" flag, so they have no dominated reads. None found.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**cost(defect)**, per data landing that adds a directory under a walked root:
- main's drift step red until a re-take merges. Measured: red continuously from 2026-11-18T20:58Z
  to the measurement, 50.8 h. Of that, 19.6 h (to #3739) had only dominated refusals. #3806 has
  been open 42.4 h (created 2026-11-19T05:23Z).
- one seat re-take per landing, each with a fixer, a reviewer and a FULL `instrument-self-tests`
  run (the table is a gate file). #3806 did four takes, three of them forced by dominated
  refusals only: the first after #3723, then after #3809 and #3810. #3739's was owed.
- artifacts arrive late: main's traced push job takes 38 to 72 min (`R11-RCA-SELFTEST-TABLE-DRIFT`
  section 5), and the next merge cancels it. 30 of the 119 completed push runs since 2026-11-16
  concluded `cancelled` (E1), among them `689f33e265` and `9e7abae6bb`.

**P(recurrence)**: 5 of the 120 merges since 2026-11-16 added a directory under
`dev/audit/rounds/` (#3669, #3665, #3723, #3809, #3810). Three were in the 27 merges since
2026-11-19. Each one reddens main with certainty while a whole-tree walker is dominated by a
flag. The rest of round 11 lands more finder data.

| candidate | standing cost | landings it clears | verdict |
|---|---|---|---|
| **D. drift rules out dominated misses** (built here) | one set lookup per step in `drift`; 4 self-test checks (under 1 s); 4 mutants, +4 of the lane's runs | every one: the #3810 replay below goes 3 refusals to 0 | **passes** |
| A. landing PRs carry their own entries, as a prepr step | every landing edits a gate file, so FULL `instrument-self-tests` on each (19 to 24 min untraced, `R11-RCA-SELFTEST-TABLE-DRIFT` section 5); concurrent landings conflict in one sorted 398 KB file; Darwin has no strace (`precheck` rc 3) | all, at that cost | fails |
| B. dirs and probes collapse to a bounded `D/**` | changes the table format, `select`, `drift`, `absorb` and `write_table`. It is lossless only where every tracked directory under D was listed at record time: `prepr` lists 694 of 926. Per-directory `.gitattributes` probes have no form `covers` reads. | some, partial | not taken: D does the same for these steps with less surface. Kept as the option for an undominated walker, of which none reads round data. |
| C. drift treats adds under `dev/audit/rounds/**` as inert | zero | all | **refused as a weakened check**: `merge-fast-path` and `review-strength-enumerator` read round data with no flag, so their real misses would pass |
| E. `closures-autofix` (a bot) re-takes the table on main | one bot commit and one FULL push run per landing. The artifact is still late when the next merge cancels the push run. It reverses the owner's 2026-11-18 ruling (no write-token route commits the table). | all, one push late | not taken: it repairs refusals that D removes. An owed drift keeps the seat route. |

D's standing cost on a green push is zero. It adds no seat, no bot commit and no runner minute.
Its induced work is this pull request's review and one FULL CI run, once. It passes at the first
landing.

## 6. Countermeasure: D, built on this branch

`selftest_scope.dominated(entry)` returns the lists `select` never reads for the entry. `drift`
prints a miss in one of them as a `dominated step` note, never as a refusal. The docstring's
DRIFT CHECK paragraph states the rule. Rung: **delete**. It removes refusals that guard nothing.
It does not add an exception: an owed miss on the same step (for example a `files` miss under
`index` alone) is still refused, and so is every flag miss (`it read the index, the table says
not`). If a later `prune` drops a flag, the step's list misses are refused again on the next
push, because the rule reads the committed entry.

The state is (d), and the countermeasure fits it: the check decides per entry whether its
precondition holds (the miss can change a selection), rather than assuming it does.

**The detector, shown to detect**:

- On the defect: the unmodified `drift` over run 44798542157's artifact and the table at
  `6d7d52709f`: 4 refusals. The patched `drift` gives 1 refusal (`roster-library: dirs misses
  ['dev/governance/dimensions']`, an owed selection gap) and 3 `dominated` notes. Same counts at
  `053c33bcc6`'s table and over runs 44677469341's and 44807933952's artifacts.
- Passing once fixed: over #3806's head table (`248c33b40a`): 0 refusals.
- #3810, the landing that owes #3806's next re-take, replayed by adding its 34 directories (E4) to
  the walkers' measured `dirs` and their `.gitattributes` to `policy-lint-mutants`' probes, over
  `248c33b40a`'s table: unmodified `drift` 3 refusals, patched 0.
- It still detects (null control against going green by skipping): dropping one file from
  undominated step `alert-lister-mutants`' entry is refused as
  `UNDER-SCOPED step alert-lister-mutants: files misses ['tools/ci/alert_list.py']`.
- Self-test: 156 checks, 0 failed. The new checks cover four cases. Under `index`, a probe and dir
  miss become notes, but a file miss is still refused. Under `objects`, every list miss is a note,
  and the same misses without the flag are refused (3). The rule never narrows a selection: the
  reads it excuses either pick the same steps or, where an added `tools/` path stops being a
  known read, force FULL. The two existing probe and dir checks now grade an entry without
  `index`; under the new rule their old fixture is dominated.
- Mutants in `tools/ci/selftest_scope_mutants.sh` cover four ways to break the rule: no
  dominance; `index` excusing files; `objects` excusing nothing; an unflagged step excusing its
  lists. The lane's result is in the pull request body.

**Residual.** `roster-library`'s dimensions read is owed and still needs one re-take. #3806 carries
it, and no landing invalidates it. Owed drift from tools (the round-10 cause) keeps `absorb` and
the seat route.

**Approval.** `tools/ci/` is code-owned by `@tvofi`. The change narrows what the drift step
refuses, so it merges only on the owner's approving review.

## Reproduction

    W=<checkout of this branch>; E=<dir holding run 44798542157's selftest-closures artifact>
    python3 dev/audit/harnesses/r11_selftest_dominated_drift.py --self-test
    python3 dev/audit/harnesses/r11_selftest_dominated_drift.py 6d7d52709f $E/selftest_closures.json
    # 4 refusal(s), 1 owed, 3 dominated
    python3 -I tools/ci/selftest_scope.py --self-test     # 156 checks, 0 failed
    sh tools/ci/selftest_scope_mutants.sh --self-test     # every mutant refused
