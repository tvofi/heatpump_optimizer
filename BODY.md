R10-FLOW-AUTOTRAIN: the merge pitch becomes a mechanism instead of an agent's turn. Until now nothing wrote a train queue. `merge_train.py`'s docstring documented the schema, and every pitch waited for a seat to assemble pull request numbers, verdict heads and comment ids by hand. Every input was already machine-readable, so this diff reads them.

- `merge_train.py queue <file|->` (`Train.build_queue`, `Train.admit_verdict`). It reads every open pull request, oldest (lowest number) first, and prints one `QUEUE #<pr>` or `LEFT #<pr>: <why>` line each. In order:
  - it leaves out the record branch (`record_row.RECORD_BRANCH`; `--bot-prs` merges it);
  - it needs a confirmed verdict on the bus (`verdict/<pr>`, from `git ls-remote`);
  - the approver App's newest `Fix review:` comment must be that tip's posting, keyed on the `bus: verdict/<pr> at <tip>,` line `bus.sh`'s post writes. A verdict that is confirmed but not posted, or one a later verdict superseded, waits;
  - that verdict must be `merge` at the head, or `app_approve.sh --carry` must say it carries to the head. The carry is asked only where verdict and head differ.

  The approver identity is `proof_watch.verdict_allowlist`'s (login and id, the same filter as `orchestrator_tick.py`'s verdict levels). The entry carries the comment id the mandate approval quotes. Files are never read: a budget, policy or workflow head is queued like any other and goes to the serial route the batch's own admission applies (`file_class`, then `raise_hold` and `policy_gate`, which `--pre-flight` parks on). That keeps a second copy of those rules out of the builder. An unreadable pull request list, approver identity or bus listing stops the builder, because a queue built on a failed read is a queue nobody read.
