#3885 L3 (design/r11-ci-3885-queue §4 W1 + W2). No runner is held now while another run's work finishes.

- W1: a prelude that would have waited on another run's sources fails at once, on ci.yml's step `Defer: sources still running`. `prelude.busy_sources` makes one runs listing and never sleeps. `sweep.py`'s `Sweep.undefer` re-runs the deferred run's failed jobs once no source at the head is busy. A stale pin gets one `STALE-PIN` dispatch instead.
- W2: the sweep of a green, newest-covering run no longer polls another run's unfinished gate, and `settle` skips on one. That run's own completion sweeps it. Its completion arm, `Sweep.completion`, re-runs its red gate where another run's green gate covers the newest event, within `settled` and `ATTEMPT_CAP`. The arm needs that green gate to have completed before the red one did; a green gate that completed later belongs to its own run's sweep.

The branch is stacked on L4: the L4 commit 77f41cbb0d is its first commit, and #3885 L4's own pull request carries it. Carry 2 of `dev/programme/carries/carry-3885.json` rides here, as commit a036a9ad20. Leaves #3885 open. Carry: #3885

## Head

88bfe8ce5b3198456142e8bbfeec116494532e3c, on L4's head 77f41cbb0d, cut from origin/main 8890fc2bada17f6c7d8a6bbf03e6625a16a0967c. origin/main was at d380053b01 at 2026-11-27T04:03:55Z, and `git merge-tree --write-tree origin/main HEAD` was not re-run against it (the train re-proves the head).

## Mutation proof

Each mutant was applied at the head. The named self-test was then run, and the file restored. After restoring: `sweep self-test: 145 checks, 0 failed`, `prelude self-test: 162 checks, 0 failed`, `gate self-test: 133 checks, 0 failed`.

