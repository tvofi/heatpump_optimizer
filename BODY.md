record: RCA for the orphaned-handoff class (N-orphaned-handoff)

Class `N-orphaned-handoff`, round 10. One root-cause record, `dev/audit/rca/N-orphaned-handoff.md`, its citation in `dev/audit/config/bugclasses.json` (the class's `rca` list names it beside `R9-ORPHAN-HANDOFF`, with an `_rca` entry of level `class`, status `partial`, `landed` `b38c6431 (#2547)`), and the class search's harness, `dev/audit/harnesses/r10_relay_owed_class_reach.py`. No production, policy or roster change.

The record carries `root-cause.md`'s four products:

- **Named cause** (§1), dated to `1ebc737e7`: `relay_owed` keyed every relay OWED row on `f[2]`, so five kinds keyed on their kind token were never cleared by a `POSTED`. Two were levels replayed as history (`probe-ref`, `handoff-no-pr`), and three were one-shot events (`handoff-update`, `approve-held-runs`, `dispatch`). §1 now records that `b38c6431a` (`R10-TICK-OWED-LEVEL`, #2547, an ancestor of the merge base) keys every log event on its PR and makes the levels a rewritten `<log>.level`. The one-shot keying and the replay are closed in the tree this record merges into. What remains of the first cause is the level's closer set. The relay drops a `handoff-no-pr` line only for an open PR, a disposition, or a vanished ref. That gap is `R10-FLY-ORPHANS-REWRITTEN`'s brief. The other two causes are unchanged: the detector arm that read its own finding as unavailability for 143 passes, and an obligation with no age and no closer.
- **Process state** (§3): (c), unchanged.
- **Cost test** (§4): unchanged, except that the board-write saving is now dated to `1ebc737e7` and no longer credited to the ledger, because `b38c6431a` removed the replay behind it.
- **Countermeasure** (§5): §5.1 now keeps only the level's live-world closers. The extension's other parts (§5.2–§5.6) are unchanged. §7 routes §5.1's closers and §5.4 to `R10-FLY-ORPHANS-REWRITTEN`, and §5.2, §5.3, §5.5 and §5.6 to `R10-ORCH-MACHINERY`.

The previous body's third forward-carry, which asked `R10-ORCH-MACHINERY` to key the one-shot events on their PR, is dropped: `b38c6431a` already does it (`## Figures`). The record's §2 and §2a are measurement records dated where they were taken, and stay as written.

## Head

`6a70a8f49618da6f2744380e51a3b4a03f9bd19c`. It is the round-2 head `2124bc75b` with origin/main `46e3681276f99e8d3e4d12e9d316a46946f666d7` merged in by `0acc2fbc1` (a clean merge), plus `6a70a8f49`, which re-cuts the record's §1, §4, §5 and §7, the register entry, and the harness. The three-dot diff from the merge base `46e368127` covers `dev/audit/config/bugclasses.json`, `dev/audit/rca/N-orphaned-handoff.md`, `dev/audit/harnesses/r10_relay_owed_class_reach.py`, `tests/closures.json` (one inert-read line) and `dev/programme/delivery/2545.md`. Every figure below was taken at this head, with origin/main `46e368127` and roster ref `origin/handoff/audit-r10-roster` `743463c61`, on 2026-10-22 at about 00:50Z.

## Mutation proof

n/a: no production line or gate check changes. The harness under `dev/audit/harnesses/` is a round harness that no gate script runs. Its own perturbation runs are under `## Null control`. The register's reader, `fold_ledger.py check`, reads the new `_rca` entry: the rca-entry count moves 113 → 114 from the merge base to the head, with 0 violations at both.

## Null control

- **Event clearing, same run**: at `1ebc737e7` the harness reports the 4 PR-keyed event writers (three `owed` calls and `reviewer-fire`) as cleared by their `POSTED`, beside the 4 one-shot lines it reports uncleared.
- **Harness moves under the event keying** (P1): this head's tick with `b38c6431a`'s keying reverted to `f[2]` gives `events_uncleared=4`, against 0 when unmodified.
- **Harness moves under the level rewrite** (P2): this head's relay with `level_set` appending instead of rewriting gives `level_lines=4 level_items=2`, against `2/2` when unmodified.
- **The tick alone clears the events** (the verdict's "mixed" run, P3/P4): this head's tick over `1ebc737e7`'s relay clears 8 of 8 events, and `1ebc737e7`'s tick over this head's relay leaves 4 uncleared.
- **The finder's harness**: the reviewer's own replay, `evidence/replay.py` on `origin/review/2545`, gives `uncleared_after_POSTED=8` at `1ebc737e7`, 0 at this head and 8 under P1.

## Figures

- Class reach, new harness at both ends. Command: `python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py <tick.py> <cloud_relay.sh>`, with each file from `git show <commit>:tools/audit/seat/{orchestrator_tick.py,cloud_relay.sh}`. The rule is the harness's writer regex over the relay up to `self_test()`, with each row classified by what that tick does with it.
  - `1ebc737e7`: `RESULT writers=10 events=8 events_cleared=4 events_uncleared=4 events_unreported=0 level_writers=2 level_lines=4 level_items=2`
  - merge base `46e368127` and this head: `RESULT writers=10 events=8 events_cleared=8 events_uncleared=0 events_unreported=0 level_writers=2 level_lines=2 level_items=2`

  Every writer returned at this head, against its disposition:
  - `cloud_relay.sh:146`, `:148`, `:149` (`owed`) and `:242` (`reviewer-fire`): cleared by `POSTED`. Already sound.
  - `:232` `handoff-update`, `:236` `approve-held-runs`, `:239` and `:244` `dispatch`: cleared by `POSTED`, closed by `b38c6431a`.
  - `:177` `probe-ref`, `:253` `handoff-no-pr`: level writers through `level_set`, 1 line per item, closed by `b38c6431a`. The `handoff-no-pr` closer set is a distinct finding owned by `R10-FLY-ORPHANS-REWRITTEN`.
- The old harness at the same three commits gives `RESULT writers=10 kinds_on_kind_token=5 uncleared_lines=8` at `1ebc737e7`, and `writers=9 kinds_on_kind_token=4 uncleared_lines=0` at `46e368127` and this head. At those two commits its writer set lost both level writers and gained the self-test fixture at `cloud_relay.sh:376`. Its `kinds_on_kind_token=4` counts rows the tick clears. Same command, harness from `git show 2124bc75b:dev/audit/harnesses/r10_relay_owed_class_reach.py`.
- Perturbations P1–P4: as `## Null control`, from the same command with the edited copy as the argument. P1 replaces `pr = next((x for x in f[1:4] if x.isdigit()), None)` in `relay_owed` with `pr = f[2] if len(f) > 2 else None`. P2 replaces `level_set`'s `awk -v k="$1" '$3 != k' "$lv"` with `cat "$lv"`.
- Reviewer's replay: `python3 -I replay.py <tick.py>`, with `replay.py` from `git show origin/review/2545:evidence/replay.py`.
- Readers of the relay log outside `dev/audit/harnesses/`: `cloud_relay.sh` and `orchestrator_tick.py` only, at this head and at `1ebc737e7`. Command: `grep -rln 'cloud-relay.log\|relay_log' --include=*.py --include=*.sh --include=*.mjs .`, and `git grep -ln 'cloud-relay.log\|relay_log' 1ebc737e7 -- '*.py' '*.sh' '*.mjs'`.
- `b38c6431a` landed by #2547: `git log --format='%h %s' origin/main | grep -i '#2547'` prints `295c874e8 Merge pull request #2547 from tvofi/fix/r10-tick-owed-level`, and `git merge-base --is-ancestor b38c6431a 46e368127` exits 0.
- Register: 113 rca entries and 0 violations at the merge base `46e368127`, 114 and 0 at this head. Command: `python3 tools/audit/fold_ledger.py check`.
- Roster states at `743463c61`: `R10-FLY-ORPHANS-REWRITTEN` and `R10-ORCH-MACHINERY` not-started, `R10-RCA-HANDOFF-SLIP` in-progress, `R10-TICK-OWED-LEVEL` and `R10-ROSTER-OPS` done. Command: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | "\(.group) \(.resume.stage)"'`. `R10-ORCH-MACHINERY`'s `carry` holds `From #2545 (item 3985dac8)` and the brief pin `(from #2545)` via #2554. It does not hold the friction item below. Command: the same `git show`, piped to `jq -r '.groups[]|select(.group=="R10-ORCH-MACHINERY").carry[]'`.
- Carry routing: `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, rc=0, under both rosters. A draft of this body that routed the first forward-carry to `R10-FLY-ORPHANS-REWRITTEN` printed `BAD-DEST ... is not a group of the roster` under `origin/main` and rc=0 under the roster branch. That is the control, and the friction item below again. Commands: `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md`, and the same with `--roster-ref origin/main`.
- Gate: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. Command: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. These pass under `PYTHONPATH=tests/hastub`: the run_always set (`env_drift.py --claims-only 46e368127`, `closure.py selftest`, `layout.py`, `harness_headers.py`), `tests/structure.py`, `tools/audit/seat/tmp_paths.py --check` (0 refused) and `tests/entities.py` under `env -u BASH_ENV`.

## Red checks

From the check-runs API, `repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` for every commit of the PR. Conclusions failure, cancelled or timed_out:

- `pr-contract`, red at `81514b55c` (119148157821, 119148348823), `2cd325bc2` (119154980893, 119169171657) and `6e12aeb5b` (119236489332, 119243225219). It failed in the same step each time, `carry_audit.py check`: `BAD-DEST ... R10-ORCH-MACHINERY is not a group of the roster` and the same for `R10-TICK-OWED-LEVEL`. That step reads main's roster, which lacked both groups then. At `2124bc75b` both pr-contract runs succeeded. Cheaper detector: `carry_audit.py --roster-ref origin/main check --body <body>`, which takes seconds. It is on no local path, because neither `prepr.sh` nor `body_push.sh`'s `ci_predict.py` runs it. That is the friction item below.
- `nightly-status`, red at `81514b55c`, `2cd325bc2`, `6e12aeb5b` and `2124bc75b` (119558728031). It grades main's scheduled Tests run, and this diff touches nothing it reads. Owed by the orchestrator on main.
- `ci-ratchet`, `graders-head-copy`, `closures-autofix`, `closures`, `lane-proofs`, `coverage-ratchet`, `composed-proof` and `coverage` were cancelled at `81514b55c`, superseded by the next push (`cancel-superseded`). They are not reds. Each succeeded or was skipped at `2124bc75b`.

## Forward-carry

- §1's remaining cause, the `handoff-no-pr` level closed only by an open PR, a disposition or a vanished ref, is stated in `R10-FLY-ORPHANS-REWRITTEN`'s brief on `origin/handoff/audit-r10-roster` `743463c61` ("cloud_relay.sh classifies handoff-no-pr from its own rules"). `R10-ORCH-MACHINERY`'s obligations ledger replaces the relay's log scan and the tick's OWED scan, so it must keep the grammar `b38c6431a` landed. That group is the destination here because `R10-FLY-ORPHANS-REWRITTEN` is not yet on main's roster, which pr-contract's carry step reads. Carry text for the orchestrator to land: "The relay's event keying and level file landed by b38c6431a (events keyed on their PR and cleared by its POSTED; levels a rewritten <log>.level) must survive the ledger. Control: `python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py` prints `events_uncleared=0` and `level_lines` equal to `level_items` before and after; reverting either half moves it (`events_uncleared=4`, or `level_lines=4` for 2 items). (from #2545, dev/audit/rca/N-orphaned-handoff.md §1, §5.1)" Carry: R10-ORCH-MACHINERY
- §5's ledger-extension controls (the `ecaf178c` content-covered close with a positive case and a null case, and the §5.6 exit-code red case) are landed in `R10-ORCH-MACHINERY`'s carry at `743463c61`. Carry: R10-ORCH-MACHINERY (item 3985dac8)
- §3's (d) observation, the brief pinned at handoff, is landed in `R10-ORCH-MACHINERY`'s carry at `743463c61`, re-carried from `R10-ROSTER-OPS` by #2554. Carry: R10-ORCH-MACHINERY

## Friction

- `finding-propagation.md`: contradiction: the rule counts a roster carry as landed once it is on `handoff/audit-r10-roster`, but `pr-contract`'s carry step reads main's roster. Six pr-contract runs on this PR refused routings to groups the roster branch already held (`## Red checks`). The roster-sync step is `R10-ORCH-MACHINERY`'s. Carry text for the orchestrator to land: "pr-contract's carry step and the rule must read the same roster; prepr or body_push should run carry_audit against the roster the check will read. (from #2545)" Carry: R10-ORCH-MACHINERY
- `brief`: stale: the brief names `tools/audit/seat/carry_audit.py`, but the instrument is `tools/audit/carry_audit.py`. Carry: dismissed: one-line path slip, instrument found

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01NXVK56Dsy5yvQjYnEc2fo5
