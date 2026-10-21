record: RCA for the orphaned-handoff class (N-orphaned-handoff)

Class `N-orphaned-handoff`, round 10. One root-cause record, `dev/audit/rca/N-orphaned-handoff.md`, its citation in `dev/audit/config/bugclasses.json` (the class's `rca` list names it beside `R9-ORPHAN-HANDOFF`, with an `_rca` entry of level `class`, status `proposed`), and the class search's harness, `dev/audit/harnesses/r10_relay_owed_class_reach.py`. No production, policy or roster change.

The record carries `root-cause.md`'s four products:

- **Named cause** (§1): `orchestrator_tick.py`'s `relay_owed` keys every relay OWED row on `f[2]`, and a `POSTED` row on a PR number. The rule that enumerates the reach is the writer set of `cloud_relay.sh` (every `logline OWED`, `owed` call and literal `printf 'OWED ...'`): 10 writers. Four are PR-keyed and cleared by `POSTED` (three `owed` calls, `reviewer-fire`). Five kinds are keyed on their kind token and never cleared: the levels `probe-ref` and `handoff-no-pr`, replayed as history, and the one-shot events `handoff-update`, `approve-held-runs` and `dispatch`, which stay OWED after their PR's `POSTED`. The log has no third reader. The other two causes are unchanged: a detector arm read its own finding (`bus.sh orphans` exit 1) as unavailability, and an obligation had no age and no closer.
- **Process state** (§3): (c), with the `orchestrator.md` §5b duty quoted. §3 now cites the landed countermeasure to the cap half of the delay: `orchestrator.md` §5, the soft cap never refuses opening or updating a pull request for an owed handoff (tvofi, 2026-10-20, `5d477d6e9`). Residuals (a), the design-to-build kind, and (d), a brief that grew after its handoff, are kept separate.
- **Cost test** (§4): 1.65–2.4 h per round against R9's 5.13 seat-hours, now stated as **quoted, not verified**. R9's record takes the figure from its launching seat's session record, which neither seat could read. P = 1.0. The class is an audit class, so the barrier is owed whatever the test says.
- **Countermeasure** (§5): a barrier, not a refusal. §5.1 now covers every kind the writer set returns. The two levels are derived each pass from the live world. The three one-shot kinds are events keyed on their PR. The PR-keyed rows keep their grammar. The age, attempt record, content-covered close, `design-build` kind and availability contract (§5.2–§5.6) are unchanged. The build and its red/green demonstration belong to `R10-ORCH-MACHINERY`.

The record's §2 and §2a are measurement records dated where they were taken. They stay as written.

## Head

`7b05b95f346d4bba88f799a23601def16d305c50`: the reviewed head `6e12aeb5bd976a7520361dd05bf9300cb6c77a04` with origin/main `1ebc737e7e187a1d45c62069ae8ab69c465db928` merged in (a clean merge), plus three commits: `e83e6fa03` re-cuts the record, widens the register entry's `subject` and `countermeasure` and adds the harness, and `e8b4787a5` makes the harness's default paths repo-root-relative (`harness_headers.py` refuses a `parents[N]` depth root), and `7b05b95f3` records the harness as an inert read of `tests/harness_headers.py` in `tests/closures.json`, as written by `tools/pr/ci_predict.py --apply-inert` after `body_push.sh`'s predictor named it. The three-dot diff covers `dev/audit/config/bugclasses.json`, `dev/audit/rca/N-orphaned-handoff.md`, `dev/audit/harnesses/r10_relay_owed_class_reach.py`, `tests/closures.json` (one inert-read line), and this PR's own row `dev/programme/delivery/2545.md`. Figures were taken against main `1ebc737e7` and roster ref `handoff/audit-r10-roster` `ae0f167c9` on 2026-10-21.

## Mutation proof

n/a: no production line or check changes. The new file is a round harness under `dev/audit/harnesses/`, and no gate script runs it. The register's reader, `fold_ledger.py check`, reads the new `_rca` entry: its rca-entry count moves by one from the merge base to the head, with 0 violations at both (`## Figures`).

## Null control

- **The class replay**, in the same run: the 4 PR-keyed writers print 0 lines after their `POSTED`, and the 5 kind-keyed kinds print 8.
- **Perturbation** (the harness moves under the defect's own mechanism): the same harness, pointed at a scratch copy of `orchestrator_tick.py` whose OWED arm also requires `f[2].isdigit()`, prints `uncleared_lines=0`. Unmodified, it prints 8.
- **Base control**: the same harness, run on `orchestrator_tick.py` and `cloud_relay.sh` as they were at the reviewed head `6e12aeb5`, prints the same `RESULT`. The merge brought in no change to either file that moves the count.
- **The carry re-route**: under `--roster-ref origin/handoff/audit-r10-roster`, the previous body's two `R10-ROSTER-OPS` markers are refused as `R10-ROSTER-OPS is done` (the reviewer's `ev/body_carry.txt`). This body's markers route at rc=0 under the same ref (`## Figures`).

## Figures

All at origin/main `1ebc737e7`, roster ref `ae0f167c9`, 2026-10-21, unless the record dates them.

- Class reach: `RESULT writers=10 kinds_on_kind_token=5 uncleared_lines=8 pr_keyed_writers=4 pr_keyed_lines=0`; `kinds keyed on the kind token: approve-held-runs dispatch handoff-no-pr handoff-update probe-ref`. Command: `python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py`. The rule is the writer regex in the harness over `tools/audit/seat/cloud_relay.sh`. Each writer returned, against its disposition:
  - `cloud_relay.sh:132`, `:134`, `:135` (`owed`) and `:222` (`reviewer-fire`): PR-keyed, cleared by `POSTED`, so already sound.
  - `:158` `probe-ref` and `:232` `handoff-no-pr`: levels, not cleared. Closed by §5.1's derivation (R10-ORCH-MACHINERY) and by `R10-TICK-OWED-LEVEL`'s level/event split, whose brief names both.
  - `:212` `handoff-update`, `:216` `approve-held-runs`, `:219` and `:224` `dispatch`: one-shots, not cleared. Closed by §5.1's PR-keyed events. `R10-TICK-OWED-LEVEL`'s brief does not yet state this part, so it is carried below.
- Perturbation: `uncleared_lines=0`, from the same command with a first argument naming a copy of `tools/audit/seat/orchestrator_tick.py` whose `relay_owed` OWED arm adds `and f[2].isdigit()`.
- Base control: identical `RESULT` from the same command with the two files at `6e12aeb5` (`git show 6e12aeb5:<path>`) as its arguments.
- Readers of the relay log: `cloud_relay.sh` and `orchestrator_tick.py` only. Command: `grep -rln 'cloud-relay.log\|relay_log' --include=*.py --include=*.sh --include=*.mjs .`
- R9's 5.13 h provenance: "not independently verified by me" and "I verified the arithmetic ... and nothing else". Command: `grep -n 'not independently verified\|nothing else' dev/audit/rca/R9-ORPHAN-HANDOFF.md`
- The landed cap countermeasure: `5d477d6e9` "docs(seat): the soft cap gates only group dispatch, never an open or update". Command: `git log --format='%h %s' -S 'never refused by it' origin/main -- dev/governance/roles/orchestrator.md`
- Register: 0 violations at both ends, with rca entries 113 at the merge base `1ebc737e7` and 114 at the head. Command: `python3 tools/audit/fold_ledger.py check`
- Roster states at both `origin/main` and `ae0f167c9`: `R10-ROSTER-OPS` done, `R10-ORCH-MACHINERY` not-started, `R10-TICK-OWED-LEVEL` in-progress. `R10-ORCH-MACHINERY`'s brief holds "Ledger extension owed" and not the brief pin or the friction item. `R10-TICK-OWED-LEVEL`'s brief names `handoff-no-pr` and `probe-ref` but not the one-shot kinds' key. Command: `git show <ref>:dev/programme/rosters/wave-r10-groups.json`, with the groups' `resume.stage`, `brief` and `carry` read by `json`.
- Carry routing: `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, rc=0, under both `origin/handoff/audit-r10-roster` and `origin/main`. Commands: `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md`, and the same with `--roster-ref origin/main`.
- Gate: `MODE: SCOPED -- 1 script(s) run`, and `scope.run` names `tests/entities.py` (the `closures.json` line). Command: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. The run_always set passes: `env_drift.py --claims-only`, `closure.py selftest`, `layout.py`. `harness_headers.py` (all 109 checks), `tests/structure.py`, `tools/audit/seat/tmp_paths.py --check` (0 refused) and `tests/entities.py` under `env -u BASH_ENV` (all 2382 checks) pass.

## Red checks

`pr-contract` was red at `6e12aeb5` (runs 119236489332 and 119243225219) on its last step only, `carry_audit.py check`, with BAD-DEST for `R10-ORCH-MACHINERY` and `R10-TICK-OWED-LEVEL`. That step reads main's roster, and when it ran, main's roster lacked both groups. Main's roster now carries both (`## Figures`), and this body routes every item at rc=0 under main's roster and under the roster branch. A re-run at this head reads that roster. Cheaper detector: `carry_audit.py --roster-ref origin/main check --body <body>`, which is on no local path, because neither `prepr.sh` nor `body_push.sh`'s `ci_predict.py` runs `carry_audit.py`. This is the friction item below.

`nightly-status`: this check grades main, not this branch, and the diff touches nothing it reads. At `6e12aeb5` it graded scheduled run 39563978649 (main `c77f89dc6`), which concluded failure in `slow`, the replay cost-budget lane owned by R10-REPLAY-CAP, and in `mutation-nightly`. That run is still the latest scheduled Tests run on main, so the check will read red at this head for the same reason.

## Forward-carry

- §5's ledger extension is in `R10-ORCH-MACHINERY`'s brief ("Ledger extension owed"). That brief carries the claims but not their controls. The orchestrator should add this carry text to the group: "Controls for the Ledger extension: the content-covered close's positive case is `ecaf178c` (`git cherry origin/main origin/handoff/r10-earlycutoff-coverage` prints `-`, so it closes), and its null is a hunk re-applied with an edit (`git cherry` prints `+`, so it stays open). The availability contract's red case is the 143-pass shape: `bus.sh orphans` rc 1 with ORPHAN rows and a summary line must read as a finding and never as unavailability, and rc 0 with a summary and zero rows reads empty. (from #2545, dev/audit/rca/N-orphaned-handoff.md §5.4, §5.6)" Carry: R10-ORCH-MACHINERY (item 3985dac8)
- §3's (d) observation is that a brief grew 41 h after its handoff. Its countermeasure was carried to `R10-ROSTER-OPS`, which is done (#2513). It now goes to the group that builds the §6.4 roster-sync and record verifier. Carry text for the orchestrator to land: "Pin each group's brief (a hash) when its handoff is pushed, and have the roster-sync pass compare it against the live brief; a brief that changed after its handoff is flagged to the orchestrator, never silently re-dispatched. (from #2545, dev/audit/rca/N-orphaned-handoff.md §3, state (d))" Carry: R10-ORCH-MACHINERY
- §1's cause reaches the one-shot kinds that `R10-TICK-OWED-LEVEL`'s brief does not name. Carry text for the orchestrator to land: "The one-shot relay kinds `handoff-update`, `approve-held-runs` and `dispatch` are written `OWED <utc> <kind> <pr> ...`, so `relay_owed` keys them on the kind token and their PR's `POSTED` never clears them. Key each event on its PR. The replay is `dev/audit/harnesses/r10_relay_owed_class_reach.py`, which must print `uncleared_lines=0` after the fix and `pr_keyed_lines=0` before and after. (from #2545)" Carry: R10-TICK-OWED-LEVEL

## Friction

- `finding-propagation.md`: contradiction. The rule counts a carry to the round's roster as landed once it is on `handoff/audit-r10-roster`, but `pr-contract`'s carry step reads main's roster, so a carry the rule accepts is refused until the roster lands on main. Round 1 of this PR measured 2 bad destinations under main's roster and 0 under the branch for the same body. A group finishing between the body and the check also moves the answer, which happened here with `R10-ROSTER-OPS`. The roster-sync step is `R10-ORCH-MACHINERY`'s. Carry text for the orchestrator to land: "pr-contract's carry step and the rule must read the same roster; prepr or body_push should run carry_audit against the roster the check will read. (from #2545)" Carry: R10-ORCH-MACHINERY
- The brief: wrong path. It names `tools/audit/seat/carry_audit.py`, but the instrument is `tools/audit/carry_audit.py`. Carry: dismissed: one-line path slip, instrument found

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01L3iRhj6rzqvKKdTFa9HhP1
