Closes #2272.

## Re-cut

R10-REPLAY-REAL-DAY: the replay lane's first real recorded day, tvofi's 2026-10-30 away episode, cut from the owner's export, masked, sealed and replayed through the current coordinator as a nightly guard on the away path. This body replaces the earlier ones. The round-3 block (mutation-vacuous away guard) is answered below; nothing else in the code moved except what `## Head` names.

The block: `recorded_away = []` in `run_fixture` (and, equivalently, the owner fixture with `controls.away` emptied) left the away check green with 0 commanded cycles. The repair, in `tests/replay.py`:

- `away_offenders(observations, events, expect_commanded)`: for a fixture in the new `AWAY_COVERED` set (the owner fixture; coverage is declared there, a design choice) the replay must carry at least one commanded cycle. The docstring now claims only what the check delivers.
- `away_coverage_offenders(name, events)`: a covered fixture whose `controls.away` holds no active command is refused. It runs in `run_fixture` and, per committed fixture, in `sanitiser_checks` (`away_coverage:<fixture>`).
- Two new controls pair each refusal with its green case: `control:away:coverage_needs_a_command`, `control:away:coverage_needs_a_commanded_cycle`.

## Head

Code head: a8f48032e911703f58acea90dc15cbea5f609437 (every figure below was taken at 80c6fa40a, which differs from it by one `git merge origin/main` of e4c9e2016, whose delta touches no file under `custom_components/`, `tests/replay*` or `tools/replay/`).

It is the PR head 18bdd5c88 plus a merge of the handoff ref's earlier tip d9ca33852 (the alert-47/48 code change 2042aefb7 and main at c3b7c964f), plus the repair commit. The d9ca33852 content was not in the round-3 review; it is in this diff for the reviewer.

## Mutation proof

In-tree harness, `HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py --replay` at 80c6fa40a: `RESULT killed=35 mutants=35 null_red=0`. The FAST tier alone (no `--replay`) was 32/32 (29 before; +3 rows). New rows:

- Fixture-side twin, the owner fixture with `controls.away` emptied: KILLED, red `away_coverage:owner-2026-10-30-away.json`.
- `away_coverage_offenders` not asking a command-less fixture: KILLED, red `control:away:coverage_needs_a_command`.
- `expect_commanded` check off: KILLED, red `control:away:coverage_needs_a_commanded_cycle`.
- REPLAY tier, `recorded_away = []` (round 3's survivor): KILLED, `away` 2 offenders (no active command, no commanded cycle), `cycle_cost` 1.
- REPLAY tier, `commanded = None` (round 2's): KILLED, `away` 13 (12 cycles and the coverage line).
- REPLAY tier, `no_default` exemption not handed the config: KILLED, `no_default` 14.

## Null control

- Unmutated head: FAST red `[]`; REPLAY null replay counts all 0 (`finite`, `unit`, `no_default`, `agreement`, `cycle`, `not_frozen`, `away`, `cycle_cost`).
- Finder's harness at both ends (`tests/replay.py --one tests/replay/owner-2026-10-30-away.json`, same env, `--step-minutes 60`): at the previous head 18bdd5c88 with `recorded_away = []` applied, `away` is `[]` (survives, 4 cycles); at this head the same mutant reads `away` 2 (REPLAY row above).
- Each new refusal is paired with its green case in `controls()` (`pair(...)` requires bad non-empty and good empty).

## Figures

none new beyond the ones above; commands: the harness line in `## Mutation proof`; `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED; `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed "no closures, fast, governance or instrument red predicted". The `COST_BUDGETS` recorded values are unchanged and the cost-budget restatement is below.

## Red checks

- CodeQL alerts 47 (`tools/replay/export.py`, recorder label on stderr) and 48 (`tests/replay.py` `_mariadb_install`, the invented credential in a temporary `secrets.yaml`). The handoff ref's commit 2042aefb7 (now in this branch) already removes the URL text from the label (`MYSQL_LABEL`) and renames the invented values; it could not be rescanned from this seat. If CodeQL still reports either site, it is a false positive (`redacted()` dropped user, password and query; the credential is invented) and the dismissal is owed by the owner, tvofi. Cheaper detector: none; CodeQL is the cheapest detector of its own alerts.
- No other concluded red check is known at this head: the last classification (round 3, at 18bdd5c88) was GREEN apart from `CodeQL`; `tests / replay` and `tests / mutation` succeeded. This head has not run CI.

## Carries

The group's eight roster carries (`dev/programme/rosters/wave-r10-groups.json` at origin/handoff/audit-r10-roster), by index. Dispositions are unchanged from the earlier rounds' accepted record; this pass re-took none of them.

- Carry 1 (the real day), Carry 2 (classify the fixture), Carry 3 (#2810), Carry 4 (the R10-DIAG-REDACT precondition on the exported document), Carry 5 (the day choice) and Carry 7 (the owner's export result): done.
- Carry 6 (STRANDED CARRY 57, cost-budget spread): half done, the budget is recorded; the open half, re-centring on the second CI class, is the orchestrator's restatement of R10-REPLAY-COST-BUDGET (see `## Forward-carry`).
- Carry 8 (D15-s1-04, a boolean under a credential-named key): done.

## Forward-carry

- Owed to the orchestrator: restate R10-REPLAY-COST-BUDGET's carry in `dev/programme/rosters/wave-r10-groups.json` as "re-centre the recorded 355.7 / 3740.0 / 0.249 on the second CI class's reading", with its control. Carry: R10-REPLAY-COST-BUDGET
- Carries 4, 6, 8 and 9 (live-bundle reads) are held verbatim by R10-LIVE-BUNDLE-READS in the roster. Carry: R10-LIVE-BUNDLE-READS
- The mold-guard finding is a carry of R10-USER-DOCS-VERIFY in the roster, unchanged. Carry: R10-USER-DOCS-VERIFY
- The widened `not_frozen` rule's blind spot (a published value tracking an input idling at zero that meets one non-zero value and then freezes is not judged; `control:not_frozen` still fires on the two-value case) is a disclosed design trade recorded in `tests/replay.py`'s comment, not a defect. Carry: dismissed: disclosed design trade with its control
- The warm-up claim, export-side masking figures and pump-draw comparison need the owner's untracked export and stay unverified. Carry: dismissed: no seat holds the export

## Friction

none
