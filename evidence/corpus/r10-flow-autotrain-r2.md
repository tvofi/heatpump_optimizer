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

**Round 2: one reader of the verdict grammar.** The opener at r1 was refused by prepr's agreement lane. `python3 -I tools/policy/agreement_py.py --run` reported `RESULT divergent=0 unregistered=2 dead=0`, because `merge_train.py` (the queue) and `orchestrator_tick.py` (the verdict levels) each compiled the same two patterns, `Fix review: merge ([0-9a-f]{40})` and `Fix review: blocked ([0-9a-f]{40}) [a-z-]+: .+`. The patterns now live once, in `tools/audit/seat/proof_watch.py`: `VERDICT_MERGE`, `VERDICT_BLOCKED` and `parse_verdict(first) -> ("merge"|"blocked", sha) | None`. `Train.admit_verdict` and `Tick.verdict_levels` both read through `parse_verdict`. `verdict_levels` now loads proof_watch once per pass and hands it to `_verdict_authors`, so the identity and the grammar come from the same module. The behaviour is unchanged: the same two patterns, the same LEFT text (`the newest verdict is blocked|unparsed: ...`), the same MERGE-READY and BLOCKED-UNFIXED lines.

Why proof_watch.py and not a third module: the grammar's owner is `bus.sh`'s `verdict_sha` (the patterns are `app_comment.sh`'s, character for character), and that is shell, which Python cannot import. proof_watch.py is already the one Python reader both callers import for the approver identity (`verdict_allowlist`), and it is the merge-side reader of the newest allowlisted `Fix review: merge <sha>` verdict. A new module would be a third owner, and registering the duplicate would keep two copies with nothing to stop them drifting apart. Sharing is possible, so nothing is registered. `ledger.py`'s `VERDICT` (`(?:merge|blocked) <sha>(?: |$)`) and `review_strength.py`'s `verdict: #<pr> ...` are different grammars that agreement_py does not pair, and this diff leaves them alone.

## Head

`77ef64df943b24d722f725b83c7e00295c7ee335` is the code head, on merge base `c6ef25a6534a612a1cdde1ebb9285e422f609a5a` (origin/main's tip at 2026-10-25T00:18Z, `git rev-parse origin/main` after `git fetch origin main`). It is r1's head `b3dceb5cafc873698ab7e0967bfd624ff749b1ec`, plus `96149e328` (`git merge origin/main`, 511 commits, no conflict), plus `77ef64df9` (the shared grammar reader, the two self-test arms and the harness's A7, G1 and G2). Every figure below was re-taken at this head after the merge, except the live queue snapshot, which is marked with its own head.

## Mutation proof

`bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` (sha1 fb20409b971d9e4d808a75a205e7abf56820acca) plants 27 mutants, one rule each. It runs the owning self-test (`merge_train.py --self-test`, `orchestrator_tick.py --self-test` or `tick_loop.sh --self-test`) per mutant from a clean checkout and restores the file between runs. M0 at the head: `merge_train self-test: 267 checks, 0 failed; tick_loop self-test: 17 checks, 0 failed`. Every mutant failed at least one named arm. The arm(s) unique to each:

- G1, the merge pattern re-inlined in `Train.admit_verdict` instead of `proof_watch.parse_verdict`: "queue: the verdict grammar is proof_watch.parse_verdict's, not a copy -- a grammar swapped there admits #11 under it and leaves #11 under the old spelling". Under this mutant `agreement_py --run` also prints `RESULT divergent=0 unregistered=1`.
- G2, the merge pattern re-inlined in `Tick.verdict_levels`: "verdict grammar: null control: under the swapped grammar the old spelling is no merge verdict" (orchestrator_tick self-test, 1 of 214 failed). Under this mutant `agreement_py --run` also prints `unregistered=1`.
- A1 record-branch skip off: "the record pull request is left to --bot-prs (#16)"
- A2 no-tip refusal off: "no verdict/<pr> on the bus is left (#17)"
- A3 approver login check off: "a merge comment under another login is no verdict, though it carries the App's id (#19)"
- A4 approver id check off: "a merge comment under the App's login and another id is no verdict (#20)"
- A5 newest → oldest verdict: "a newest verdict that is blocked is left, though an older one was merge (#14)"
- A6 `bus:` line check off: "a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)"
- A7 a blocked verdict read as merge (`if got is None:` for `if got is None or got[0] != "merge":`): the #14 arm
- A8 carry refusal ignored: "a head the carry refuses is left, with the carry's own line (#13)"
- A9 carry asked at every head: "the carry is asked only where the verdict is not the head (#12, #13)"
- A10 order unsorted: "the fixture builds exactly #11 ..., #12 ... and #15 ..., oldest first"
- A11 failed list read as empty: "an unreadable pull request list stops the builder"
- A12 failed bus listing ignored: "an unreadable verdict bus listing stops the builder"
- P1 live-pidfile hold off: "a live train's pidfile holds the pitch -- no read, no queue, no train"
- P2 empty-queue stop off: "an empty queue starts no train and runs no pre-flight"
- P3 same-queue hold off: "the same queue at the same heads starts no second train"
- P4 pre-flight summary check off: "a pre-flight that prints no summary refuses, and no train starts"
- P5 `--pre-flight` dropped from PITCH_FLAGS: "a stale pidfile does not hold it; ... ONE train.sh with --bot-prs --approval-carry --pre-flight"
- P6 launch-failure refusal off: "a train.sh that exits before taking its pidfile is REFUSED ..."
- P7 a dead pid read as live: the stale-pidfile arm
- P8 ledger train-stop hold off: "an open train-stop in the ledger holds the pitch -- no read, no train"
- P9 `--once` read as always: "pitch without --once: a pitch every 3600 s (the hourly pitch) until stopped"
- P10 `--every` ignored: the same arm
- T1 pitch run without `--pitch`: "null control: without --pitch no pitch runs (the default loop starts no train)"
- T2 pitch step deleted: "--pitch: one pitch after the tick, its last line after the banner, ..."
- T3 hourly cadence off: "--pitch: the next pass inside the hour pitches nothing (the hourly pitch)"

The kill rule: a mutant is killed when its self-test's last line reports one or more failures and no crash line. The CI mutation lane does not cover `tools/`.

## Null control

- Agreement: at `96149e328` (r1's head merged with main, before the reader moved), `python3 -I tools/policy/agreement_py.py --run` prints `RESULT divergent=0 unregistered=2 dead=0 refused=0` and `AGREEMENT REFUSED`, with the two UNREGISTERED lines above. At the head it prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`.
- The two grammar arms pair a positive with a null. In merge_train, the swapped grammar admits #11 under the new spelling, and the same fixture under the old spelling leaves #11. In orchestrator_tick, the swapped grammar's spelling is MERGE-READY (#50), and the old spelling under the swap is not (#51). With the swap in place and the reader re-inlined (G1, G2), the arm fails. The swapped pattern is derived from the owner's (`.pattern.replace(" merge ", " MERGE ")`), never written out, so the test is not a second copy for agreement_py to count. A first draft wrote it out and agreement_py refused it as `unregistered=1`.
- Every arm that existed before the reader moved passes unchanged: merge_train's verdict arms (#11 to #20) and orchestrator_tick's ten verdict-level arms. The two pattern strings are byte-identical to r1's.
- At merge base 50af6174f, `python3 tools/audit/seat/merge_train.py queue -` refuses with `argument cmd: invalid choice: 'queue'`. Nothing wrote a queue (r1's control; the r1 delta is unchanged).
- In the self-test fixture, each LEFT arm has its admitted twin, which is the null control for that rule: #11 and #12 beside #13; #14 and #18 beside #11; #19 and #20 beside #11. A closed `train-stop` holds nothing, a new verdict at a moved head starts a train again, and a pass once the interval has passed pitches again.
- Without `--pitch` the tick loop runs no pitch. Its earlier self-test arms pass unchanged.

## Figures

- Agreement: `python3 -I tools/policy/agreement_py.py --run`, at the head: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`, `agreement_py restore: 18 closure file(s), 18 covered by the wave-script restore list, 0 missing`. At `96149e328`: `unregistered=2` (Null control).
- Self-tests at the head: `python3 tools/audit/seat/merge_train.py --self-test` (267 checks, 0 failed; 266 at `96149e328`, the difference being the new grammar arm), `python3 tools/audit/seat/orchestrator_tick.py --self-test` (214 checks, 0 failed; 212 at `96149e328`, the difference being the two grammar arms), `python3 tools/audit/seat/proof_watch.py --self-test` (40 checks, 0 failed), `bash tools/audit/seat/tick_loop.sh --self-test` (17 checks, 0 failed), `python3 -I tools/audit/seat/selftest_wiring.py --check` (96 self-testing, 96 wired, 0 unwired), `python3 tests/throwaway_git.py --check` (0 refused), `python3 -I tools/audit/seat/tmp_paths.py --check` (0 refused), `python3 -I tools/audit/seat/ref_privacy.py --self-test` (92 checks, 0 failed; the diff adds no push site).
- Mutants: 27 planted, 27 killed by a named arm, `bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` (kill rule under Mutation proof).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, and the two scripts are `tests/entities.py` and `tests/harness_headers.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` reports `2 of 2429 ENTITY CHECKS FAILED` at the head and also at merge base c6ef25a65. Its FAIL-line set, with each line's bracketed detail stripped and sorted, is identical at both ends (`diff base head && echo IDENTICAL` printed IDENTICAL). The two failures are the `hb:positive_control` py-spy checks, which this container cannot satisfy. `tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED. run_always: `tests/closure.py selftest` (ALL 117 closure shrink pins PASSED), `tests/layout.py` (ok), `tests/env_drift.py --claims-only c6ef25a65` (claims hygiene ok). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, wave-script or instrument red predicted against c6ef25a6534a`.
- Live queue, measured at r1's head `acdc10b22` at 2026-10-24T09:00Z and not re-taken: `python3 dev/audit/harnesses/r10_flow_autotrain_live.py <prs.json> <comments.json>`. This seat's `gh` token is refused, so the gh reads would again have to be answered from MCP reads, and a snapshot is stale the moment a verdict lands. At that time it queued #2683, #2688 and #2689, each with its verdict at its head, and left #2687 (the record PR) and #2678, #2690 and #2691 (no `verdict/<pr>`). The r2 delta moves the two patterns without changing them (byte-identical strings), and the #11 to #20 arms pin the admission outcome at the head.

## Architecture score

n/a: no file under `custom_components/` changes, so `tools/audit/archscore/` reads nothing this diff moves.

## Unpinned sites

none: the diff adds no production line. The CI mutation lane's scope is production code, and the 27 planted mutants above are this tool's own mutation proof.

## Red checks

- `tools/pr/prepr.sh`'s agreement lane, red at r1: `agreement_py --run` reported `unregistered=2` (above). The cheaper detector already exists: `agreement_py --run` takes about 2 s and runs inside prepr, which is where it was caught, before any pull request. r1's handoff ran the per-tool checks and `ci_predict.py` but not the full prepr. Now `agreement_py --run` reads `AGREEMENT ok` at this head, and a re-inlined copy fails a named self-test arm as well (G1, G2).
- `tests / nightly-status`, red on main's ancestry: it grades `main`'s nightly lane, not this head (`merge_train.py`'s default `--ignore-red`). This diff did not turn it red, and the detector that grades it is the nightly itself.
- `tests / ci-ratchet`, which may be red on main's push runs: GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix is in flight. That red is not this branch's, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

1. The roster's re-scope (tvofi 2026-10-24) is NOT built in this round: drop the timed pitch, build on R10-TRAIN-UPGRADE's `train.sh add` / `Train.admit_add`, add the event-driven dispatch call and the slow backstop. Reason: #2772 is open and draft at `c8219f601` (read through the GitHub MCP pull-request read at about 2026-10-25T00:15Z), not merged, and its own rework (`dispatch/fixer-r10-train-upgrade-r2`) is claimed and in progress. Reworking onto an `add` whose shape is still moving would build against code main does not hold. #2772's body already carries its seams to this group: `Train.admit_add` is the admission seam, `launch_detached` replaces `launch_train`, and `live_train` must read `queue.open`. The destination is this group's own roster carry, which already holds the re-scope. The orchestrator decides whether this head merges as the interim pitch or waits for #2772. Control: once #2772 merges, `grep -n "def pitch\|live_train\|launch_train" tools/audit/seat/merge_train.py` on the reworked head shows no timed pitch and no `launch_train`. Carry: R10-FLOW-AUTOTRAIN
2. nudge.md step 3 says to leave budget-file and policy-path heads out of the queue and direct-merge them (step 7). The pitch queues them for the batch's serial route instead, where `--pre-flight` parks a budget raise or policy head the owner has not approved at that head. Step 3's hand procedure now disagrees with the mechanism it describes. Control: diff nudge.md step 3 against `Train.admit_verdict` and `sweep_template.md` item (3); no contradiction remains. Carry: R10-POLICY-ROLE-PACK
3. R10-ORCH-MACHINERY hosts the pitch as the beat's pitch job: `merge_train.py pitch --once --state-dir <dir> [--mandate M]`, last line `PITCH HELD|EMPTY|STARTED|REFUSED`, rc 2 only on REFUSED. Nothing writes a `train-stop` yet, so the producer the beat adds must `ledger.py open train-stop <pr> <head>` on a `TRAIN STOPPED` line. The roster already carries this seam on R10-FLOW-AUTOTRAIN. Carry: R10-ORCH-MACHINERY

## Friction

- dev/governance/roles/fixer.md#3: cost: this seat's `gh` token is refused, so the live queue run cannot be re-taken at this head without answering its gh reads from MCP tools through a stub harness. The pitch's first real run, with `gh`, is the orchestrator-watched one the brief already owes. Carry: dismissed: the live pitch is orchestrator-watched by the brief, and a cloud seat's credentials are its environment
