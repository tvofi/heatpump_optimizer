record: RCA for the orphaned-handoff class (N-orphaned-handoff)

Class `N-orphaned-handoff`, round 10. One root-cause record, `dev/audit/rca/N-orphaned-handoff.md`, and its citation in `dev/audit/config/bugclasses.json`: the class's `rca` list names it beside `R9-ORPHAN-HANDOFF`, with an `_rca` entry of level `class`, status `proposed`, as `defect-root-cause.md`'s "Where it is recorded" requires. No code, policy or roster change.

The record carries `root-cause.md`'s four products:

- **Named cause** (§1): the relay's `handoff-no-pr` level is replayed as append-only history (`orchestrator_tick.py`'s `relay_owed` keys an OWED row on `f[2]`, the kind token, while a POSTED row keys on a PR number, so nothing clears it); a detector arm read its own finding (`bus.sh orphans` exit 1) as unavailability; and an obligation had no age and no closer.
- **Process state** (§3): (c), with the `orchestrator.md` §5b duty quoted and the seat log showing it was read and queued and two openers dispatched and killed; residuals (a) for the design-to-build kind and (d) for a brief that grew after its handoff, kept separate.
- **Cost test** (§4): the per-round countermeasure cost against the measured seat-hours of R9's record, P = 1.0 (figures below).
- **Countermeasure** (§5): a barrier, not a refusal. The class is an audit class, so `defect-root-cause.md` says it owes a class-eliminating barrier and the cost test only picks its form: the obligations ledger's `handoff-no-pr` kind, derived each pass, aged, with an opener-attempt record, a content-covered close and a `design-build` kind. Its build and red/green demonstration belong to `R10-ORCH-MACHINERY`.

The record's §2a is a measurement record dated at origin/main `0cc148b2f`, 2026-10-21T08:54Z, and stays as written; `## Figures` re-takes what it measures at this pass's main.

## Head

`14fc4cf6e5c629e6c4242fa84790530ff00a6836`: the previous head `2cd325bc2816017a92daf4bb4587c6f4571504c1` with origin/main `289426c1fddef7efdb9278f0455cad8533b93ac6` merged in, a clean merge. The three-dot diff is unchanged: `dev/audit/config/bugclasses.json`, `dev/audit/rca/N-orphaned-handoff.md`, and this PR's own row `dev/programme/delivery/2545.md`. Figures taken 2026-10-21T12:08Z against that main.

## Mutation proof

n/a: no production line or check changes. The diff is one record, one register citation and the PR's own row. `fold_ledger.py check` is the register's reader, and it reads the new entry: its rca-entry count moves by one from the merge base to the head, with 0 violations at both (`## Figures`).

## Null control

The carry refusal is reproduced and separated from its cause by the roster ref alone: the same body under `carry_audit.py --roster-ref origin/main` refuses both destinations at rc=1, and under `--roster-ref origin/handoff/audit-r10-roster` routes every item at rc=0. So the refusal is the roster ref read, not the markers' grammar.

The re-measurement's controls: the PR query returns a PR for refs known to have one (`r10-i5-docs`, `r10-roster-ops`), so an empty answer for `r10-earlycutoff-coverage` is not the query failing; `git cherry` prints `-` for earlycutoff's one commit, where a commit with no equivalent on main prints `+`.

## Figures

All at origin/main `289426c1f`, 2026-10-21T12:08Z, unless the record dates them. The record's §2 and §4 figures read the orchestrator host's `tick.txt`, `tick.log`, `cloud-relay.log` and seat log; none exists in this container, so they stand as that seat measured them on 2026-10-20 and were not re-taken.

- stranded and superseded counts, and which §2a refs are still listed (`r10-earlycutoff-coverage` is; `r10-merge-pr-mandate` and `r10-rca-harness-friction` no longer are): `bash tools/audit/seat/bus.sh orphans --min-age-h 0`
- no pull request at `fix/r10-earlycutoff-coverage` or its `-pr` form; open #2555 for `r10-merge-pr-mandate`, #2561 for `r10-rca-harness-friction`, #2521 for `r10-i5-docs`, #2513 for `r10-roster-ops`, #2545 for this ref: `gh api 'repos/tvofi/heatpump_optimizer/pulls?state=all&head=tvofi:fix/<topic>'`
- earlycutoff's one commit is equivalent on main: `git cherry origin/main origin/handoff/r10-earlycutoff-coverage`
- `relay_owed` keys OWED on `f[2]` and POSTED on the PR number; the relay writes `OWED <utc> handoff-no-pr <ref> <sha>`: `grep -n 'def relay_owed' -A25 tools/audit/seat/orchestrator_tick.py` and `grep -n 'handoff-no-pr' tools/audit/seat/cloud_relay.sh`
- `content_superseded`'s M arm compares blob ids, so a hunk re-applied into a changed file reads stranded: `grep -n 'content_superseded()' -A12 tools/audit/seat/bus.sh`
- R9's measured seat-hours: `grep -n '5\.13' dev/audit/rca/R9-ORPHAN-HANDOFF.md`
- R9 per-round count and barrier: `python3 -c "import json;e=json.load(open('dev/audit/config/bugclasses.json'))['N-orphaned-handoff'];print(e['per_round'],e['barrier'])"`
- the median aged-ref age, the two per-round countermeasure costs and the brief's growth: arithmetic on the record's own figures, `python3 -c "a=sorted([41.9,44.3,47.5,48.9]);print((a[1]+a[2])/2, 5*12*144/3600, 5*8.25*144/3600, 31303-29976)"`
- register: 0 violations at both ends; rca entries 113 at the merge base, 114 at the head: `python3 tools/audit/fold_ledger.py check`
- carry refusal and its control: 2 bad destinations at rc=1 with main's roster, 0 at rc=0 with the roster branch at `524e8fdad`: `python3 -I tools/audit/carry_audit.py --roster-ref origin/main check --body <body>` and the same with `--roster-ref origin/handoff/audit-r10-roster`
- the carry check's wall time, 0.14 s: `python3 -I tools/audit/carry_audit.py --roster-ref origin/main check --body <body>` under `time`
- gate: `MODE: SCOPED -- 0 script(s) run`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`; run_always green (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`); `tests/entities.py` (under `env -u BASH_ENV`) and `tests/structure.py` pass

