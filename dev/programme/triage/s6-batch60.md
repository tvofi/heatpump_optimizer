# Proposal triage, session s7, batch 60 (P278-P283)

The rolling batch (V182) after batch 59 (#2945, merged as
`66974d47312caa46e9817b9aeae7186e9764e560`). Facts were read at that origin/main.

## P278: retry a roster push refused as non-fast-forward

Verdict: ACCEPT, narrowed to R10-ORCH-ROSTER-SCHEMA: the lint-gate refusal's last line names its
cause. The proposed retry is REJECTED, because the tree already has it and these refusals were not
races.

Source: the orchestrator's triage-queue line of 2026-10-29T10:24:00Z. Two `append-group
R10-FLY-OWED-LEVELS` ops were refused with `rc=3 'the commit is local ... nothing pushed'`, at
09:15:52Z and 09:26:09Z (`roster-blocked.txt`). The proposal reads both as lost races to
`roster_sync.py`'s beat pushes, and the fly-in fixer's dispatch was delayed by more than an hour.

Instances:
- **rc 3 is the lint gate, not a push.** In `tools/audit/seat/roster_edit.py`, the only print of
  "the commit is local ... nothing pushed" follows "LINT GATE REFUSED the push" (`:657-660`), and
  it returns before any push is tried. A lost race has its own path, "lost a race: origin/... moved"
  (`:682`), which re-fetches, re-applies and re-lints up to `PUSH_ATTEMPTS = 3` times (`:137`,
  `:631`). It refuses with rc 2, never rc 3.
- **The retry already exists one level up as well.** `roster_queue.py` re-fetches its lint clone
  and retries up to four times on a stale lint checkout (`MOVED`, `:42`) or on a lost race whose
  lint was clean (`:122`, `:137`).
- **Reproduced, with no rival.** `roster_edit.py append-group R10-FLY-OWED-LEVELS <json>
  --lint-cwd <origin/main checkout>` was run without `--push` on a scratch worktree, at roster tip
  `68406609a`. brief_lint printed `TOTAL: 2 error(s)`. Both are in the group's own brief:
  "none of [owed_unactioned] found near tools/audit/seat/orchestrator_tick.py:690" and "none of
  [orchestrator_tick] found near tools/audit/seat/owed_unactioned.py:50". The cause is that one
  sentence cited both files. The linter reads each citation's anchors from its clause, bounded
  only by `.` or `;` (`tools/policy/brief_lint.mjs`, `clauseWindow`, `:391`, called at `:591`). So
  each file was searched for the other file's name. The roster at the same tip without the group
  lints clean. Every retry would have refused again, so a retry on rc 3 would have bought nothing.
- **Why it read as a race.** The roster loop records only the last output line that matches
  `pushed|REFUSED|error` (`roster-loop.sh`, `res=`, line 49). That line is "... nothing pushed".
  The `TOTAL: 2 error(s)` line and the two errors above it are dropped. The 09:24Z re-queue note
  reported "brief_lint clean" and "likely push race", and the 10:24Z note reported "non-ff
  refusal". Neither is what the gate printed.
- **The authoring defect is this seat's.** The brief was written by P277 (batch 59). It was queued
  without a dry run of the op it feeds. The group JSON is now corrected: the two citations are
  split into separate sentences. The same dry run prints `lint gate: TOTAL: 0 error(s)`, and
  nothing was pushed. Queue line 291, already re-queued, now lands on the loop's next pass.

Accepted (narrowed), carried to R10-ORCH-ROSTER-SCHEMA (carries open; `roster_edit.py` is in its
files):
1. The lint-gate refusal in `roster_edit.py` ends with one line that carries the cause, the count
   and the outcome together, for example `roster_edit: LINT GATE REFUSED: 2 error(s); the commit
   is local at <sha12> in <wt> (detached); nothing pushed`. The detail lines still print above it.
   Any caller that keeps only a last line, or only a last line matching `REFUSED` or `pushed`,
   then records the cause. rc stays 3.
2. Self-test: a fixture roster whose brief cites a symbol its file lacks. The last stderr line
   holds both `LINT GATE REFUSED` and `nothing pushed`. Mutation: the old two-line form fails the
   arm. Null control: a clean fixture still prints `lint gate: TOTAL: 0 error(s)` and pushes.

Rejected: the retry as proposed. It exists twice already (`PUSH_ATTEMPTS`, `roster_queue.py`).
Extending it to rc 3 would re-run a deterministic lint failure up to the bound and then refuse
with the same hidden cause, only later.

Not a tree change: this seat now dry-runs every `append-group` and `append-carry` it queues
through `roster_edit.py` without `--push`, from a fresh origin/main lint checkout, and queues only
on `TOTAL: 0 error(s)`. It costs seconds a ruling.

Cost: about 3 lines of message in `roster_edit.py` plus one self-test arm, in a group already open
on the file. No CI, no new file and no change to rc or behaviour.

Binding: two refusals, two misdiagnoses written into the queue, and a fly-in held for more than
an hour on one cause. The countermeasure makes that cause visible on the one line the callers
keep, and the retry it replaces would not have helped.

## P279: the tick should owe a PR the merge train PARKed

Verdict: ACCEPT, in two parts. Item 1 amends P265's owed-PR buckets in R10-ORCH-LEDGER. Item 2 is
a defect the measurement found, a new fly-in, R10-FLY-TICK-TRAIN-RC. The proposal's own
mechanism, a separate tick line, is not built.

Source: the orchestrator's triage-queue line of 2026-10-29T11:08:00Z. #2933 and #2939 were PARKed
at 10:46Z and 10:58Z on unrouted review items. The sweep printed `TRAIN_RC=1` as a status line,
not as owed, and nobody saw it for about 30 minutes, until the owner asked.

Instances:
- **What the tick showed.** The live tick runs with `--train-log` at the train's state-dir
  `train.log`. Its TRAIN section printed `log tail: ... SKIP REPORT: 2 skipped of 2 | ... |
  TRAIN_RC=1 end=2026-10-29T10:58:00Z`, unflagged. Its PRS section printed `MERGE-READY: #2933
  33b128eb` and `MERGE-READY: #2939 000eae09` for the same two PRs. Neither line is in
  `owed_unactioned.py`'s family today.
