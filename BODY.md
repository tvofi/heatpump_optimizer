R10-TRAIN-UPGRADE. The owner's ask (tvofi, 2026-10-24): "upgrade the train to allow both policy files and to sequence multiple batches on the same train, as well as loading more PRs on an already running train". This replaces the ad-hoc per-PR merge loops of proposal S6-V19. Triage P84 (`dev/programme/triage/s6-batch15.md#P84`, ACCEPT NARROWED, on `triage/s6-batch15`) is folded in as part 1. The coordinator's design input for `add`, items (a) to (d), is in part 3.

**Part 1: policy heads batch.** I measured this first. Policy heads are never routed serial: `merge_fastpath.file_class` has no policy class, so a policy head joins the batch. It is refused inside `Train.policy_gate`, the `raise Stop("policy", ...)` after `g.approval(...)`. Both `Train.admit` (batch admission) and `Train.land` (the merge) call it. The gate needs the owner's APPROVED review at exactly the head, citing the mandate id, and nothing in the train posted one. `approve` (step 6) posts only for app_approve's code-owned refusal, cites a free-text label, and runs after `land`'s `policy_gate`. The practice "policy heads stay off the train" therefore follows from a gap in the code, not a stale rule.

The fix is `Train.policy_approve`, which runs before `policy_gate` in both `admit` and `land`. It posts only when all of these hold:
- `--mandate` names exactly one comment id: a bare id, or a label from which `MANDATE_CITE` reads one id (`Train.mandate_id`).
- That mandate is in force now for policy merging, by `budget_raise_gate.mandate_state` with `MANDATE_COVERS_POLICY`.
- The head changes policy paths.
- The head changes no `*_budgets.json` file.
- No owner approval sits at the head yet.

The post goes out as the `gh` account and cites `mandate comment <id>`. The head is re-checked right before it. Its body comes from one writer, `_post_agent_approval`, which `approve`'s code-owned post now shares (that post's bytes are unchanged). `policy_gate` itself is unchanged and stays the only judge at the merge. Budget raises stay serial and stay the owner's (CLAUDE.md rule 2, 0013): `file_class` still routes every budget file serial, and the policy post refuses any head that touches one.

**Part 2: several batches on one train.** For `batch`, the queue file may be a list of non-empty lists of entries. `queue_batches` reads it, and a flat list stays one batch. The batches run in order, one `_batch` each, so each gets its own banner (`BATCH <tag>`, then `<tag>-b2`, and so on), admission, proof (`batch/<tag>-b2-<n>`) and merges. A completed batch logs `BATCH DONE`. A batch that stops ends the train: the later batches are logged `NOT RUN` before the closing `TRAIN STOPPED` line, which stays last. `run` refuses a nested queue.