- `merge_train.py pitch [--once] [--every S] [--mandate M] [--state-dir D]` (`pitch`, `live_train`, `launch_train`). It holds, with no queue built, while `train.pid` in the state dir is live (`kill -0`, train.sh's own test). It also holds while the obligations ledger has an open `train-stop` (`ledger.fold`: a stopped train is read before its queue is reloaded, per nudge.md step 3), and when the queue at the same heads already had its train (`pitch-last.json`), so a stopped train is not restarted every pass on whatever stopped it. Otherwise it writes `pitch-queue.json`. An empty queue starts no train. A non-empty one runs `queue_pre_flight.py` (no summary line means a refusal) and then starts exactly one `train.sh --bot-prs --approval-carry --pre-flight` in its own session. `launch_train` reports it STARTED only once train.sh holds its pidfile; a train.sh that refuses first, for example on a live pidfile or no seat venv, is REFUSED with its own line. `--once` is one pitch and its rc: the tick loop's job, and the job the R10-ORCH-MACHINERY beat hosts unchanged. Without it the pitch runs every `--every` seconds (default 3600, the hourly pitch) and is meant to run detached under `daemonize.py`. Every merge stays the train's, and the train approves before it merges (app_approve.sh, or the owner's review under `--mandate` on a code-owned path). A posted merge verdict is not a GitHub approval, and nothing here approves.
- `tick_loop.sh --pitch` (off by default). The first pass and then the first pass an hour after the last pitch (`HPO_TICK_PITCH_EVERY`, stamped in `<out>.pitch.at`) run `merge_train.py pitch --once` after the board. Its output goes to `<out>.pitch.log`, and one `TICK-PITCH <utc> rc=<rc> <last line>` line follows the banner. `HPO_PITCH_MANDATE` becomes the train's `--mandate`. Without the flag the loop is byte-for-byte today's: the existing arms pass unchanged and a null-control arm pins it. The first live pitch runs with the orchestrator watching, as the brief says, which is why the flag is opt-in.
- `sweep_template.md` item (3) (the #2628 review's carry on this group): it now names the hourly pitch, `--bot-prs` merging the record PR inside the train, and the batch's serial route for budget and policy heads. `INSTRUMENTS.md` gains the `queue` and `pitch` lines.

Alternatives considered:

- (a) Filtering budget and policy heads out in the builder, as nudge.md step 3's hand procedure does. That would duplicate `file_class`, `raise_hold` and the policy corpus filter in a second place, and the brief asks for the serial route the batch admit already applies.
- (b) Reading the verdict's first line from the bus ref's `VERDICT.md` instead of the comment. That gives no comment id, and it is not what `app_approve.sh`'s evidence gate reads at the merge. Keying on the posted comment's `bus:` line binds the two.
- (c) A separate pitch script. That would mean a new tracked file and a second import of the train's methods, where a subcommand beside `build_queue` reuses `Train.run`'s retried reads and stubs.

## Head

`acdc10b22e018087626b0d545c22cf8e99965b97` on merge base `50af6174f53c0f9bec3f705c3a4bb99615f71acc`, which was origin/main's tip at 2026-10-24T09:00Z (`git rev-parse origin/main` after `git fetch origin main`). Four commits: the change (`6106b480d`), the two harnesses' `inert_reads` entries for `tests/harness_headers.py` (`ci_predict.py --apply-inert`, the predictor's own repair), and the live harness. No production file (`custom_components/`) is touched.

## Mutation proof

`bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` (sha1 024288e70924423ce7bb618c570f07a69c7e2246) plants 25 mutants, one rule each, and runs the owning self-test (`merge_train.py --self-test`, or `tick_loop.sh --self-test`) per mutant from a clean checkout, restoring the file between runs. M0 at the head: `merge_train self-test: 267 checks, 0 failed; tick_loop self-test: 17 checks, 0 failed`. Every mutant failed at least one named arm. The arm(s) unique to each:

- A1 record-branch skip off: "the record pull request is left to --bot-prs (#16)"
- A2 no-tip refusal off: "no verdict/<pr> on the bus is left (#17)"
- A3 approver login check off: "a merge comment under another login is no verdict, though it carries the App's id (#19)"
- A4 approver id check off: "a merge comment under the App's login and another id is no verdict (#20)"
- A5 newest → oldest verdict: "a newest verdict that is blocked is left, though an older one was merge (#14)"
- A6 `bus:` line check off: "a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)"
- A7 a blocked verdict read as merge: the #14 arm
- A8 carry refusal ignored: "a head the carry refuses is left, with the carry's own line (#13)"
- A9 carry asked at every head: "the carry is asked only where the verdict is not the head (#12, #13)"
- A10 order unsorted: "the fixture builds exactly #11 ..., #12 ... and #15 ..., oldest first"
- A11 failed list read as empty: "an unreadable pull request list stops the builder"
- A12 failed bus listing ignored: "an unreadable verdict bus listing stops the builder"
- P1 live-pidfile hold off: "a live train's pidfile holds the pitch -- no read, no queue, no train"
- P2 empty-queue stop off: "an empty queue starts no train and runs no pre-flight"
- P3 same-queue hold off: "the same queue at the same heads starts no second train"
- P4 pre-flight summary check off: "a pre-flight that prints no summary refuses, and no train starts"
- P5 `--pre-flight` dropped from PITCH_FLAGS: "a stale pidfile does not hold it; ... ONE train.sh with --bot-prs --approval-carry --pre-flight" (the arm names the three flags literally, not through the constant)
- P6 launch-failure refusal off: "a train.sh that exits before taking its pidfile is REFUSED ..."
- P7 a dead pid read as live: the stale-pidfile arm
- P8 ledger train-stop hold off: "an open train-stop in the ledger holds the pitch -- no read, no train"
- P9 `--once` read as always: "pitch without --once: a pitch every 3600 s (the hourly pitch) until stopped"
- P10 `--every` ignored: the same arm
- T1 pitch run without `--pitch`: "null control: without --pitch no pitch runs (the default loop starts no train)"
- T2 pitch step deleted: "--pitch: one pitch after the tick, its last line after the banner, ..."
- T3 hourly cadence off: "--pitch: the next pass inside the hour pitches nothing (the hourly pitch)"

A2's first planting crashed on a `tip[:12]` slice instead of failing an arm. The message now prints the full sha, and A2 fails its named arm (above). The CI mutation lane does not cover `tools/`.

## Null control

- At merge base 50af6174f, `python3 tools/audit/seat/merge_train.py queue -` refuses with `argument cmd: invalid choice: 'queue' (choose from 'run', 'batch', 'wait-ci', 'unstale', 'classify')`. Nothing wrote a queue.
- In the self-test fixture, each LEFT arm has its admitted twin, which is the null control for that rule: #11 (verdict at the head) and #12 (carried) sit beside #13 (carry refused); #14 (newest blocked, older merge) and #18 (tip not yet posted) beside #11; #19 and #20 (wrong login or wrong id) beside #11. A closed `train-stop` holds nothing, a new verdict at a moved head starts a train again, and a pass once the interval has passed pitches again.
- Without `--pitch` the tick loop runs no pitch, so the default loop starts no train. Its 12 earlier self-test arms pass unchanged.

## Figures

- Live queue at 2026-10-24T09:00Z, `python3 dev/audit/harnesses/r10_flow_autotrain_live.py <prs.json> <comments.json>` (sha1 20bc55649ced1e09adf20bbae0fea41baec476dc). git ran for real: `ls-remote` of `verdict/*`, the fetches, and `app_approve.sh --carry` where it applied. The two gh reads were answered from the GitHub MCP tools' reads of the seven open pull requests and of the approver comments on the three that hold a `verdict/<pr>` ref, because this seat's `gh` token is refused. Queued: #2683 (verdict 8d965647, comment 6381802091), #2688 (b451bde0, 6381850867), #2689 (44ee0e5f, 6382009283), each verdict at its head. Left: #2687 (the record PR), and #2678, #2690 and #2691 (no `verdict/<pr>`). That snapshot is stale the moment a verdict lands. An earlier run the same morning, with #2683's round-3 comment not yet in the saved reads, left #2683 with "the newest posted verdict (comment 6379079217) is not verdict/2683's tip 36fe4e74": the confirmed-not-posted arm, on live data. A run before that queued #2683 through the real `--carry` (verdict 07b83e9b, carried across `ci: merge main` to 8d965647).
- Mutants: 25 planted, 25 killed by a named arm, `bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` (rule above: a mutant is killed when its self-test's last line reports one or more failures and no crash line).
- Self-tests at the head: `python3 tools/audit/seat/merge_train.py --self-test` (267 checks, 0 failed), `bash tools/audit/seat/tick_loop.sh --self-test` (17 checks, 0 failed), `bash tools/audit/seat/train.sh --self-test` (ok), `python3 -I tools/audit/seat/sweep_render.py --self-test` (21 checks, 0 failed), `python3 -I tools/audit/seat/selftest_wiring.py --check` (0 unwired), `python3 tests/throwaway_git.py --check` (0 refused), `python3 -I tools/audit/seat/tmp_paths.py --check` (0 refused), `python3 -I tools/audit/seat/ref_privacy.py --self-test` (0 failed; no new push site).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, and the one script is `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` reports 2 of 2425 failed, and the same run at merge base 50af6174f also reports 2 of 2425. Its FAIL-line set, with each line's bracketed detail stripped, is identical at both ends (`diff` of the two lists empty). The two failures are `hb:positive_control`: py-spy cannot name the spin in this container. run_always: `tests/closure.py selftest` (117 pins passed), `tests/layout.py` (ok), `tests/harness_headers.py` (all passed). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (it measures `custom_components/` only, which this diff does not touch).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no closures or fast red predicted at the head.

## Architecture score

n/a: no file under `custom_components/` changes, so `tools/audit/archscore/` reads nothing this diff moves.

## Unpinned sites

none: the diff adds no production line. The CI mutation lane's scope is production code, and the 25 planted mutants above are this tool's own mutation proof.

## Red checks

- `tests / nightly-status`, red on main's ancestry: it grades `main`'s nightly lane, not this head (`merge_train.py`'s default `--ignore-red`). This diff did not turn it red, and the detector that grades it is the nightly itself.
- `tests / ci-ratchet`, which may be red on main's push runs: GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix (`fix/r10-ci-ratchet-artifacts-pr`, #2690) is in flight. That red is not this branch's, and this diff does not touch `tests/ci_ratchet.py`.
- None turned red by this branch locally. The one red `ci_predict.py` predicted, `tests / closures` INERT READS for each new harness, was repaired before the handoff by `--apply-inert` (the predictor is the cheaper detector, at a few seconds per run, already paid).

## Forward-carry

1. nudge.md step 3 says to leave budget-file and policy-path heads out of the queue and direct-merge them (step 7). The pitch queues them for the batch's serial route instead, where `--pre-flight` parks a budget raise or policy head the owner has not approved at that head. Step 3's hand procedure, which names `merge_train.py run` (serial, no admission routing), now disagrees with the mechanism it describes. The orchestrator or R10-POLICY-INSTRUMENTS should bring step 3 into line, or rule that the builder filters them. Control: diff nudge.md step 3 against `Train.admit_verdict` and `sweep_template.md` item (3); no contradiction remains. Not yet in that group's roster carry: this seat writes no roster. Carry: R10-POLICY-INSTRUMENTS
2. R10-ORCH-MACHINERY hosts the pitch as the beat's pitch job: `merge_train.py pitch --once --state-dir <dir> [--mandate M]`, last line `PITCH HELD|EMPTY|STARTED|REFUSED`, rc 2 only on REFUSED. Its `train-stop` read is `ledger.fold(ledger.events(home, log))` at the default ledger home. Nothing writes a `train-stop` yet, so the producer the beat adds must `ledger.py open train-stop <pr> <head>` on a `TRAIN STOPPED` line. The roster already carries this seam on R10-FLOW-AUTOTRAIN (the "Seam with R10-ORCH-MACHINERY" item). Carry: R10-ORCH-MACHINERY

## Friction

- dev/governance/roles/fixer.md#3: cost: this seat's `gh` token is refused (`gh auth status`: "Failed to log in"), so the live run had to answer the two gh reads from the GitHub MCP tools through a stub harness. The pitch's first real run, with `gh`, is the orchestrator-watched one the brief already owes. Carry: dismissed: the live pitch is orchestrator-watched by the brief, and a cloud seat's credentials are its environment