- W1 M1: `self.undefer(runs, head)` replaced by `pass` in `Sweep.run`. Result `sweep 145 checks, 5 failed`: the four W1 re-run rows (decider green, decider still busy, the deferred run's own completion, decider cancelled) and `W1 stale pin null`.
- W1 M2: `out["defer"]` always `''` in `prelude.outputs`. Result `prelude 162 checks, 4 failed`: three C3 rows and `#3885 null control, W1`.
- W2 M1: `Sweep.completion` never fires (`if not green` made `if True`). Result `sweep 145 checks, 8 failed`: the six `W2: ... left unpolled, and its own completion re-runs it red` rows (HIGHER-id, then queued, waiting, pending, requested, in_progress), `W2 completion arm`, and `W2 completion arm null` (the bot's re-run).
- W2 M2: `self_swept` always `False`. The self-test raises (`min() iterable argument is empty`) at `polls are >= 60 s apart`: the bot-actor poll rows lose their sleeps.
- W2 M3: `self_swept` always `True`. Result `sweep 145 checks, 8 failed`: the six `W2 ... left unpolled` rows, `sweep-self null, W2`, and `settle, W2`.
- W2 M4: the arm's ordering clause (`completed_at < done`) dropped. Result `sweep 145 checks, 2 failed`: `a lower green gate that started after the higher red concluded: settle from run 2 re-runs nothing` and `#3544: gate-sweep run 43573334631, R1's settle`.
- W2 M5: the arm ignores `settled`. Result `sweep 145 checks, 3 failed`: `W2 completion arm null` and two `census: the second round posts nothing` rows (lower success, higher created 45).

prepr ran with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, as the dispatch brief directs, so it drew no `diff mutants`. The hand mutants above prove each added predicate.

## Null control

- W2 companion: the probe drives the same worlds through each tree's own `tools/ci/sweep.py`, built from `tools/ci/sweep_selftest.py`'s helpers at the head. Held seconds are the summed `sleep` calls. Where the first sweep posts nothing, the left run is finished red and its own completion's sweep is driven too. The probe is in scratch only, sha1 6b4b1e04c8855550e5c804912dbef2e9e29bbe0a. Command: `python3 -I probe.py <tree's tools/ci> tools/ci`.
  - Base 8890fc2bad:
    - green sweep, other gate in_progress, red after 3 polls: held 180 s, posts `jobs/10/rerun`
    - same, never finishing within the bound: held 600 s, posts nothing (left red)
    - settle, decider gate in_progress, red after 1 poll: held 60 s, posts `jobs/10/rerun`
    - null, a bot-actor gate in_progress, red after 3 polls: held 180 s, posts `jobs/10/rerun`
  - Head 88bfe8ce5b, same four rows: held 0 s, 0 s, 0 s, then 180 s for the null. Every row posts `jobs/10/rerun`. The never-finishing row posts once the run completes, which is what a run does whether or not anyone polls it.
  - The null row reads the same at both ends, as it should: a bot-actor run keeps its poll.
- Self-test nulls beside each W2 row: `W2 completion arm null: a green gate that does not cover the newest event re-runs nothing`, `W2 completion arm null: the bot's re-run of it, red again after every source finished, is left (no loop)`, `W2: a left run that completes green is not re-run by its own sweep`, and `W2: a push that moved the head before the left run completed: its own sweep re-runs nothing`.

## Figures

- `python3 tools/ci/sweep.py --self-test`: 145 checks, 0 failed. `python3 tools/ci/prelude.py --self-test`: 162 checks, 0 failed. `python3 tools/ci/gate.py --self-test`: 133 checks, 0 failed. All at the head.
- The W2 row conversions use the design's rule, "the existing poll rows become completion rows, with the same POST set". Each base row that polled an unfinished gate is kept as a bot-actor row (`bot()`), and gains a non-bot completion row (`own_completion`) that asserts no sleep and the same POST:
  - `HIGHER-id gate still waiting`
  - the five `NOT_COMPLETED` states
  - `push that moved the head`
  - `polled run that completes green`
  - `sweep-self null: the workflow_run sweep polls that gate as before`
  - `settle: a gate still running is polled`
  
  The rows that poll on spacing and the bound (`polls are >= 60 s apart`, `the bound is reached by polling`) now use a bot-actor run. Rows that poll a gate completed in a run still running are unchanged.
- Two fixture changes make a recorded world match GitHub:
  - `shape3400`'s dispatched run gets the bot actor. It is a github.token dispatch, and its `sweep-self` unit runs only under `github.actor == 'github-actions[bot]'`.
  - The census's second round sets `triggering_actor` to the bot. The sweep posts that re-run, and `settled` reads that field.
- Gate scope (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: FULL`, because `.github/workflows/ci.yml` changes the gate. That is W1's `Defer: sources still running` step, plus the prelude's `timeout-minutes` dropping from 150 to 30.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- Finder's harness `dev/audit/harnesses/ci3885_queue.py` was not re-run. Its `fetch` needs `gh api`, which this container lacks, and its after-merge reading cannot exist before the merge. The reviewer re-runs it locally. The companion under `## Null control` applies each tree's own rule to the same inputs.
- Not taken:
  - W1's per-poll API seconds (design §4, the W1 API-vs-sleep row). The head makes one listing and has no sleep, so the replaced loop's API share was not printed.
  - W3's conditional cap (`GATE_WAIT_MAX_S` to `GATE_ABSENT_MAX_S`). `gate.lag_bound` applies `GATE_WAIT_MAX_S` only where every reason is this run's own jobs listed pending (`OWN_PENDING`), which is no source wait. The design's W3 row measured one such job at over 5 min, so a 120 s cap would turn it red. It is carried below.

## Red checks

none

## Forward-carry

- Departure from design §4 W2 ("the polled run's own completion then does what the poll did"): a run whose actor is the bot (`sweep.self_swept`) keeps the poll, in the green branch and in `settle`. gate-sweep.yml's `workflow_run` never fires for that run, and its sweep-self runs inside it, where GitHub refuses a re-run of its own gate. So no completion of its own can re-run it. A gate completed in a run still running is still polled too, for its own sweep-self's seconds. The orchestrator rules whether this stands. Carry: #3885
- Residue of the completion arm's ordering clause: a green sweep whose jobs listing still shows the other gate in_progress, after that gate completed earlier (W3's ~20 s listing lag, 41289450679), leaves it. Its own arm then defers to the green run's sweep. The lag is measured; the window was not measured on live runs. Carry: #3885
- W3's cap stays at `GATE_WAIT_MAX_S`, because the precondition the design names ("once W1 removes every source wait") is not what bounds it: `OWN_PENDING` is this run's own jobs. Re-measure own-pending wait durations after this merge before lowering it. Carry: #3885
- Carry 2 (env_drift baseline cache after a light main push) is measured in commit a036a9ad20, in `dev/programme/carries/carry-3885.json` carry 2's `control` and `brief`. Its null control (a miss forked at a full push whose run did save, plus the hit duration) is still owed there. Carry: #3885

## Friction

none