- **Where a PARK is written.** `merge_train.py`'s pre-flight logs `PARK #<pr> <step>: <why>`,
  leaves the entry out and writes `skipped.json` (`preflight`, `:1977`). The live log holds 6
  PARKs since 2026-10-27: 4 `findings` and 2 `policy`. Nothing in the tree reads a PARK line back.
- **The bucket gap.** P265's carry on R10-ORCH-LEDGER gives each open PR one bucket. A PR
  "queued at a verdict that is the head" is `train`, so a PARKed PR, which is still queued at its
  verdicted head, would be bucketed `train` and owe nothing.
- **A dead flag, found on the way.** The tick's "last train exited N" flag reads
  `Path(train_log).with_suffix(".rc")` (`orchestrator_tick.py:536`). `train.sh` writes the status
  as `$state/rc` and as the log line `TRAIN_RC=<n> end=<ts>` (`train.sh:396`), never as
  `train.rc`. Of the 23 runs the live log records, 16 ended `TRAIN_RC=1` and none was flagged. The
  self-test passes because its fixture writes `train.rc`, the reader's own name, beside its log
  (`:2420`).

Accepted:
1. Carried to R10-ORCH-LEDGER, amending P265. An open PR that the latest train run PARKed (the
   `PARK #N` lines after the log's last `STARTED`) is bucket `owed`, reason `train-parked <step>:
   <why>`, never `train`. It is keyed (train-parked, PR, head) in the obligations ledger, and a
   moved head closes it. It reads only the train log the pass already reads, with no GitHub call.
   Controls: a 10:58Z-shaped fixture gives one owed line per PARK; null: a PARK before the last
   `STARTED` gives none; mutant: dropping the arm leaves the fixture in `train`.
2. New fly-in R10-FLY-TICK-TRAIN-RC (size S, `orchestrator_tick.py`). The tick reads the status
   from the log's last `TRAIN_RC=` line, falling back to `rc` in the log's directory. The fixture
   uses `train.sh`'s names. Mutation: the `.rc` suffix read leaves it unflagged. Null control: a
   log ending `TRAIN_RC=0` flags nothing.

Not built: a separate `OWED train-parked` tick line outside the ledger. R10-ORCH-LEDGER's design
replaces the tick's own OWED scans with the ledger, and a second producer of owed-PR lines would
be the double-bucket that P265 rules out. Meanwhile R10-FLY-OWED-LEVELS (P277), on the roster
since 10:28Z and dispatchable, makes those PRs' `MERGE-READY` lines owed after two sweeps, so
the interim gap closes without the reason text.

Cost: item 1 is one bucket arm and a fixture in a group already carrying P265. Item 2 is about 5
lines and a corrected fixture.

Binding: 6 PARKs in 3 days, each unseen until someone read the log, and a flag silent on 16 of
23 nonzero exits.

## P280: the tick should report a cloud seat whose run ended without pushing

Verdict: REJECT. The tick cannot read what the proposal needs, and its measured instance is
already owed under P277.

Source: the orchestrator's triage-queue line of 2026-10-29T11:08:00Z. #2872's cloud fixer ended
at 08:57Z on a ref_privacy refusal (`HOME=/root` matching a path in `root-cause.md`). It sat
about 2 h while `BLOCKED-UNFIXED` printed every tick.

Instances:
- **The read is not available to the tick.** The proposal keys on RemoteTrigger's
  `get_run_log`. That is a call of the orchestrator's session. No file in the tree reads a cloud
  run log: `cloud_dispatch.py` writes `cloud-sessions.tsv` (494 rows) and never reads a run back.
  Building it means a new API client in the tick, for one signal.
- **The instance is a blocked PR at an unmoved head.** That is exactly P277's
  `BLOCKED-UNFIXED: #2872 <head8>`, which R10-FLY-OWED-LEVELS makes owed and keys per head. With
  it, #2872 stands UNACTIONED after two sweeps (about 10 minutes), not 2 hours. A head that
  moves re-raises it.
- **The no-PR case has no instance here.** Work-based liveness already exists in the tick's
  WORKERS section (head unchanged, no new CI, or no PR past `--stall-hours`). The live tick
  passes no workers file, so that section is unwired, not missing.

Rejected: the per-session liveness line. Its one instance is covered by an S fly-in that can be
dispatched now. Its mechanism needs a session API the tick does not have, and it would judge
liveness from the session, where the WORKERS section judges it from the work.

## P281: the live tick's queue is a hand-kept link, and its workers file is unwired

Verdict: ACCEPT, narrowed to the queue read, folded into R10-FLY-TICK-TRAIN-RC (P279). The tick
takes the queue path from the train's own start line. The stable link the proposal asks
`train.sh` to keep is REJECTED, and so is wiring `--workers-file` while nothing writes one.

Source: the orchestrator's triage-queue line of 2026-10-29T11:15:08Z. The live tick's `--queue`,
`train/current-queue.json`, is a symlink kept by hand. It named
`add-queue-20261027-022550-2867.json` for two days, so every pass printed "stale queue entries
... #2867". The proposal offers two fixes: `train.sh` keeps a stable link, or the tick reads the
live pid's queue. It also asks to wire `--workers-file`.

Instances:
- **The writer already records the path.** `merge_train.py`'s add writes a fresh
  `add-queue-<ts>-<pr>.json` per run and starts `train.sh --queue <it>`. `train.sh` logs `train.sh:
  queue=<path> ... pid=<n>` at the start of every run (`train.sh:378`). The live log holds 27 such
  lines, and its last two name `add-queue-20261029-105739-2933.json` and `...-110724-2933.json`.
  The tick already reads that log (`--train-log`).
- **A link would be a second record of the same fact.** It would be kept by a different writer,
  and the add, sweep and spool paths would each have to keep it right. That is the class that just
  went stale.
- **The workers file has no writer.** The WORKERS section reads `seat, pr, head, dispatched_at,
  agent_kind` (`orchestrator_tick.py`, `--workers-file`). No other file in `tools/audit/seat/`
  writes or names one: not `cloud_dispatch.py`, not `bus.sh`. Wiring the flag would point the
  reader at a file nothing produces, so the section would still be empty. Its target cases are
  owed elsewhere: a blocked PR at an unmoved head under P277, and a live roster stage with no ref
  under R10-ORCH-LEDGER's `IN-PROGRESS NO LIVE REF` carry.

Accepted (narrowed), folded into R10-FLY-TICK-TRAIN-RC as item 3. With `--train-log` given and no
`--queue`, the tick's `_queue` reads the path from the log's last `train.sh: queue=` line. An
explicit `--queue` still wins, and an absent named file is UNREADABLE as today. Self-test: a
fixture log with two start lines reads the second. Mutation: reading the first fails. Null
control: an explicit `--queue` is used unchanged.

Rejected: the stable link, as a second record. Also rejected: `--workers-file` wiring without a
writer. A writer in `cloud_dispatch.py` would be a new proposal with its own instance, and none is
measured here.

Not a tree change: until the fly-in lands, the live tick's `--queue` should be dropped or
re-pointed. That is the orchestrator's live wiring, not a ruling.

Cost: about 6 lines in the same section and fixture as P279 item 2, which stays size S.

Binding: two days of a false stale line on every pass, from a link no tool kept, fixed by reading
the record the train already writes.

## P282: the review packet owes main-graded reds an answer

Verdict: ACCEPT, reframed, as a new fly-in, R10-FLY-PACKET-RED-PATHS. The exemption already
exists. The packet does not give it the inputs it decides on. The exemption list the proposal
would add to `review_packet.py` is REJECTED as a second copy.

Source: the orchestrator's triage-queue line of 2026-10-29T11:46:16Z. #2933, #2946, #2948 and
#2925 each had dispatch refused on `tests / nightly-status`. Each needed an orchestrator
`body_patch`, and each patch re-triggered pr-contract and the gate (about 10 minutes).

Instances:
- **The rule.** `defect-root-cause.md` says `tests / nightly-status` and `governance /
  delivery-status` grade `main`, so a body owes them no answer unless its diff touches what they
  read.
- **The rule is implemented once.** `policy_lint.mjs --pr-body` exempts both reporters, but only
  when it is given the changed paths. With no `--paths-file` the obligation is restored on
  purpose: its self-test's `no paths` case (`policy_lint.mjs:4447`). `prepr.sh` passes
  `--paths-file` and `--existing-file` (`body_check`, `:858-863`), and states that the exemption
  is "deliberately NOT copied" anywhere else (`:1239`).
- **The packet omits the inputs.** `review_packet.py` calls `policy_lint.mjs --pr-body {BODY}
  --head <head> --red <name>...` with no paths (`:331`), although the same function computes
  the diff's paths as `touched` (`:321`). So every concluded nightly-status red reads as
  red-unanswered.
- **Reproduced.** The batch-59 body was linted with `--red 'tests / nightly-status' --red
  typing`. With no paths, both are reported unanswered. With a `--paths-file` naming one triage
  file and an empty `--existing-file`, only `typing` is reported. The null control holds: the
  check still bites on a red that is not main-graded.

Accepted: the packet passes `touched` as `--paths-file` and the base's existing paths as
`--existing-file`, plus `--base`, as `prepr.sh` does. Self-test: reds nightly-status and typing
over a test-only diff report typing alone. Mutation: dropping `--paths-file` reports both. Null
control: a diff touching `tests/nightly_status.py` reports both.

Rejected: an exemption list in `review_packet.py`. It would be the second implementation that
`prepr.sh`'s comment refuses, and it would drift from `policy_lint.mjs`'s voiding routes (an own
row edited, a reporter's script, no existing list).

Placement: a fly-in, not a carry on R10-ORCH-REVIEW-PACKET. That group's open work is #2939
(parked, a different function in the same file), and a carry would wait behind it. The brief
names the overlap.

Cost: about 10 lines and one self-test arm in one file.

Binding: four dispatch refusals in one day, each needing a hand body patch and a re-triggered
gate, from a call that drops two arguments its own function already has.

## P283: the pushers' STALE CHECKOUT guard refuses from a current worktree

Verdict: ACCEPT, narrowed, as a new fly-in, R10-FLY-RELAY-TOOLS-LEVEL. The relay runs
`update_pr.sh` from a tools checkout it keeps level. Both options as proposed are REJECTED:
(a) is already the behaviour, and (b) would make the guard move the checkout it is running from.

Source: the orchestrator's triage-queue line of 2026-10-29T12:00:46Z. It says the guard judges
the main checkout even when invoked from the orchestrator worktree, "whose tools are current".
It refused three times today (11:00Z open #2948, about 11:20Z #2925, 11:52Z #2939), each needing
a checkout bump or `HPO_ALLOW_STALE_TOOLS=1`.

Instances:
- **The guard judges the running script's checkout.** `pr_tools_fresh` (`pr_args.sh:166-178`)
  resolves `dirname "${BASH_SOURCE[0]}"` and counts what origin/main adds under
  `tools/audit/seat` and `tools/pr`. That is option (a), already in the tree.
- **The record names only the orchestrator worktree.** Of the `STALE CHECKOUT` refusals in
  `tick-loop.log` and `cloud-relay.log`, all 41 name the orchestrator worktree's
  `tools/audit/seat`, and none names the main checkout. It was behind when they fired: for
  example 3 commits behind `9df0fe679` and 13 behind `53c4b9cb0`. The premise "whose tools are
  current" did not hold at those moments.
- **Nothing levels that worktree.** The relay calls `bash "$HERE/update_pr.sh"`, with `HERE` its
  own directory (`cloud_relay.sh:154`, `:438`). Since 2026-10-29T00:00Z, 9 of main's 23
  first-parent commits (to `b87019b86`) change the guarded paths. So each tools merge refuses the next relayed
  update until a hand bump: 13 relay refusals (10 on 2026-10-28, 3 on 2026-10-29).
- **Why (b) is unsafe.** A guard that fast-forwards its own checkout changes the files of the
  bash scripts running from it. bash reads a script from its file as it executes, and the relay
  is one of those scripts.

Accepted (narrowed): the relay runs `update_pr.sh` from a tools checkout it owns, never from the
checkout its own loop executes. It is a worktree added once and detached. Before each update
call it is fetched and checked out at origin/main when clean, and a dirty or busy one is a named
refusal. This is the pattern `roster_queue.py` uses for its lint clone. Self-test: with the
scratch origin's main one tools commit ahead, the relayed update passes the guard. Mutation:
calling `$HERE/update_pr.sh` again gives the refusal. Null control: a dirty clone is refused by
name and left untouched.

Rejected: (a), which is the present behaviour, and (b), a self-moving guard. The guard stays as
is: it caught a real staleness 41 times. The orchestrator's own manual `open_pr.sh` and
`update_pr.sh` runs level their checkout first. That is practice, not a tree change.

Cost: about 15 lines in `cloud_relay.sh` and one self-test arm. No change to the guard.

Binding: 13 relayed updates refused in two days, plus the three manual refusals named, from a
checkout that no caller keeps level.