**Part 3: loading PRs into a running train.** Design:
- **Queue format.** The queue file is unchanged, plus the nested form above. The spool `<state>/queue-add.jsonl` holds one JSON entry per line (`pr`, `verdict`, `verdict_comment`).
- **The lock.** `<state>/queue.lock` is taken with `fcntl.flock` in Python, never the `flock(1)` binary, which macOS lacks. Every reader and writer of the queue files takes it: `add`, and the train's open, drain and close.
- **How the live train re-reads.** `<state>/queue.open` holds the live train's pid. Between two batches, and never during one, `queue_take` drains the spool under the lock. The drained entries become one new batch after any still to run. An entry the train already holds is logged `ALREADY` and is not run twice. If the drain finds nothing and no batch is left, it removes `queue.open` in the same locked step, which closes the queue. An add therefore either lands in a drain or meets no open queue and starts its own train. No add is accepted and then never run.
- **An entry added while a batch is in proof.** It waits in the spool and runs as the next batch, with its own proof. A batch in proof is never mutated.
- **`add` (`train.sh add <pr> <verdict> --repo R --state-dir D [--verdict-comment ID] [flags]`, which calls `merge_train.py add`).** Under the lock, in order:
  - (c) A PR already in the live train's running or later batches (`queue.pending.json`, written by the train under the lock) or already in the spool is a no-op: `ALREADY`, rc 0.
  - (b) It runs `Train.admit_add`, a named seam that returns `<rule>: <why>` or None. The rules are `shape`, `open`, `base`, `carry` (the verdict at the head, or `app_approve.sh --carry` printing `CARRY: yes`), `row`, `budget-raise` (`raise_hold`: admitted only when the owner's approval is held, and the batch still routes it serial) and `policy` (an owner approval at the head, or a `--mandate` id that `policy_approve` can post under).
  - (d) A refusal prints `ADD REFUSED #<pr> <rule>: <why>`, rc 1.
  - With a live train, the entry goes to the spool: `ADDED`.
  - (a) With no live train, it starts train.sh detached over the entry, plus anything a stopped train left in the spool. It holds the lock until train.sh owns `train.pid`, so a concurrent add finds that train live and spools instead. If a train.sh still holds `train.pid` while no queue is open (it is closing), `add` waits that pid out and otherwise refuses (`one-train`, rc 2). It never starts a train beside it.
- **One train per state dir.** train.sh's pidfile still refuses a second train.sh. `Train.queue_open` also refuses a `batch` while `queue.open` names another live process. The two pids it accepts are its own and its parent's: the train.sh that `add` started.

Rejected alternatives and their failure modes:
- **Re-reading the queue file itself between batches.** It needs a writer that rewrites a file the train is reading, so a partial write races the read. And "which entries are new" becomes a diff against a moving file.
- **A second merge lane per added PR, or parallel shell loops.** That is the per-PR loop this replaces: the S6-V19 defects (an empty head variable, a garbled PID line, a hand-corrected rerun rule) and no shared hold or proof.
- **Joining an added entry to the batch in proof.** That mutates a proved set, so the proof no longer grades the tree that merges.
- **Setting a crashed train's spool aside.** That drops accepted work. The next train runs those entries instead, and its admission re-reads every one.
- **The shell's `flock(1)`.** It is absent on macOS.
- **An `add` that refuses when no train is live.** Superseded by the coordinator's item (a).

**Carried in: triage P86** (`dev/programme/triage/s6-batch17.md#P86`, on PR #2761). Every train merge was refused twice. Each approval starts a `CI review pr=<n>` run of ci.yml (`pull_request_review`, 66 to 76 s in runs 40124449022, 40129950489 and 40130190054), and base-branch policy refuses the merge until that run concludes. `land` slept 30 s before every attempt, and app_approve.sh posts on every call. The changes:
1. A batch entry is approved at admission (`#<pr> approved at admission`), before its proof is pushed, so its review run is over while the proof and the earlier merges run.
2. `Train.approve` posts no second approval at a head this train already approved (`Train.approved`), or that `hpo-approver[bot]` has already APPROVED on GitHub. A head that moved is approved afresh.
3. `land`'s first attempt waits in `review_settle` instead of a blind 30 s. It sleeps one `REVIEW_POLL_SECONDS` (5 s) grain, then polls `actions/runs?event=pull_request_review&head_sha=<h>` while a run there is unfinished, up to `polls` times. An unreadable listing is not a wait. Later attempts keep the 30-s grain.

The serial `run` path still approves inside `land`. That path is P86's null. Approving at admission also approves an entry the proof later drops to serial: the approval sits at its admitted head, and the recarry's new head is approved afresh.

Not built here (R10-FLOW-AUTOTRAIN's): the backstop sweep, the dispatch wiring, and any change to its unmerged `pitch`.

## Head

b1cba1acab22009ca5eb2de99237d8f421d05dca

## Mutation proof

`python3 dev/audit/harnesses/r10_train_upgrade_mutants.py` applies one mutant per new arm to `tools/audit/seat/merge_train.py`, each a copy that runs `--self-test`. A span that does not occur exactly once is reported STALE. Result: `MUTANTS: 28 run, 0 not as required`. M0, the unmutated head, PASS. M1 to M27 are all KILLED. The checks each mutant fails:
- M1, `land` no longer posts the policy approval: `policy post: a policy head with no owner approval at it, under --mandate <id> in force ...`
- M2, admission no longer posts it: `batch policy post: under --mandate <id> in force, a policy head is approved at admission ...`
- M3, the in-force check dropped: `policy post null: a mandate out of its window posts nothing ...` and `... scoped code-owned ...`
- M4, the budget exclusion dropped: `policy post null: a budget file beside the policy ...`. That run also reddened `a TERMed train exits 143 ...` (R10-PUSHER-REAP). This is a timing check under four parallel self-tests; M0 and the serial runs pass it.
- M5, an existing approval re-posted: `policy post: an owner approval already at the head is not re-posted` and the batch policy arm.
- M6, `mandate_id` reads no label: `mandate_id: a bare id and a label citing exactly one are read ...`
- M7, only the first batch runs: both `several batches:` arms.
- M8, no NOT RUN lines: `several batches: a batch that stops ends the train ...`
- M9, a duplicate accepted: `queue_batches refuses a pull request in two batches ...`
- M10, the spool not drained, and M11, no dedupe at the drain: `live queue: entries added while a batch is in proof never join it ...`
- M12, a second train allowed: `one train per state dir: ...`
- M13, add not idempotent: `add is idempotent: ...`
- M14, no admission: `add refused: the admission's rule is printed ...`
- M15, add without the lock: `RACE: two concurrent adds with no train live start exactly ONE train ...`
- M16, no wait on a closing train.sh: `add beside a train.sh still holding train.pid ...`
- M17 to M23, each `admit_add` rule dropped: the matching `admit_add refuses by its <rule> rule` arm, and for carry also `add refused: ...`
- M24, a second approval at a head this train approved: `P86: in a batch of two, each entry is approved ONCE, at admission ...`, `P86: a [MAIN-MOVED] re-prove at unchanged heads approves nothing again ...`, `on main: entries are approved ONCE ...` and `batch mandate: ...`
- M25, a second approval at a head the approver App approved: `P86: an approver App approval already at the head is not posted again ...`
- M26, no approval at admission: `P86: in a batch of two ...` and `on main: entries are approved ONCE ...`
- M27, the blind 30-s grain back in place of the review wait: `batch null control: ...`, `PERTURBATION: ...` and other batch arms. The test world refuses a merge while the head's review run has not been read as concluded, as base-branch policy does.

`tools/audit/seat/train.sh --self-test` arm 11 pins `add`'s argv shape, the absent pidfile and the `--queue` refusal.

## Null control

- **A one-batch queue behaves as before.** Every one of main's own self-test arms passes unchanged on this head. Among them are the batch arms asserting `lines[-1] == "TRAIN DONE"`, the `SKIP REPORT` lines and the stop lines. The new arm `live queue NULL CONTROL` runs the same two-entry queue flat and nested (`[[...]]`) with nothing spooled. It asserts identical log lines and identical call argv, with shas normalized because each world commits afresh, and no queue line (`BATCH DONE`, `ADDED`, `ALREADY`, `NOT RUN`, `ADD`) in either.
- **No mandate posts nothing.** The `policy post null:` arms cover five cases: no `--mandate`, a label with no id, an out-of-window mandate, a mandate whose scope does not cover policy merging, and a budget file beside the policy. Each posts nothing and stops with today's `policy:` refusal (`no decisive review`). The batch arm without `--mandate` stops at admission as before.
- **A non-policy head posts nothing**, and an owner approval already at the head is not re-posted.
- **P86 null.** An approver approval at another head (the head moved) is no approval of this one, and app_approve.sh approves afresh. With no review run pending, the first attempt waits one 5-s grain and merges, with no refused attempt.
- **The code-owned approval body is byte-identical.** The shared writer keeps its text. Main's arm that reads `approve7.md` passes unchanged.

## Figures

- merge_train self-test at this head: `python3 tools/audit/seat/merge_train.py --self-test`, last line `merge_train self-test: 283 checks, 0 failed`. Main's arms are a subset, all unchanged.
- train.sh self-test: `bash tools/audit/seat/train.sh --self-test` prints `train.sh self-test: ok (...)`. It needs the seat venv's python3 first on PATH: under the shim PATH, arm 9 symlinks the `seat-python3` shim, which re-resolves to itself under the arm's `HPO_STATE_DIR`. Main's train.sh fails arm 9 identically on this host, so this is host-only and pre-existing.
- Mutants: `python3 dev/audit/harnesses/r10_train_upgrade_mutants.py` prints `MUTANTS: 28 run, 0 not as required`. The rule is one mutant per new arm, listed by `--list`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, which names `tests/entities.py`. On this macOS host it prints `4 of 2425 ENTITY CHECKS FAILED`, all four `hb:` py-spy positive-control retry checks (`the control rests between tries`, `... survives two hung samples ...`, `... survives one hung py-spy sample ...`, `a try whose sample misses the spin ... is retried`). The diff touches none of their closure (`tests/entities.py`, `tests/nightly_ha.py`). Null control: the same command in a detached worktree at origin/main c176ee55de7c on this host prints `4 of 2425 ENTITY CHECKS FAILED`, with the same four checks. So these failures are this host's and predate the diff. CI's Linux run is the authority.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- R10-FLOW-AUTOTRAIN (handoff `b3dceb5ca`, unmerged; the coordinator was told before this push and sequences AUTOTRAIN after this group):
  - Its queue builder has no policy exclusion at that head, so P84's "lift the exclusion" has nothing to lift.
  - `Train.admit_add` is the admission seam its builder extends.
  - `launch_detached` replaces its own `launch_train`.
  - Its `live_train` must read `queue.open` as well as `train.pid`.
  - Carry: R10-FLOW-AUTOTRAIN (its group in dev/programme/rosters/wave-r10-groups.json).

## Friction

none