## Red checks

`pr-contract`: red at `2cd325bc2` (runs 39580002021 and 39580002446) on its last step, `carry_audit.py check`, BAD-DEST for `R10-ORCH-MACHINERY` and `R10-TICK-OWED-LEVEL`; `policy_lint.mjs --pr-body` and `figure_lint.mjs` passed with 0 refusals. The step reads the roster in the checked-out merge ref's tree, which is main's, and both groups exist only on `handoff/audit-r10-roster` (added there 2026-10-20 and 2026-10-21, before the run). Cheaper detector: `carry_audit.py --roster-ref origin/main check --body <body>`, 0.14 s, which reproduces the refusal exactly; it is on no local path, because neither `prepr.sh` nor `body_push.sh`'s `ci_predict.py` runs `carry_audit.py`. This body keeps both markers because those groups are the true owners and their briefs already hold the items. The check stays red at this head until those groups are on main's roster, which is the orchestrator's to land; a marker changed only to pass it would misroute the finding.

`nightly-status`: main's, not this branch's; the diff touches nothing it reads (the record, the register and this PR's own added row). At `2cd325bc2` it graded the scheduled run 39387919507, whose `slow` job failed in the replay lane: `synthetic-dhw-only.json: cycle_cost`, `loop_cpu_ratio` over its budget in `tests/replay.py`'s cost budgets, owned by roster group R10-REPLAY-CAP. The next scheduled run, 39563978649, has since concluded failure in `slow` (the same replay step) and in `mutation-nightly`, so a re-grade on this head reads that run.

## Forward-carry

- The ledger extension in §5.1–§5.4 and §5.6 (age and escalation, the opener-attempt record, the content-covered close, the availability contract) and §5.5's `design-build` kind are in `R10-ORCH-MACHINERY`'s brief ("Ledger extension owed") in `dev/programme/rosters/wave-r10-groups.json` at `handoff/audit-r10-roster` `524e8fdad`. That build owes the barrier's red/green demonstration, which the record's scratch prototype cannot give. Carry: R10-ORCH-MACHINERY
- §3's (d) observation is that a brief grew 41 h after its handoff. The countermeasure is to pin the brief at handoff and compare it on a later pass, which is the §6.4 roster-sync step; it is in `R10-ROSTER-OPS`'s carry list in `dev/programme/rosters/wave-r10-groups.json` at `524e8fdad` ("Carry: R10-ROSTER-OPS (from #2545)"). Carry: R10-ROSTER-OPS
- §1's first cause, the board replaying level lines as history, is the live defect `R10-TICK-OWED-LEVEL`'s brief states, and that group's carry list holds this item at `524e8fdad`. Its grammar must agree with the ledger's when that lands. Carry: R10-TICK-OWED-LEVEL

## Friction

- `finding-propagation.md`: contradiction: the rule counts a carry to the round's roster as landed once it is on `handoff/audit-r10-roster`, and `roster_lib.default_roster_ref` reads that branch, but `pr-contract`'s carry step and `queue_pre_flight.py` read main's roster, so a carry the rule accepts is refused until the roster lands on main. Measured above: 2 bad destinations under main's roster, 0 under the branch, same body. Carry: R10-ROSTER-OPS
- `tools/audit/seat/cloud-setup.sh`: cost: the payload said the venv was on PATH, but this harness's shell sources no login profile. `python3` was 3.11, `tests/entities.py` failed with an f-string `SyntaxError`, and the run passed only under `/opt/hpo/venv-ci/bin/python` from `/etc/profile.d/hpo-toolchain.sh`. Carry: dismissed: one rerun, the profile already names the interpreter

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01FcnyEy7GRaAT8ZocgKEW3V
