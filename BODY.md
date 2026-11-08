R10-RCA-COP-UNMEASURED: the root-cause seat for R10-HOTFIX-COP-UNMEASURED (#3297).

- **Trigger:** 1. The defect reached v4.0.0 through v7.1.5.
- **Scope:** this seat ran beside the hotfix fixer. It edits nothing under
  `custom_components/` and does not touch #3297's branch.

The product is `dev/audit/rca/R10-RCA-COP-UNMEASURED.md`, cited from
`dev/audit/config/bugclasses.json` `_rca["R10-RCA-COP-UNMEASURED"]`. Its
reproduction and detector is `dev/audit/harnesses/r10_rca_cop_unmeasured.py`.
The four parts follow.

- **Named cause.** One COP sample per interval serves both a learner (the
  COP scale) and two graders: the last measured COP and the COP health watch.
  The sample carries no provenance.
  - With no heat input, `flow_meter.cop_evidence` infers the COP as the model
    times ask over draw.
  - A vendor-estimated thermal power entity was read as metered heat.
  - Either way, the watch's bands and `machine_score` compared the model with
    itself.
  - By `git log`, the inference came first, named "measured" from
    `df7db8215` (PR #11, v2.8.0). The watch was built onto it in `a63b576cd`
    (PR #50, v4.0.0) and had no metered input until v7.0.5. The watch did not
    degrade: it was born on an inference.
- **Process state: (c).** Three processes read this seam and passed it.
  Each judged whether the sample was clean. None traced where its inputs came
  from.
  - `D1.md` hunts "fabricated data as measured" but has no method step that
    reaches it.
  - The round-10 P5 sweep (`dev/audit/rounds/round10/sweep-P5.md:37`) cleared
    `_cop_health_cusum` as "an empirical per-bucket, per-curve baseline ...
    not a model residual".
  - STUDY R10-IDENT Q2 (#2262) found "COP is not observable without a heat
    meter". The R10-COP-GATE group carried it as a draw-follows-plan state.
    Its null control was "an install whose draw does follow the plan still
    reaches a COP model": the learner only, never the graders.
  - Not (a), not (b) and not (d): the reasons are in the document's
    section 2.
- **Cost test.**
  - P = 0.1 per round, estimated from one release escape over ten rounds
    (78 days). No class frequency exists.
  - cost(defect) is at least 12 h of fix wall-clock, plus an RCA seat and 73
    days of exposure.
  - The expected cost is 1.2 to 1.5 h per round.
  - A D1 provenance step costs about 10 min a round, covering only the
    `measured` / `observed` names a round adds (23 today), so it **passes**.
  - A CI-wide provenance type on every reading **fails**: it would rewrite
    the readers, and #3297 already concentrates the decision in
    `InstallCapability.cop_measured`.
- **Countermeasure.**
  - **Built:** the harness's `--check` is the detector. It exits 1 on v7.1.5
    and on main, 0 at the fix head, 2 on a skip tree, and 1 on each of two
    single-door trees, whatever the shell's cwd: it changes into the named
    root before importing, and exits 3 if a module it grades loaded from
    outside that root. It is hand-run and wired into no gate: #3297's own
    `tests/features.py` section is the instance's CI barrier, and a second
    copy would pin the same line twice.
  - **Proposed to the owner, not landed:** the D1 step "Measured means
    measured". It is quoted in the document's section 5, with its planning
    counterpart. Both are policy, so both wait for the owner's approval.
  - **Refused, and recorded:** the static provenance check.
- **Class.** No class is minted. The shape has one instance on the register,
  closed through one function.
  - The class search is in the document's section 3. It traced 23 names and
    the sample's readers.
  - It found one more self-referential seam, `_fold_capacity_envelope`'s
    no-heat branch. That is a learner, off by default, and kept by the owner's
    ruling of 2026-11-07 that no learner is gated.
  - The nearest classes are N-unmetered-reference and P11.
- **No issue comment.** `defect-root-cause.md` asks for a Root cause section
  on the defect's issue. This hotfix has no issue, and this seat's brief
  forbids comments. If the orchestrator opens one, the section is state (c),
  the cost-test numbers above, and the document's path, all in the
  document's section 6.
- **Owner decision owed.** The D1 step and its planning counterpart are
  policy. The register's `_rca["R10-RCA-COP-UNMEASURED"].parts_missing`
  holds both, `status` `proposed`, until the owner rules. Neither is landed
  here.

## Head

The head is `1b684dfbffdd6bbe3d864dc9d339c50c82739c9d`.

Repair of round 1's block, `countermeasure-unsound` at `b8fba2c8d`: the
detector measured the shell's cwd tree, not the checkout it was given.
`tests/harness.py` inserts the cwd-relative `tests` and `custom_components`
ahead of the root's own `sys.path` entries, so `heatpump_optimizer` loaded from
the cwd. Commits since `b8fba2c8d`:

- `142bbf919`: `main()` runs `os.chdir(root)` before its imports, then refuses
  with `REFUSED <module> loaded from <path>, outside <root>` and rc 3 if
  `harness`, `flow_meter` or the coordinator loaded from outside the root.
  The docstring states both.
- `8c1b6a017`: the document's section 5 states the cause and the re-taken
  rcs, two mutants join the set, the Reproduce recipe gains the two
  cross-cwd lines, and section 6 carries the class (below).
- `1b684dfbf`: a merge of origin/main `8a4cf2618`, no conflict
  (`LEDGER-MERGE: resolved tests/closures.json`).

The three commits were first written under another author identity and rebuilt
with `git commit-tree` on the same trees under the pinned one, before any push:
`git diff --quiet` between each rebuilt commit and its original exits 0, so
every figure below was taken on this tree.

The group's Carry 1 is this body's own Forward-carry item on the cwd capture
across `dev/audit/harnesses/` (body item 6d58568e), landed on
`handoff/audit-r10-roster` at `a62e0a80a2039fdf89953ac83ae06311f40beb4a`. It is
routed, not closed, by this pull request: only this seat's detector is repaired.

Alternatives considered for the fix:

- Anchor the two inserts in `tests/harness.py` to its own directory: lost,
  because a historical root such as v7.1.5 brings its own `tests/harness.py`
  with the cwd-relative inserts, so the detector would still read the cwd's
  tree when measuring any release before that change. It is carried as a
  class repair instead (Forward-carry).
- Import `harness` first, then re-put the root's entries ahead: works for the
  inserts known today, but any later cwd-relative read still follows the cwd.
  The change of directory makes cwd and root the same tree, and the
  provenance refusal catches whatever the change of directory misses.

## Mutation proof

`tools/pr/prepr.sh`'s diff-mutant step lists no mutants, because
`tools/audit/seat/mutant_run.py` skips `dev/` (`SKIP_PREFIXES`) and every
added line is under `dev/audit/`. So the detector was mutated by hand. Each
mutant was applied alone to a copy of
`dev/audit/harnesses/r10_rca_cop_unmeasured.py`; the tree's file was never
edited.

The scored command requires all of these together, each run with the shell's
cwd on a **different** tree from the target:

- rc 0 on the fix head `2d010b091`, cwd v7.1.5;
- rc 1 on v7.1.5, cwd the fix head;
- rc 2 on the skip tree, cwd v7.1.5;
- rc 1 on door N and on door T, cwd v7.1.5.

Unmutated it passes. Each mutant below fails it, so 8 of 8 are killed:

| mutant | the edit | first failing arm |
|---|---|---|
| M-a | the verdict line becomes `return 0` | v7.1.5 rc 0 |
| M-b | the skip guard becomes `if False:` | skip rc 0 |
| M-c | the null verdict is forced to `withheld` | door N rc 0 |
| M-d | the tuya verdict is forced to `withheld` | door T rc 0 |
| M-e | `null` is dropped from the verdict | door N rc 0 |
| M-f | the metered verdict is forced to `graded` | skip rc 0 |
| M-g | `os.chdir(root)` deleted | fix rc 3 (the refusal fires) |
| M-h | M-g, and the refusal's `return 3` made `pass` | fix rc 1 |

M-h is the head `b8fba2c8d` shipped. Run alone, with cwd the fix head and the
target v7.1.5, M-h prints `null=withheld tuya=withheld metered=graded` and
rc 0: the false clean the block named, reproduced on the mutant and absent at
this head.

## Null control

- **Cwd control (the block's).** The same detector, the same target, the
  shell's cwd moved between trees. At `b8fba2c8d` the verdict followed the cwd;
  at this head it follows the target. Both runs are in Figures.
- **Metered control.** The metered install (plain ids, 6.0 kW of heat over
  2.0 kW of power) grades on every tree, defective and fixed. So the detector
  can see a sample.
- **Skip control.** The fix head with `if measured:` turned to `if False:`
  withholds all three samples, and the detector exits 2, not 0.
- **No production change.** `git diff --stat $(git merge-base origin/main HEAD)...HEAD`
  lists `dev/audit/config/bugclasses.json`,
  `dev/audit/harnesses/r10_rca_cop_unmeasured.py`,
  `dev/audit/rca/R10-RCA-COP-UNMEASURED.md`, `dev/programme/delivery/3316.md`
  and `tests/closures.json`, nothing under `custom_components/`.

## Figures

Trees: detached worktrees of v7.1.5 (`516ad1b6b`), the #3297 head
`2d010b091`, origin/main `bb7dfb9bd`, and three copies of `2d010b091` edited
as the skip tree, door N and door T (section 5 of the document).

- **The block, reproduced at `b8fba2c8d`.** That head's detector, copied out,
  `python3 -I <copy> --check <target>` from `cd <cwd>`:
  - cwd v7.1.5, target fix head: `null=graded tuya=graded metered=graded`, rc 1.
  - cwd fix head, target v7.1.5: `null=withheld tuya=withheld metered=graded`, rc 0.
  - cwd `/tmp`: fix head rc 0, v7.1.5 rc 1.
- **This head, the full cwd by target matrix.** cwd each of v7.1.5, fix head,
  origin/main `bb7dfb9bd` and `/tmp`; target each of fix head, v7.1.5 and
  origin/main. All 12 cells: the fix head prints
  `null=withheld tuya=withheld metered=graded`, rc 0; v7.1.5 and origin/main
  print `null=graded tuya=graded metered=graded`, rc 1. No cell printed
  `REFUSED`.
- **Section 5's rcs, re-taken from a different cwd.** fix head rc 0 (cwd
  v7.1.5); v7.1.5 rc 1 (cwd fix head); origin/main rc 1 (cwd v7.1.5); skip
  tree `null=withheld tuya=withheld metered=withheld`, rc 2; door N
  `null=graded tuya=withheld metered=graded`, rc 1; door T
  `null=withheld tuya=graded metered=graded`, rc 1 (each cwd v7.1.5).
- **The Reproduce recipe**, run from this worktree with the tree paths
  substituted: v7.1.5 rc 1; `.` rc 1 (origin/main as merged here, before
  #3297); fix head rc 0; cwd fix head to v7.1.5 rc 1; cwd v7.1.5 to fix head
  rc 0.
- **Release reach.** `git tag --contains a63b576cd -l 'v*' --no-contains v7.1.6`
  lists the tags v4.0.0 (2026-08-26) to v7.1.5: 134.
- **The name census**, at the merge base `8a4cf2618`:
  `grep -ohiE '"[a-z_]*(measured|observed)[a-z_]*"'` over
  `custom_components/heatpump_optimizer/*.py`, `sort -u | wc -l`: 23.
- **The register.** `python3 tools/audit/fold_ledger.py check`: `fold_ledger: 50 classes, 755 instances, 121 in-tree judge survivors (rounds [8, 10]), 138 rca entries`, `0 violation(s)`.
- **Scoped gate.** `tests/closure.py select --diff $(git merge-base origin/main HEAD)`:
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running
  `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: on this macOS host the run dies with a traceback before its summary line, `PermissionError: Cannot get task port` in `_hb_stdlib_reads` (the heartbeat lane's stdlib sampler needs the `com.apple.system-task-ports` entitlement). The same command at origin/main `8a4cf2618` dies with the same traceback, so the crash is the host's, not this diff's; CI's Linux runner is the verdict.
  `tests/harness_headers.py` (it reads the changed docstring): `12 of 112 HARNESS HEADER CHECKS FAILED`, every failing line `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` (`rc=124 ... wall limit 900s exceeded`, host load average about 121). This diff does not touch that harness; `grep FAIL | grep -v sysid_estimator_frontier` returns only the summary line. CI runs it unloaded.
  `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **prepr.** `bash tools/pr/prepr.sh BODY.md` at `1b684dfbf`, `MUTANT_CMD` unset (the diff-mutant step skips; `mutant_run.py` skips `dev/` regardless, and the hand proof is above): `PRE-PR: 1b684dfbffdd6bbe3d864dc9d339c50c82739c9d 000000000000000000000000000 rc=0`. Its `ci predict` step: `CI PREDICT: no closures, fast, governance or instrument red predicted against 8a4cf2618c53`.

## Red checks

No check has concluded at this head; CI runs once the handoff is published.

At `b8fba2c8d`, every red was a **cancellation** of one run, `CI code pr=3316`
(run 42463804677, concluded `cancelled`), plus `gate`'s derived failure over it:
`tests / fast (3.14)`, `tests / closures`, `tests / coverage`,
`tests / coverage-ratchet`, `tests / ci-ratchet`, `tests / graders-head-copy`,
`tests / lane-proofs`, `tests / claims-autofix`, `tests / closures-autofix`
and `governance / instrument-self-tests`. No job log showed an assertion or an
`UNDER-SCOPED` line. The latest edit gate on that head (128707623015) exited 3
on `RATE-LIMITED`: the API refused the gate's read, not a test.

- Cause: run cancellation and a secondary rate limit, neither caused by this
  diff, which touches only `dev/` and one inert `tests/closures.json` line.
- Cheaper detector: none. A cancellation or an API rate limit is not a defect
  a local check predicts. What a local check does predict (`ci predict`, the
  carry routing, the body) was run before this handoff (Figures, prepr).
- Owed: a code run at this head that concludes. A failure there is the finding.

## Forward-carry

- **Doc claims #3297 leaves stale.** These are for the user-docs
  verification pass, once #3297 merges:
  - `README.md:614`: Observed COP "Needs measured power".
  - `docs/how-it-works.md:1240`: the watch "compares each measured COP".
  - The `ObservedCOPSensor` docstring: "derived from measured electrical
    input".

  At the fix head, observed COP needs a heat reading over a power reading,
  neither of them an estimate. Carry: #3139
- **The cwd capture across `dev/audit/harnesses/`.** Any harness that takes a
  root and imports `tests/harness.py` measures the cwd's tree unless it changes
  into the root first, for the cause in Head. This seat's detector is
  repaired. The rest are enumerated, as a superset and not a per-file trace,
  by `git grep -l 'from harness import\|import harness' -- dev/audit/harnesses/ | xargs grep -l sys.path`,
  less those `git grep -l os.chdir -- dev/audit/harnesses/` also lists. The
  repair belongs to the stage owning those harnesses: a change of directory
  per harness, or anchoring `tests/harness.py`'s inserts (current trees only,
  see Head). Recorded in the document's section 6 for the orchestrator to
  route. Carry: R10-RCA-COP-UNMEASURED

## Friction

none
